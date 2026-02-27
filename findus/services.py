"""
Business logic layer for FindUs application.
Separates complex operations from views for better testing and debugging.
"""
from django.db.models import Q, Avg, Count, Case, When, F, Value, DecimalField, Exists, OuterRef, Subquery
from django.core.paginator import Paginator
from django.core.cache import cache
from django.utils import timezone
import hashlib
import json
import logging

from .models import Service, Review, CraftsmanProfile, BoostRequest

logger = logging.getLogger(__name__)


class ServiceQueryBuilder:
    """Builds optimized service queries with proper select_related and prefetch_related"""
    
    @staticmethod
    def get_base_queryset():
        """Get base service queryset with relations and review stats (Service has no avg_rating/review_count columns)."""
        return (
            Service.objects.select_related(
                'craftsman',
                'craftsman__user_profile',
                'craftsman__user_profile__user',
            )
            .annotate(
                avg_rating=Avg('reviews__rating'),
                review_count=Count('reviews'),
            )
            .only(
                'id', 'title', 'description', 'category', 'region',
                'price_type', 'hourly_rate', 'fixed_price', 'availability',
                'job_size', 'created_at', 'image', 'service_status',
                'features', 'materials_included', 'travel_fee',
                'craftsman__id', 'craftsman__business_name', 'craftsman__rating',
                'craftsman__is_verified', 'craftsman__license_number',
                'craftsman__phone', 'craftsman__profile_photo',
                'craftsman__user_profile__user__username',
                'craftsman__user_profile__user__first_name',
                'craftsman__user_profile__user__last_name',
                'craftsman__user_profile__user__email',
            )
        )
    
    @staticmethod
    def apply_filters(queryset, filters):
        """Apply filters to service queryset
        
        Args:
            queryset: Base queryset to filter
            filters: Dict with filter parameters
            
        Returns:
            Filtered queryset
        """
        # Category filter
        if filters.get('category'):
            queryset = queryset.filter(category=filters['category'])
        
        # Region filter
        if filters.get('region'):
            queryset = queryset.filter(region=filters['region'])
        
        # Search query
        search = filters.get('search', '').strip()
        if search and len(search) >= 2:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(craftsman__business_name__icontains=search)
            )
        
        # Price filters
        price_min = filters.get('price_min')
        price_max = filters.get('price_max')
        
        if price_min or price_max:
            queryset = queryset.annotate(
                effective_price=Case(
                    When(price_type='hourly', then=F('hourly_rate')),
                    When(price_type='fixed', then=F('fixed_price')),
                    default=Value(999999),
                    output_field=DecimalField(),
                )
            )
            
            if price_min:
                try:
                    queryset = queryset.filter(effective_price__gte=float(price_min))
                except (ValueError, TypeError):
                    logger.warning(f"Invalid price_min value: {price_min}")
            
            if price_max:
                try:
                    queryset = queryset.filter(effective_price__lte=float(price_max))
                except (ValueError, TypeError):
                    logger.warning(f"Invalid price_max value: {price_max}")
        
        # Rating filter (using denormalized field)
        rating = filters.get('rating')
        if rating:
            try:
                queryset = queryset.filter(avg_rating__gte=float(rating))
            except (ValueError, TypeError):
                logger.warning(f"Invalid rating value: {rating}")
        
        # Availability filter
        availability = filters.get('availability', [])
        if availability:
            queryset = queryset.filter(availability__in=availability)
        
        # Job size filter
        job_sizes = filters.get('job_sizes', [])
        if job_sizes:
            queryset = queryset.filter(job_size__in=job_sizes)
        
        # Features filter
        features = filters.get('features', [])
        if features:
            for feature in features:
                queryset = queryset.filter(features__contains=[feature])
        
        return queryset
    
    @staticmethod
    def apply_sorting(queryset, sort_by):
        """Apply sorting to queryset"""
        sort_mapping = {
            'relevance': ['-avg_rating', '-created_at'],
            'rating': ['-avg_rating', '-review_count'],
            'newest': ['-created_at'],
            'price_low': ['hourly_rate', 'fixed_price'],
            'price_high': ['-hourly_rate', '-fixed_price'],
        }
        
        order_by = sort_mapping.get(sort_by, ['-avg_rating', '-created_at'])
        return queryset.order_by(*order_by)


class CraftsmanServiceManager:
    """Manages craftsman's services with boost status"""
    
    @staticmethod
    def get_craftsman_services(craftsman_profile, service_filter='all'):
        """Get services for a craftsman with boost annotations (single query, no N+1)."""
        approved_boosts = BoostRequest.objects.filter(
            service=OuterRef('pk'),
            status='approved',
            expires_at__gte=timezone.now(),
        )
        latest_boost = (
            BoostRequest.objects.filter(service=OuterRef('pk'))
            .order_by('-created_at')
            .values('status')[:1]
        )
        services = (
            Service.objects.filter(craftsman=craftsman_profile)
            .annotate(
                is_boosted=Exists(approved_boosts),
                latest_boost_status=Subquery(latest_boost),
            )
            .select_related('craftsman', 'craftsman__user_profile')
        )
        if service_filter == 'active':
            services = services.filter(service_status='Active')
        elif service_filter == 'boosted':
            services = services.filter(is_boosted=True)
        return services.order_by('-created_at')

    @staticmethod
    def get_service_counts(craftsman_profile):
        """Dashboard counts in one aggregate query instead of three."""
        result = Service.objects.filter(craftsman=craftsman_profile).aggregate(
            total=Count('id'),
            active=Count('id', filter=Q(service_status='Active')),
            paused=Count('id', filter=Q(service_status='Paused')),
        )
        return {
            'total': result.get('total') or 0,
            'active': result.get('active') or 0,
            'paused': result.get('paused') or 0,
        }


class CacheManager:
    """Manages Redis caching for views"""
    
    VERSION_KEY_PREFIX = "craftsman_dash_version_"
    
    @staticmethod
    def generate_cache_key(prefix, filters, page=1):
        """Generate consistent cache key from filters"""
        cache_data = {
            'filters': filters,
            'page': page,
        }
        hash_key = hashlib.md5(
            json.dumps(cache_data, sort_keys=True).encode()
        ).hexdigest()
        return f"{prefix}_{hash_key}"
    
    @staticmethod
    def get_cached_context(cache_key):
        """Retrieve cached context"""
        return cache.get(cache_key)
    
    @staticmethod
    def set_cached_context(cache_key, context, timeout=300):
        """Cache context with timeout (default 5 minutes)"""
        cache.set(cache_key, context, timeout)
    
    @staticmethod
    def get_craftsman_dash_version(craftsman_id):
        """Return current cache version for this craftsman's dashboard (so cache keys change on invalidation)."""
        key = f"{CacheManager.VERSION_KEY_PREFIX}{craftsman_id}"
        return cache.get(key, 0)
    
    @staticmethod
    def invalidate_craftsman_dashboard(craftsman_id):
        """Invalidate all dashboard cache for this craftsman (after edit/delete). Works with any cache backend."""
        key = f"{CacheManager.VERSION_KEY_PREFIX}{craftsman_id}"
        version = cache.get(key, 0)
        cache.set(key, version + 1, timeout=86400 * 7)  # 1 week so version doesn't expire
        # Optional: try Redis-style delete_pattern for backends that support it (e.g. django-redis)
        try:
            if hasattr(cache, 'delete_pattern'):
                cache.delete_pattern(f"craftsman_dash_{craftsman_id}_*")
        except Exception:
            pass


def delete_service_safe(service, user):
    """Safely delete a service with permission check
    
    Args:
        service: Service instance
        user: User attempting deletion
        
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        # Permission check
        if service.craftsman.user_profile.user != user:
            logger.warning(
                f"Unauthorized delete attempt: User {user.id} tried to delete "
                f"service {service.id} owned by {service.craftsman.user_profile.user.id}"
            )
            return False, "You don't have permission to delete this service"
        
        # Store info for logging and cache invalidation (before delete)
        service_id = service.id
        service_title = service.title
        craftsman_id = service.craftsman_id
        
        # Delete the service
        service.delete()
        
        logger.info(
            f"Service deleted: ID={service_id}, Title='{service_title}', "
            f"User={user.id}"
        )
        
        # Clear related caches
        cache.delete(f"service_detail_{service_id}")
        CacheManager.invalidate_craftsman_dashboard(craftsman_id)
        
        return True, "Service deleted successfully"
        
    except Exception as e:
        logger.error(
            f"Error deleting service {service.id}: {str(e)}", 
            exc_info=True
        )
        return False, f"Error deleting service: {str(e)}"