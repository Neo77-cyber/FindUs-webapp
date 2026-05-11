"""
Public views (accessible without login)
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.utils import timezone
import logging

from ..models import (
    Service,
    WaitingList,
    CraftsmanProfile,
    AVAILABILITY_CHOICES,
    SERVICE_SCOPE_CHOICES,
    REGION_CHOICES,
    CATEGORY_CHOICES,
)
from ..services import ServiceQueryBuilder, CacheManager
from ..email_utils import send_waitlist_email_async

logger = logging.getLogger(__name__)


def home(request):
    """Public home page with service listings"""
    is_htmx = request.headers.get("HX-Request") == "true"

    # Redirect authenticated users to their dashboards
    if not is_htmx and request.user.is_authenticated:
        if hasattr(request.user, "userprofile"):
            try:
                request.user.userprofile.craftsmanprofile
                return redirect("craftsman_dashboard")
            except:
                return redirect("customer_dashboard")

    try:
        # Extract filters
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

        # Check if filters are active
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

        # Try cache (skip for HTMX)
        cache_key = CacheManager.generate_cache_key(
            "home_results", {**filters, "sort": sort_by}, page
        )

        if not is_htmx:
            cached_context = CacheManager.get_cached_context(cache_key)
            if cached_context:
                cached_context.update(
                    {
                        **filters,
                        "filters_active": filters_active,
                        "sort_by": sort_by,
                        "AVAILABILITY_CHOICES": AVAILABILITY_CHOICES,
                        "SERVICE_SCOPE_CHOICES": SERVICE_SCOPE_CHOICES,
                        "REGION_CHOICES": REGION_CHOICES,
                        "CATEGORY_CHOICES": CATEGORY_CHOICES,
                    }
                )
                return render(request, "home.html", cached_context)

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
        if not is_htmx and paginator.count > 0:
            CacheManager.set_cached_context(cache_key, context, 300)

            # Also cache default page
            if not filters_active and page == 1:
                CacheManager.set_cached_context("home_page_default", context, 300)

        # HTMX response
        if is_htmx:
            return render(request, "partials/filtered_results.html", context)

        return render(request, "home.html", context)

    except Exception as e:
        logger.error(f"Home view error: {e}", exc_info=True)

        context = {
            "Service": Service,
            "filters_active": False,
            "results_count": 0,
            "has_services": False,
            "show_alert": "We're working on fixing this issue. Please try again later.",
            "AVAILABILITY_CHOICES": AVAILABILITY_CHOICES,
            "SERVICE_SCOPE_CHOICES": SERVICE_SCOPE_CHOICES,
            "REGION_CHOICES": REGION_CHOICES,
            "CATEGORY_CHOICES": CATEGORY_CHOICES,
        }
        return render(request, "home.html", context)


def add_to_waiting_list(request):
    """Add user to waiting list"""
    if request.method != "POST":
        return redirect("home")

    try:
        logger.info(f"Form data: {dict(request.POST)}")

        name = request.POST.get("fullname")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        service_needed = request.POST.get("service")
        location = request.POST.get("location")
        notes = request.POST.get("notes")

        waiting_list_entry = WaitingList.objects.create(
            name=name,
            email=email,
            phone=phone,
            service_needed=service_needed,
            location=location,
            notes=notes,
        )

        logger.info(
            f"Created: {waiting_list_entry.name} - {waiting_list_entry.service_needed}"
        )

        # Send email asynchronously
        send_waitlist_email_async(email, name, location, service_needed)

        if request.headers.get("HX-Request"):
            return HttpResponse(
                "Success! We'll notify you when professionals are available."
            )
        else:
            messages.success(
                request, "Success! We'll notify you when professionals are available."
            )
            return redirect(request.META.get("HTTP_REFERER", "home"))

    except Exception as e:
        logger.error(f"Error: {str(e)}")

        if request.headers.get("HX-Request"):
            return HttpResponse(f"Error: {str(e)}", status=400)
        else:
            messages.error(request, f"Error: {str(e)}")
            return redirect(request.META.get("HTTP_REFERER", "home"))


def craftsman_public_profile(request, craftsman_slug):
    """Public craftsman profile"""

    craftsman = get_object_or_404(
        CraftsmanProfile.objects.select_related("user_profile__user"),
        slug=craftsman_slug,
    )

    services = (
        Service.objects.filter(craftsman=craftsman, service_status="Active")
        .select_related("craftsman__user_profile__user")
        .order_by("-created_at")
    )

    # Check boost status for each service
    from ..selectors import check_active_boost

    for service in services:
        service.is_boosted = check_active_boost(service)

    context = {
        "craftsman": craftsman,
        "services": services,
        "total_services": services.count(),
    }

    return render(request, "craftsman_public_profile.html", context)


def offline_page(request):
    """Offline page for PWA"""
    return render(request, "offline.html")
