"""
Customer-specific views
"""

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.core.paginator import Paginator
import logging

from ..models import (
    Service,
    Review,
    CustomerProfile,
    AVAILABILITY_CHOICES,
    SERVICE_SCOPE_CHOICES,
    REGION_CHOICES,
    CATEGORY_CHOICES,
)
from ..services import ServiceQueryBuilder, CacheManager
from ..selectors import get_service_by_id
from ..forms import ReviewForm

logger = logging.getLogger(__name__)


def invalidate_service_cache(service_slug):
    """Clear service detail cache"""
    cache_key = f"service_detail_{service_slug}"
    try:
        CacheManager.set_cached_context(cache_key, None, 1)
    except:
        pass


@login_required(login_url="home")
def customer_dashboard(request):
    """Customer dashboard with service browsing"""
    is_htmx = request.headers.get("HX-Request") == "true"

    try:
        # Extract filters from request
        filters = {
            "category": request.GET.get("category", "").strip(),
            "region": request.GET.get("region", "").strip(),
            "search": request.GET.get("search", "").strip(),
            "price_min": request.GET.get("price_min", "").strip(),
            "price_max": request.GET.get("price_max", "").strip(),
            "rating": request.GET.get("rating", "").strip(),
            "availability": request.GET.getlist("availability", []),
            "features": request.GET.getlist("features", []),
            "job_sizes": request.GET.getlist("job_size", []),
        }
        sort_by = request.GET.get("sort", "relevance").strip()
        page = request.GET.get("page", 1)

        # Check if any filters are active
        filters_active = any(
            [
                filters["category"],
                filters["region"],
                filters["search"] and len(filters["search"]) >= 2,
                filters["price_min"],
                filters["price_max"],
                filters["rating"],
                filters["availability"],
                filters["job_sizes"],
                filters["features"],
                sort_by != "relevance",
            ]
        )

        # Try cache (skip for HTMX to keep real-time)
        cache_key = CacheManager.generate_cache_key(
            "customer_dash", {**filters, "sort": sort_by}, page
        )

        if not is_htmx:
            cached_context = CacheManager.get_cached_context(cache_key)
            if cached_context:
                # Update dynamic values
                cached_context.update(
                    {
                        **filters,
                        "filters_active": filters_active,
                        "sort_by": sort_by,
                    }
                )

                template = (
                    "partials/dashboard_results.html"
                    if is_htmx
                    else "customer_dashboard.html"
                )
                return render(request, template, cached_context)

        # Build query
        services = ServiceQueryBuilder.get_base_queryset()
        services = services.filter(service_status="Active")

        # Apply filters
        services = ServiceQueryBuilder.apply_filters(services, filters)

        # Apply sorting
        services = ServiceQueryBuilder.apply_sorting(services, sort_by)

        # Paginate
        paginator = Paginator(services, 12)
        page_obj = paginator.get_page(page)

        # Build context
        context = {
            "Service": Service,
            "page_obj": page_obj,
            "services": page_obj,
            "results_count": paginator.count,
            "has_services": paginator.count > 0,
            **{f"selected_{k}": v for k, v in filters.items()},
            "filters_active": filters_active,
            "sort_by": sort_by,
            "AVAILABILITY_CHOICES": AVAILABILITY_CHOICES,
            "SERVICE_SCOPE_CHOICES": SERVICE_SCOPE_CHOICES,
            "REGION_CHOICES": REGION_CHOICES,
            "CATEGORY_CHOICES": CATEGORY_CHOICES,
        }

        # Cache for 5 minutes
        if paginator.count > 0:
            CacheManager.set_cached_context(cache_key, context, 300)

        # HTMX response
        template = (
            "partials/dashboard_results.html" if is_htmx else "customer_dashboard.html"
        )
        return render(request, template, context)

    except Exception as e:
        logger.error(f"Customer dashboard error: {e}", exc_info=True)

        context = {
            "Service": Service,
            "filters_active": False,
            "results_count": 0,
            "has_services": False,
            "show_alert": "We're experiencing technical difficulties. Please try again later.",
            "AVAILABILITY_CHOICES": AVAILABILITY_CHOICES,
            "SERVICE_SCOPE_CHOICES": SERVICE_SCOPE_CHOICES,
            "REGION_CHOICES": REGION_CHOICES,
            "CATEGORY_CHOICES": CATEGORY_CHOICES,
        }

        template = (
            "partials/dashboard_results.html" if is_htmx else "customer_dashboard.html"
        )
        return render(request, template, context)


def service_detail(request, service_slug):
    """Service detail page with reviews"""

    # Try cache first, but skip if we just submitted a review (success message present)
    cache_key = f"service_detail_{service_slug}"
    cached_context = CacheManager.get_cached_context(cache_key)

    # Only use cache if we have valid cached data and no fresh success message
    if (
        cached_context
        and cached_context.get("service")
        and not messages.get_messages(request)
    ):
        return render(request, "service_detail.html", cached_context)

    try:
        # Get service with reviews
        from django.db.models import Avg, Count

        service = Service.objects.annotate(
            review_count=Count("reviews", distinct=True),
            avg_rating=Avg("reviews__rating"),
        ).get(slug=service_slug)

        # Get reviews (limit 10)
        reviews = service.reviews.select_related(
            "customer__user_profile__user"
        ).order_by("-created_at")[:10]

        context = {
            "service": service,
            "craftsman": service.craftsman,
            "reviews": reviews,
            "reviews_count": service.review_count,
            "avg_rating": service.avg_rating,
        }

        # Cache for 1 hour
        CacheManager.set_cached_context(cache_key, context, 3600)

        return render(request, "service_detail.html", context)

    except Exception as e:
        logger.error(f"Service detail error: {e}", exc_info=True)
        return render(
            request,
            "service_detail.html",
            {
                "error": "Service not found",
                "service": None,
            },
        )


@login_required(login_url="home")
def customer_profile(request):
    """Customer profile page"""
    user = request.user

    try:
        customer_profile = user.userprofile.customerprofile
    except:
        customer_profile = CustomerProfile.objects.create(user_profile=user.userprofile)

    if request.method == "POST":
        user.first_name = request.POST.get("first_name")
        user.last_name = request.POST.get("last_name")
        user.email = request.POST.get("email")
        user.save()

        user.userprofile.phone = request.POST.get("phone")
        user.userprofile.save()

        messages.success(request, "Profile updated successfully")
        return redirect("customer_profile")

    context = {
        "user": user,
        "profile": user.userprofile,
    }
    return render(request, "customer_profile.html", context)


@login_required(login_url="home")
def saved_services(request):
    """View saved services"""
    try:
        customer_profile = request.user.userprofile.customerprofile
        saved_services = customer_profile.saved_services.all()
        saved_count = saved_services.count()
    except:
        saved_services = []
        saved_count = 0

    context = {
        "saved_services": saved_services,
        "saved_count": saved_count,
    }
    return render(request, "saved_services.html", context)


@login_required
def save_service(request, service_slug):
    """Toggle save/unsave a service"""

    service = get_object_or_404(Service, slug=service_slug)

    try:
        customer_profile = request.user.userprofile.customerprofile

        # Check current status
        is_saved = customer_profile.saved_services.filter(slug=service_slug).exists()

        # Toggle
        if is_saved:
            customer_profile.saved_services.remove(service)
            is_saved = False
        else:
            customer_profile.saved_services.add(service)
            is_saved = True

        # Return updated button
        return render(
            request,
            "partials/save_button.html",
            {"service": service, "is_saved": is_saved},
        )

    except (AttributeError, CustomerProfile.DoesNotExist):
        return render(
            request,
            "partials/save_button.html",
            {
                "service": service,
                "is_saved": False,
                "error": "Only customers can save services",
            },
        )


@login_required
def submit_review(request, service_slug):
    """Submit a review for a service"""

    if request.method != "POST":
        return redirect("service_detail", service_slug=service_slug)

    service = get_object_or_404(Service, slug=service_slug)

    try:
        customer_profile = request.user.userprofile.customerprofile
    except:
        customer_profile = CustomerProfile.objects.create(
            user_profile=request.user.userprofile
        )

    # Check if already reviewed
    if Review.objects.filter(service=service, customer=customer_profile).exists():
        return redirect("service_detail", service_slug=service_slug)

    # Create review
    rating = request.POST.get("rating")
    try:
        rating = int(rating) if rating else 0
    except ValueError:
        rating = 0

    Review.objects.create(
        service=service,
        customer=customer_profile,
        rating=rating,
        title=request.POST.get("title", ""),
        comment=request.POST.get("comment", ""),
    )

    # Clear service detail cache properly
    cache_key = f"service_detail_{service_slug}"
    CacheManager.set_cached_context(
        cache_key, None, 1
    )  # Clear by setting None with short expiry

    return redirect("service_detail", service_slug=service_slug)


# Add this to findus/views/customer_views.py


@login_required
def create_review(request, service_slug):
    """Display review form modal"""
    service = get_object_or_404(Service, slug=service_slug)
    form = ReviewForm()

    context = {"service": service, "form": form}
    return render(request, "partials/review_form.html", context)
