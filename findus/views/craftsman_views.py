"""
Craftsman-specific views
"""
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.core.paginator import Paginator
import logging
import os
from ..models import Service, BoostRequest, CATEGORY_CHOICES, REGION_CHOICES, AVAILABILITY_CHOICES
from ..services import (
    CraftsmanServiceManager, 
    CacheManager,
    delete_service_safe
)
from ..selectors import get_craftsman_profile, get_service_by_id, check_pending_boost


logger = logging.getLogger(__name__)


@login_required(login_url="home")
def craftsman_dashboard(request):
    """Craftsman dashboard with services grid"""
    
    # Get craftsman profile
    craftsman_profile = get_craftsman_profile(request.user)
    if not craftsman_profile:
        
        return redirect("craftsman_dashboard")
    
    try:
        # Get filters
        service_filter = request.GET.get('service-filter', 'all')
        page_number = request.GET.get('page', 1)
        is_htmx = request.headers.get("HX-Request") == "true"
        
        # Always load fresh from DB (no cache) so admin changes, reassigns, and
        # multi-process / LocMemCache never show stale data.
        services_qs = CraftsmanServiceManager.get_craftsman_services(
            craftsman_profile, 
            service_filter
        )
        
        
        # Get counts
        counts = CraftsmanServiceManager.get_service_counts(craftsman_profile)
        
        # Paginate
        paginator = Paginator(services_qs, 8)
        services = paginator.get_page(page_number)
        
        # Build context
        context = {
            'craftsman': craftsman_profile,
            'services': services,
            'total_services': counts['total'],
            'has_services': counts['total'] > 0,
            'active_count': counts['active'],
            'paused_count': counts['paused'],
            'CATEGORY_CHOICES': CATEGORY_CHOICES,
            'REGION_CHOICES': REGION_CHOICES,
            'AVAILABILITY_CHOICES': AVAILABILITY_CHOICES,
            'current_filter': service_filter,
        }
        
        # HTMX response
        if is_htmx:
            return render(request, "partials/service_grid.html", context)
        
        return render(request, "craftsman_dasboard.html", context)
        
    except Exception as e:
        logger.error(f"Error in craftsman_dashboard: {e}", exc_info=True)
        return render(request, "craftsman_dasboard.html", {
            'has_services': False,
            'error': 'Unable to load dashboard. Please try again.'
        })


@login_required
def delete_service(request):
    """Delete a service with proper permission checks"""
    
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'error': 'Invalid request method'
        }, status=405)
    
    try:
        service_id = request.POST.get('service_id')
        
        if not service_id:
            return JsonResponse({
                'success': False,
                'error': 'Service ID is required'
            }, status=400)
        
        # Get service
        service = get_service_by_id(service_id)
        
        # Delete with permission check
        success, message = delete_service_safe(service, request.user)
        
        if success:
            # AJAX response
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': message
                })
            
            # Regular response
            messages.success(request, message)
            return redirect('craftsman_dashboard')
        else:
            # Failed
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': message
                }, status=403)
            
            messages.error(request, message)
            return redirect('craftsman_dashboard')
            
    except Exception as e:
        logger.error(f"Error in delete_service: {e}", exc_info=True)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'error': 'An unexpected error occurred'
            }, status=500)
        
        messages.error(request, 'An unexpected error occurred')
        return redirect('craftsman_dashboard')
    
# Add these to the END of findus/views/craftsman_views.py

@login_required
def edit_service(request):
    """Edit service details"""
    
    if request.method == 'POST':
        try:
            service_id = request.POST.get('service_id')
            service = get_object_or_404(Service, id=service_id)
            
            # Permission check
            if service.craftsman.user_profile.user != request.user:
                return JsonResponse({
                    'success': False,
                    'error': 'You do not have permission to edit this service'
                }, status=403)
            
            # Update fields
            service.title = request.POST.get('title', '').strip()
            service.category = request.POST.get('category', '')
            service.description = request.POST.get('description', '').strip()
            service.price_type = request.POST.get('price_type') or 'fixed'
            
            # Handle pricing (empty string -> None for DecimalField)
            if service.price_type == 'hourly':
                raw_hourly = request.POST.get('hourly_rate')
                service.hourly_rate = raw_hourly if raw_hourly and raw_hourly.strip() else None
                service.fixed_price = None
            else:
                raw_fixed = request.POST.get('fixed_price')
                service.fixed_price = raw_fixed if raw_fixed and raw_fixed.strip() else None
                service.hourly_rate = None
            
            # Update other fields
            service.region = (request.POST.get('region') or '').strip()
            service.availability = request.POST.get('availability') or 'immediate'
            service.save()
            
            # Invalidate dashboard cache so updated service shows on next load
            CacheManager.invalidate_craftsman_dashboard(service.craftsman_id)
            
            logger.info(f"Service updated: {service.id} by {request.user.username}")
            
            return JsonResponse({
                'success': True,
                'message': 'Service updated successfully',
                'service': {
                    'id': service.id,
                    'title': service.title,
                    'category': service.get_category_display(),
                    'description': service.description,
                }
            })
            
        except Exception as e:
            logger.error(f"Error editing service: {e}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    # GET request - return service data
    if request.method == 'GET':
        try:
            service_id = request.GET.get('service_id')
            service = get_object_or_404(Service, id=service_id)
            
            # Permission check
            if service.craftsman.user_profile.user != request.user:
                return JsonResponse({
                    'success': False,
                    'error': 'You do not have permission to view this service'
                }, status=403)
            
            return JsonResponse({
                'success': True,
                'service': {
                    'id': service.id,
                    'title': service.title,
                    'category': service.category,
                    'description': service.description,
                    'price_type': service.price_type,
                    'hourly_rate': str(service.hourly_rate) if service.hourly_rate else '',
                    'fixed_price': str(service.fixed_price) if service.fixed_price else '',
                    'region': service.region,
                    'availability': service.availability
                }
            })
            
        except Exception as e:
            logger.error(f"Error fetching service: {e}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method'
    }, status=400)


@login_required
def check_boost_status(request, service_id):
    """Check if service has pending boost request"""
    
    try:
        service = get_service_by_id(service_id)
        
        # Check for pending boost
        has_pending_boost = check_pending_boost(service)
        
        return JsonResponse({
            'has_pending_boost': has_pending_boost,
            'service_id': service_id
        })
        
    except Exception as e:
        logger.error(f"Error checking boost status: {e}", exc_info=True)
        return JsonResponse({
            'has_pending_boost': False,
            'error': str(e)
        })


@login_required
def boost_service(request):
    """Submit boost request for a service"""
    
    if request.method != "POST":
        return JsonResponse({
            'success': False,
            'error': 'Invalid request method'
        }, status=400)
    
    try:
        from datetime import datetime, timedelta
        from ..models import BoostRequest
        
        service_id = request.POST.get("service_id")
        service = get_service_by_id(service_id)
        
        # Permission check
        if service.craftsman.user_profile.user != request.user:
            return JsonResponse({
                'success': False,
                'error': 'You do not have permission to boost this service'
            }, status=403)
        
        # Check for existing pending boost
        if check_pending_boost(service):
            return JsonResponse({
                'success': False,
                'error': 'You already have a pending boost request for this service'
            }, status=400)
        
        # Get payment proof
        payment_proof = request.FILES.get("payment_proof")
        if not payment_proof:
            return JsonResponse({
                'success': False,
                'error': 'Please upload payment proof'
            }, status=400)
        
        # Validate file
        allowed_extensions = [".jpg", ".jpeg", ".png", ".pdf"]
        file_extension = os.path.splitext(payment_proof.name)[1].lower()
        
        if file_extension not in allowed_extensions:
            return JsonResponse({
                'success': False,
                'error': 'Invalid file type. Please upload JPG, PNG, or PDF'
            }, status=400)
        
        if payment_proof.size > 5 * 1024 * 1024:  # 5MB
            return JsonResponse({
                'success': False,
                'error': 'File size must be less than 5MB'
            }, status=400)
        
        # Get boost parameters
        boost_duration = int(request.POST.get("boost_duration", 7))
        price_map = {7: 15, 14: 25, 30: 40}
        price = price_map.get(boost_duration, 15)
        expiry_date = datetime.now() + timedelta(days=boost_duration)
        
        # Create boost request
        boost_request = BoostRequest.objects.create(
            service=service,
            user=request.user,
            price=price,
            duration_days=boost_duration,
            payment_proof=payment_proof,
            notes=request.POST.get("notes", ""),
            status="pending",
            expires_at=expiry_date,
        )
        
        logger.info(f"Boost request created: {boost_request.id} for service {service.id}")
        
        return JsonResponse({
            'success': True,
            'message': f'Boost request submitted! Your service will be boosted for {boost_duration} days once payment is verified.'
        })
        
    except Exception as e:
        logger.error(f"Error in boost_service: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': f'Error: {str(e)}'
        }, status=500)


@login_required(login_url="home")
def craftsman_profile(request):
    """Craftsman profile management (uses preloaded profile to avoid extra queries)."""
    craftsman_profile = get_craftsman_profile(request.user)
    if not craftsman_profile:
        messages.error(request, "You need to complete provider onboarding first")
        return redirect("craftsman_dashboard")

    user_profile = craftsman_profile.user_profile  # already loaded via select_related

    if request.method == "POST":
        request.user.first_name = request.POST.get("first_name")
        request.user.last_name = request.POST.get("last_name")
        request.user.email = request.POST.get("email")
        request.user.save()

        user_profile.phone = request.POST.get("phone")
        user_profile.save()

        # Update craftsman profile
        craftsman_profile.business_name = request.POST.get("business_name")
        craftsman_profile.years_of_experience = request.POST.get("years_of_experience")
        craftsman_profile.license_number = request.POST.get("license_number")
        craftsman_profile.has_license = bool(request.POST.get("license_number"))
        craftsman_profile.phone = request.POST.get("phone")

        # Handle profile photo upload
        if "profile_photo" in request.FILES:
            craftsman_profile.profile_photo = request.FILES["profile_photo"]

        craftsman_profile.save()
        
        logger.info(f"Craftsman profile updated: {craftsman_profile.id}")
        messages.success(request, "Profile updated successfully")
        return redirect("craftsman_profile")

    context = {
        "user": request.user,
        "profile": user_profile,
        "craftsman": craftsman_profile,
    }
    return render(request, "craftsman_profile.html", context)