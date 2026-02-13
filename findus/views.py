import logging
import os
from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.paginator import EmptyPage, Page, PageNotAnInteger, Paginator
from django.db import DatabaseError, IntegrityError
from django.db.models import Avg, Count, Q, Value
from django.db.models.functions import Coalesce
from django.http import HttpResponse
from findus.models import AVAILABILITY_CHOICES, SERVICE_SCOPE_CHOICES, CATEGORY_CHOICES, REGION_CHOICES
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods

from .email_utils import *
from .forms import *
from .models import *

from django import forms
from formtools.wizard.views import SessionWizardView
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os
from django.shortcuts import redirect
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from django.db.models import Case, When, F, Value, DecimalField, IntegerField
from django.db.models.functions import Coalesce
from decimal import Decimal
from django.core.cache import cache
import hashlib
import json
from django.db.models import Prefetch  # Add this line


WIZARD_TEMP_DIR = os.path.join(settings.MEDIA_ROOT, 'wizard_temp')
os.makedirs(WIZARD_TEMP_DIR, exist_ok=True)
temp_storage = FileSystemStorage(location=WIZARD_TEMP_DIR)



logger = logging.getLogger(__name__)



def home(request):
    is_htmx = request.headers.get("HX-Request") == "true"

    if not is_htmx and request.user.is_authenticated:
        if hasattr(request.user, "userprofile"):
            try:
                request.user.userprofile.craftsmanprofile
                return redirect("craftsman_dashboard")
            except:
                return redirect("customer_dashboard")

    try:
        # Get filter parameters
        category_filter = request.GET.get("category", "").strip()
        region_filter = request.GET.get("region", "").strip()
        search_query = request.GET.get("search", "").strip()
        price_min = request.GET.get("price_min", "").strip()
        price_max = request.GET.get("price_max", "").strip()
        rating = request.GET.get("rating", "").strip()
        availability = request.GET.getlist("availability", [])
        features = request.GET.getlist("features", [])
        job_sizes = request.GET.getlist("job_size", [])
        sort_by = request.GET.get("sort", "relevance").strip()

        # Check if filters are active
        filters_active = any(
            [
                category_filter,
                region_filter,
                search_query and len(search_query) >= 2,
                price_min,
                price_max,
                rating,
                availability,
                job_sizes,
                features,
                sort_by != "relevance",
            ]
        )

        # ============== REDIS CACHING ==============
        from django.core.cache import cache
        import hashlib
        import json
        
        # Create a unique cache key based on all filters and page
        cache_data = {
            'category': category_filter,
            'region': region_filter,
            'search': search_query,
            'price_min': price_min,
            'price_max': price_max,
            'rating': rating,
            'availability': sorted(availability),
            'features': sorted(features),
            'job_sizes': sorted(job_sizes),
            'sort': sort_by,
            'page': request.GET.get("page", "1"),
        }
        
        # Create MD5 hash of the cache data for a clean key
        cache_key = f"home_results_{hashlib.md5(json.dumps(cache_data, sort_keys=True).encode()).hexdigest()}"
        
        # Try to get from Redis cache first (skip for HTMX requests to keep real-time)
        if not is_htmx:
            cached_result = cache.get(cache_key)
            if cached_result:
                # Update the cached context with current filter values
                cached_result.update({
                    "selected_category": category_filter,
                    "selected_region": region_filter,
                    "search_query": search_query,
                    "filters_active": filters_active,
                    "price_min": price_min,
                    "price_max": price_max,
                    "rating": rating,
                    "availability": availability,
                    "job_sizes": job_sizes,
                    "features": features,
                    "sort_by": sort_by,
                    "AVAILABILITY_CHOICES": AVAILABILITY_CHOICES,
                    "SERVICE_SCOPE_CHOICES": SERVICE_SCOPE_CHOICES,
                    "REGION_CHOICES": REGION_CHOICES,
                    "CATEGORY_CHOICES": CATEGORY_CHOICES,
                })
                return render(request, "home.html", cached_result)

        # ============== FIXED QUERY WITH ALL NEEDED FIELDS ==============
        # Use select_related and prefetch_related to prevent N+1 queries
        base_services = (
            Service.objects
            .select_related(
                'craftsman',
                'craftsman__user_profile',
                'craftsman__user_profile__user'
            )
            .prefetch_related(
                Prefetch('reviews', queryset=Review.objects.only('rating', 'created_at'))
            )
            .only(
                'id', 'title', 'description', 'category', 'region',
                'price_type', 'hourly_rate', 'fixed_price', 'availability',
                'job_size', 'created_at', 'craftsman_id', 'image',
                'service_status', 'features', 'materials_included',
                # Craftsman fields needed in template
                'craftsman__id',
                'craftsman__business_name',
                'craftsman__rating',
                'craftsman__is_verified',
                'craftsman__license_number',
                'craftsman__phone',  # ← CRITICAL: for the call button
                'craftsman__profile_photo',  # ← CRITICAL: for the avatar
                'craftsman__user_profile__user__username',
                'craftsman__user_profile__user__first_name',
                'craftsman__user_profile__user__last_name'
            )
            .filter(service_status="Active")
        )

        # Apply filters efficiently
        if category_filter:
            base_services = base_services.filter(category=category_filter)

        if region_filter:
            base_services = base_services.filter(region=region_filter)

        if search_query and len(search_query) >= 2:
            base_services = base_services.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(craftsman__business_name__icontains=search_query)
            )

        # Price filtering - optimize with Case/When
        if price_min or price_max:
            base_services = base_services.annotate(
                effective_price=Case(
                    When(price_type="hourly", then=F("hourly_rate")),
                    When(price_type="fixed", then=F("fixed_price")),
                    default=Value(999999),
                    output_field=DecimalField(),
                )
            )
            if price_min:
                try:
                    price_min_val = float(price_min)
                    if price_min_val >= 0:
                        base_services = base_services.filter(effective_price__gte=price_min_val)
                except:
                    pass
            if price_max:
                try:
                    price_max_val = float(price_max)
                    if price_max_val >= 0:
                        base_services = base_services.filter(effective_price__lte=price_max_val)
                except:
                    pass

        # Rating filter
        if rating:
            try:
                rating_val = float(rating)
                if 0 <= rating_val <= 5:
                    base_services = base_services.filter(craftsman__rating__gte=rating_val)
            except:
                pass

        # Array/List filters
        if availability:
            base_services = base_services.filter(availability__in=availability)

        if job_sizes:
            base_services = base_services.filter(job_size__in=job_sizes)

        if features:
            for feature in features:
                base_services = base_services.filter(features__contains=[feature])

        # Annotate with aggregates (now with prefetched reviews)
        services = base_services.annotate(
            avg_rating=Coalesce(
                Avg('reviews__rating'), 
                Value(0.0), 
                output_field=models.FloatField()
            ),
            review_count=Count('reviews', distinct=True)
        )

        # Apply sorting
        services = apply_service_sorting(services, sort_by)
        
        if not services.ordered:
            services = services.order_by("-craftsman__rating", "-created_at")

        # ============== FORCE QUERY EXECUTION ==============
        # Convert to list to force evaluation and cache all data
        service_list = list(services)
        
        # ============== FIXED PAGINATION ==============
        from django.core.paginator import Paginator
        paginator = Paginator(service_list, 12)
        page = request.GET.get('page', 1)
        page_obj = paginator.get_page(page)

        # Build context
        context = {
            "Service": Service,
            "page_obj": page_obj,
            "services": page_obj,
            "results_count": len(service_list),
            "has_services": len(service_list) > 0,
            "selected_category": category_filter,
            "selected_region": region_filter,
            "search_query": search_query,
            "filters_active": filters_active,
            "price_min": price_min,
            "price_max": price_max,
            "rating": rating,
            "availability": availability,
            "job_sizes": job_sizes,
            "features": features,
            "sort_by": sort_by,
            "AVAILABILITY_CHOICES": AVAILABILITY_CHOICES,
            "SERVICE_SCOPE_CHOICES": SERVICE_SCOPE_CHOICES,
            "REGION_CHOICES": REGION_CHOICES,
            "CATEGORY_CHOICES": CATEGORY_CHOICES,
        }
        
        # ============== STORE IN REDIS CACHE ==============
        if not is_htmx:
            # Store in Redis for 5 minutes (300 seconds)
            cache.set(cache_key, context, 300)
            
            # Also store commonly accessed pages without filters
            if not filters_active and page == 1:
                cache.set('home_page_default', context, 300)

        # HTMX response
        if is_htmx:
            return render(request, "partials/filtered_results.html", context)

        return render(request, "home.html", context)

    except Exception as e:
        logger.error(f"Home view error: {e}")
        import traceback
        traceback.print_exc()
        context = {
            "Service": Service,
            "filters_active": False,
            "results_count": 0,
            "has_services": False,
            "show_alert": "We're working on fixing this issue. Please try again later.",
        }
        return render(request, "home.html", context)


def apply_service_sorting(queryset, sort_by):
    """Apply sorting to service queryset"""
    if sort_by == "rating":
        return queryset.order_by("-avg_rating", "-review_count")
    elif sort_by == "price_low":
        return queryset.annotate(
            effective_price=Case(
                When(price_type="hourly", then=F("hourly_rate")),
                When(price_type="fixed", then=F("fixed_price")),
                default=Value(0),
                output_field=DecimalField(),
            )
        ).order_by("effective_price")
    elif sort_by == "price_high":
        return queryset.annotate(
            effective_price=Case(
                When(price_type="hourly", then=F("hourly_rate")),
                When(price_type="fixed", then=F("fixed_price")),
                default=Value(0),
                output_field=DecimalField(),
            )
        ).order_by("-effective_price")
    elif sort_by == "newest":
        return queryset.order_by("-created_at")
    else:  # relevance
        return queryset.order_by("-craftsman__rating", "-created_at")


def add_to_waiting_list(request):
    if request.method == "POST":
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

            
            send_waitlist_email_async(email, name, location, service_needed)

            if request.headers.get("HX-Request"):
                return HttpResponse("Success! We'll notify you when professionals are available.")
            else:
                messages.success(request, "Success! We'll notify you when professionals are available.")
                return redirect(request.META.get("HTTP_REFERER", "home"))

        except Exception as e:
            logger.error(f"Error: {str(e)}")

            if request.headers.get("HX-Request"):
                return HttpResponse(f"Error: {str(e)}", status=400)
            else:
                messages.error(request, f"Error: {str(e)}")
                return redirect(request.META.get("HTTP_REFERER", "home"))

    return redirect("home")


###############AUTHETHICATION##################
@csrf_protect
def register(request):

    if request.user.is_authenticated:
        if hasattr(request.user, "userprofile"):
            try:
                request.user.userprofile.craftsmanprofile
                logger.debug(
                    f"Authenticated craftsman redirected to dashboard: {request.user.username}"
                )
                return redirect("craftsman_dashboard")
            except Exception as e:
                logger.debug(
                    f"Authenticated customer redirected to dashboard: {request.user.username}"
                )
                return redirect("customer_dashboard")

    if request.method == "POST":

        form = CustomerSignUpForm(request.POST)

        if form.is_valid():
            try:
                user = form.save()

                login(request, user)

                if user.email:
                    send_welcome_email_async(
                        user_email=user.email,
                        is_craftsman=False,
                    )

                return redirect("customer_dashboard")

            except ValidationError as e:

                logger.warning(
                    f"Validation error during customer registration: {str(e)} - Username attempt: {form.data.get('username', 'N/A')}"
                )
                messages.error(request, f" {str(e)}")

            except IntegrityError as e:

                logger.error(f"Integrity error during customer registration: {str(e)}")
                messages.error(
                    request,
                    "This email or username is already registered. Please use different credentials.",
                )

            except DatabaseError as e:

                logger.error(f"Database error during customer registration: {str(e)}")
                messages.error(
                    request,
                    "database error occurred. Please try again or contact support.",
                )

            except Exception as e:

                logger.error(
                    f"Unexpected error during customer registration: {str(e)}",
                    exc_info=True,
                )
                messages.error(
                    request, "An unexpected error occurred. Please try again later."
                )
        else:

            logger.warning(f"Form validation failed - Errors: {form.errors}")

            field_errors = 0
            non_field_errors = 0

            for field, errors in form.errors.items():
                if field == "__all__":
                    non_field_errors += len(errors)
                    for error in errors:
                        messages.error(request, f"{error}")
                else:
                    field_errors += len(errors)
                    field_name = field.replace("_", " ").title()
                    for error in errors:
                        messages.error(request, f" {field_name}: {error}")

            logger.debug(
                f"Form errors summary - Field errors: {field_errors}, Non-field errors: {non_field_errors}"
            )

            if field_errors + non_field_errors > 0 and not messages.get_messages(
                request
            ):
                messages.error(request, "Please correct the errors below.")
    else:
        form = CustomerSignUpForm()

    return render(request, "register.html", {"form": form})


@csrf_protect
def register_craftsman(request):

    if request.user.is_authenticated:
        if hasattr(request.user, "userprofile"):
            try:
                if hasattr(request.user.userprofile, "craftsmanprofile"):
                    messages.info(request, "You're already registered as a craftsman.")
                    return redirect("craftsman_dashboard")
            except Exception as e:
                logger.debug(f"Profile check error: {str(e)}")
        return redirect("customer_dashboard")

    if request.method == "POST":
        form = CraftsmanSignUpForm(request.POST, request.FILES)

        if form.is_valid():
            try:

                user = form.save()

                login(request, user)

                if user.email:
                    logger.info(f"Attempting to send welcome email to {user.email},")
                    try:
                        send_welcome_email_async(
                            user_email=user.email,
                            is_craftsman=True,
                        )
                        logger.info(f"Welcome email queued for {user.email}")
                    except Exception as e:
                        logger.error(f"Failed to queue welcome email: {str(e)}")
                else:
                    logger.warning(
                        f"Cannot send welcome email - missing email or first_name. Email: {user.email}"
                    )

                return redirect("craftsman_dashboard")

            except ValidationError as e:

                logger.warning(
                    f"Validation error during craftsman registration: {str(e)}"
                )
                messages.error(request, f"Validation error: {str(e)}")

            except IntegrityError as e:

                logger.error(f"Integrity error during craftsman registration: {str(e)}")
                messages.error(
                    request,
                    "This email or username is already registered. Please use different credentials.",
                )

            except DatabaseError as e:

                logger.error(f"Database error during craftsman registration: {str(e)}")
                messages.error(
                    request,
                    "A database error occurred. Please try again or contact support.",
                )

            except Exception as e:

                logger.error(
                    f"Unexpected error during craftsman registration: {str(e)}",
                    exc_info=True,
                )
                messages.error(
                    request,
                    "An unexpected error occurred. Our team has been notified. Please try again later.",
                )

        else:

            logger.debug(f"Form validation failed: {form.errors}")

            error_summary = []
            for field, errors in form.errors.items():
                if field == "__all__":
                    for error in errors:
                        error_summary.append(f" {error}")
                else:
                    field_name = (
                        form.fields[field].label
                        if field in form.fields
                        else field.replace("_", " ").title()
                    )
                    for error in errors:
                        error_summary.append(f" {field_name}: {error}")

            if error_summary:
                messages.error(request, error_summary[0])

            if len(error_summary) > 1:
                request.session["form_errors"] = error_summary[1:]
    else:
        form = CraftsmanSignUpForm()

    context = {
        "form": form,
        "title": "Register as Craftsman",
        "form_errors": (
            request.session.pop("form_errors", [])
            if hasattr(request, "session")
            else []
        ),
    }

    return render(request, "register_craftsman.html", context)


@csrf_protect
@require_http_methods(["GET", "POST"])
def signin(request):
    # Early redirect for already authenticated users
    if request.user.is_authenticated:
        if hasattr(request.user, "userprofile"):
            try:
                request.user.userprofile.craftsmanprofile
                return redirect("craftsman_dashboard")
            except:
                return redirect("customer_dashboard")
        return redirect("customer_dashboard")

    if request.method == "POST":
        username = request.POST.get("username", "").strip().lower()  # Normalize to lowercase
        password = request.POST.get("password", "").strip()
        
        if not username or not password:
            messages.error(request, "Please provide both username and password.")
            return render(request, "signin.html", {"username_value": username})

        # OPTIMIZATION: Try to get user from cache first
        from django.core.cache import cache
        cache_key = f"user_auth_{username}"
        cached_user_id = cache.get(cache_key)
        
        user = None
        if cached_user_id:
            try:
                user = User.objects.get(id=cached_user_id)
            except User.DoesNotExist:
                pass
        
        # If not in cache, try authentication
        if not user:
            user = authenticate(request, username=username, password=password)
            
            if not user:
                # Try email lookup (case-insensitive)
                try:
                    user_by_email = User.objects.get(email__iexact=username)
                    user = authenticate(
                        request, 
                        username=user_by_email.username, 
                        password=password
                    )
                except User.DoesNotExist:
                    pass
            
            # Cache successful logins for 1 hour
            if user:
                cache.set(cache_key, user.id, 3600)

        if user and user.is_active:
            login(request, user)
            
            # Set session expiry
            if not request.POST.get("remember"):
                request.session.set_expiry(0)
            
            # Redirect based on user type
            if hasattr(user, "userprofile"):
                try:
                    user.userprofile.craftsmanprofile
                    return redirect("craftsman_dashboard")
                except:
                    return redirect("customer_dashboard")
            return redirect("customer_dashboard")
        
        # Failed login
        messages.error(request, "Invalid username or password.")
        return render(request, "signin.html", {"username_value": username})

    return render(request, "signin.html", {"username_value": ""})


@login_required
def change_password(request):
    if request.method == "POST":
        current = request.POST.get("current_password")
        new = request.POST.get("new_password")
        confirm = request.POST.get("confirm_password")

        if not request.user.check_password(current):
            messages.error(request, "Current password is incorrect")
            return redirect("customer_profile")

        if len(new) < 6:
            messages.error(request, "New password must be at least 6 characters")
            return redirect("customer_profile")

        if new != confirm:
            messages.error(request, "New passwords do not match")
            return redirect("customer_profile")

        request.user.set_password(new)
        request.user.save()

        update_session_auth_hash(request, request.user)
        messages.success(request, "Password updated successfully")

    return redirect("customer_profile")


def user_logout(request):
    auth_logout(request)
    return redirect("home")


########################### CUSTOMER ####################


@login_required(login_url="home")
def customer_dashboard(request):
    is_htmx = request.headers.get("HX-Request") == "true"
    
    try:
        # Get filter parameters
        category_filter = request.GET.get("category", "").strip()
        region_filter = request.GET.get("region", "").strip()
        search_query = request.GET.get("search", "").strip()
        price_min = request.GET.get("price_min", "").strip()
        price_max = request.GET.get("price_max", "").strip()
        rating = request.GET.get("rating", "").strip()
        availability = request.GET.getlist("availability", [])
        features = request.GET.getlist("features", [])
        job_sizes = request.GET.getlist("job_size", [])
        sort_by = request.GET.get("sort", "relevance").strip()

        # Check if filters are active
        filters_active = any(
            [
                category_filter,
                region_filter,
                search_query and len(search_query) >= 2,
                price_min,
                price_max,
                rating,
                availability,
                job_sizes,
                features,
                sort_by != "relevance",
            ]
        )

        # ============== REDIS CACHING ==============
        from django.core.cache import cache
        import hashlib
        import json
        
        # Create cache key from all parameters
        cache_data = {
            'category': category_filter,
            'region': region_filter,
            'search': search_query,
            'price_min': price_min,
            'price_max': price_max,
            'rating': rating,
            'availability': sorted(availability),
            'features': sorted(features),
            'job_sizes': sorted(job_sizes),
            'sort': sort_by,
            'page': request.GET.get("page", "1"),
        }
        
        cache_key = f"customer_dash_{hashlib.md5(json.dumps(cache_data, sort_keys=True).encode()).hexdigest()}"
        
        # Try to get from cache
        if not is_htmx:
            cached_result = cache.get(cache_key)
            if cached_result:
                cached_result.update({
                    "selected_category": category_filter,
                    "selected_region": region_filter,
                    "search_query": search_query,
                    "filters_active": filters_active,
                    "price_min": price_min,
                    "price_max": price_max,
                    "rating": rating,
                    "availability": availability,
                    "job_sizes": job_sizes,
                    "features": features,
                    "sort_by": sort_by,
                })
                
                if is_htmx:
                    return render(request, "partials/dashboard_results.html", cached_result)
                return render(request, "customer_dashboard.html", cached_result)

        # ============== FIXED QUERY WITH ALL NEEDED FIELDS ==============
        # Use select_related and prefetch_related to prevent N+1 queries
        services = (
            Service.objects
            .filter(service_status="Active")
            .select_related(
                'craftsman',
                'craftsman__user_profile',
                'craftsman__user_profile__user'
            )
            .prefetch_related('reviews')
            .only(
                'id', 'title', 'description', 'category', 'region',
                'price_type', 'hourly_rate', 'fixed_price', 'availability',
                'job_size', 'created_at', 'image', 'service_status', 
                'features', 'materials_included',
                # ALL craftsman fields needed in template
                'craftsman__id',
                'craftsman__business_name',
                'craftsman__rating',
                'craftsman__is_verified',
                'craftsman__license_number',
                'craftsman__phone',
                'craftsman__profile_photo',
                'craftsman__user_profile__user__username',
                'craftsman__user_profile__user__first_name',
                'craftsman__user_profile__user__last_name',
                'craftsman__user_profile__user__email',
            )
        )

        # Apply filters
        if category_filter:
            services = services.filter(category=category_filter)

        if region_filter:
            services = services.filter(region=region_filter)

        if search_query and len(search_query) >= 2:
            services = services.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(craftsman__business_name__icontains=search_query)
            )

        # Price filtering
        if price_min or price_max:
            from django.db.models import Case, When, F, Value, DecimalField
            services = services.annotate(
                effective_price=Case(
                    When(price_type='hourly', then=F('hourly_rate')),
                    When(price_type='fixed', then=F('fixed_price')),
                    default=Value(999999),
                    output_field=DecimalField(),
                )
            )
            if price_min:
                try:
                    services = services.filter(effective_price__gte=float(price_min))
                except:
                    pass
            if price_max:
                try:
                    services = services.filter(effective_price__lte=float(price_max))
                except:
                    pass

        if rating:
            try:
                rating_val = float(rating)
                services = services.filter(craftsman__rating__gte=rating_val)
            except:
                pass

        if availability:
            services = services.filter(availability__in=availability)

        if job_sizes:
            services = services.filter(job_size__in=job_sizes)

        if features:
            for feature in features:
                services = services.filter(features__contains=[feature])

        # Annotate with aggregates
        from django.db.models import Avg, Count, Value
        from django.db.models.functions import Coalesce
        
        services = services.annotate(
            avg_rating=Coalesce(
                Avg('reviews__rating'), 
                Value(0.0), 
                output_field=models.FloatField()
            ),
            review_count=Count('reviews', distinct=True)
        )

        # Apply sorting
        services = apply_service_sorting_v2(services, sort_by)
        
        # ============== FORCE QUERY EXECUTION ==============
        # Convert to list to load ALL data into memory
        service_list = list(services)
        
        # ============== PAGINATION ==============
        from django.core.paginator import Paginator
        paginator = Paginator(service_list, 12)
        page = request.GET.get('page', 1)
        page_obj = paginator.get_page(page)

        # Build context
        context = {
            "Service": Service,
            "page_obj": page_obj,
            "services": page_obj,
            "results_count": len(service_list),
            "has_services": len(service_list) > 0,
            "selected_category": category_filter,
            "selected_region": region_filter,
            "search_query": search_query,
            "filters_active": filters_active,
            "price_min": price_min,
            "price_max": price_max,
            "rating": rating,
            "availability": availability,
            "job_sizes": job_sizes,
            "features": features,
            "sort_by": sort_by,
            "AVAILABILITY_CHOICES": AVAILABILITY_CHOICES,
            "SERVICE_SCOPE_CHOICES": SERVICE_SCOPE_CHOICES,
            "REGION_CHOICES": REGION_CHOICES,
            "CATEGORY_CHOICES": CATEGORY_CHOICES,
        }

        # Store in Redis cache (5 minutes)
        if len(service_list) > 0:
            cache.set(cache_key, context, 300)

        # HTMX response
        if is_htmx:
            return render(request, "partials/dashboard_results.html", context)

        return render(request, "customer_dashboard.html", context)

    except Exception as e:
        logger.error(f"Customer dashboard error: {e}")
        import traceback
        traceback.print_exc()
        context = {
            "Service": Service,
            "filters_active": False,
            "results_count": 0,
            "has_services": False,
            "show_alert": "We're working on fixing this issue. Please try again later.",
        }
        return render(request, "customer_dashboard.html", context)


def apply_service_sorting_v2(queryset, sort_by):
    """Optimized sorting function"""
    from django.db.models import Case, When, F, Value, DecimalField
    
    if sort_by == "relevance":
        return queryset.order_by("-craftsman__rating", "-created_at")
    
    elif sort_by == "rating":
        return queryset.order_by("-craftsman__rating", "-created_at")
    
    elif sort_by == "price_low":
        return queryset.annotate(
            sort_price=Case(
                When(price_type='hourly', then=F('hourly_rate')),
                When(price_type='fixed', then=F('fixed_price')),
                default=Value(999999),
                output_field=DecimalField()
            )
        ).order_by('sort_price', '-created_at')
    
    elif sort_by == "price_high":
        return queryset.annotate(
            sort_price=Case(
                When(price_type='hourly', then=F('hourly_rate')),
                When(price_type='fixed', then=F('fixed_price')),
                default=Value(0),
                output_field=DecimalField()
            )
        ).order_by('-sort_price', '-created_at')
    
    elif sort_by == "distance":
        return queryset.order_by("-craftsman__rating", "-created_at")
    
    return queryset.order_by("-craftsman__rating", "-created_at")




from django.db.models import Prefetch, Avg, Count, Value
from django.db.models.functions import Coalesce
from django.core.cache import cache
import hashlib

def service_detail(request, service_id):
    # Try cache first
    cache_key = f"service_detail_{service_id}"
    cached_context = cache.get(cache_key)
    
    if cached_context:
        return render(request, "service_detail.html", cached_context)
    
    # OPTIMIZATION: Load everything in ONE query with correct paths
    service = get_object_or_404(
        Service.objects
        .select_related(
            'craftsman',
            'craftsman__user_profile',
            'craftsman__user_profile__user'
        )
        .annotate(
            avg_rating=Coalesce(
                Avg('reviews__rating'), 
                Value(0.0), 
                output_field=models.FloatField()
            ),
            review_count=Count('reviews')
        ),
        pk=service_id
    )
    
    # Load reviews separately (with proper select_related)
    reviews = Review.objects.filter(service=service).select_related(
        'customer',
        'customer__user_profile',
        'customer__user_profile__user'
    ).order_by('-created_at')[:10]
    
    context = {
        "service": service,
        "craftsman": service.craftsman,
        "reviews": reviews,
        "reviews_count": service.review_count,
        "avg_rating": service.avg_rating,
    }
    
    # Cache for 1 hour (3600 seconds)
    cache.set(cache_key, context, 3600)
    
    return render(request, "service_detail.html", context)


@login_required
def customer_profile(request):
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


@login_required
def saved_services(request):
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
def save_service(request, service_id):
    """Toggle save/unsave a service"""
    
    # Get the service
    service = get_object_or_404(Service, id=service_id)
    
    try:
        # Get customer profile
        customer_profile = request.user.userprofile.customerprofile
        
        # Check current status
        is_saved = customer_profile.saved_services.filter(id=service_id).exists()
        
        # Toggle
        if is_saved:
            customer_profile.saved_services.remove(service)
            is_saved = False
        else:
            customer_profile.saved_services.add(service)
            is_saved = True
        
        # Return updated button
        return render(request, "partials/save_button.html", {
            "service": service,
            "is_saved": is_saved
        })
        
    except (AttributeError, CustomerProfile.DoesNotExist):
        # User is not a customer
        return render(request, "partials/save_button.html", {
            "service": service,
            "is_saved": False,
            "error": "Only customers can save services"
        })


def create_review(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    form = ReviewForm()

    context = {"service": service, "form": form}
    return render(request, "partials/review_form.html", context)


def submit_review(request, service_id):
    service = get_object_or_404(Service, id=service_id)

    if request.method == "POST":
        try:

            customer_profile = request.user.userprofile.customerprofile
        except:

            customer_profile = CustomerProfile.objects.create(
                user_profile=request.user.userprofile
            )

        if Review.objects.filter(service=service, customer=customer_profile).exists():

            return redirect("service_detail", service_id=service_id)

        # Create the review
        Review.objects.create(
            service=service,
            customer=customer_profile,
            rating=request.POST.get("rating"),
            title=request.POST.get("title"),
            comment=request.POST.get("comment"),
        )

        return redirect("service_detail", service_id=service_id)

    return redirect("service_detail", service_id=service_id)


################### CRAFTSMAN ###################


@login_required(login_url="home")
def craftsman_dashboard(request):
    """
    Display the craftsman's dashboard with their services.
    Shows empty state if no services, or service grid if services exist.
    """
    
    
    try:
        craftsman_profile = request.user.userprofile.craftsmanprofile
        
        # Get filter from request
        service_filter = request.GET.get('service-filter', 'all')
        
        # Create cache key
        cache_key = f"craftsman_dash_{craftsman_profile.id}_{service_filter}_{request.GET.get('page', '1')}"
        cached_context = cache.get(cache_key)
        
        if cached_context and not request.headers.get('HX-Request'):
            if request.headers.get('HX-Request'):
                return render(request, "partials/service_grid.html", cached_context)
            return render(request, "craftsman_dasboard.html", cached_context)
        
        # Get base services
        services_qs = Service.objects.filter(craftsman=craftsman_profile)
        
        # Get ALL boost requests in ONE query and annotate statuses
        from django.db.models import OuterRef, Subquery, Exists
        
        # Subquery for pending boosts
        pending_boosts = BoostRequest.objects.filter(
            service=OuterRef('pk'),
            status__in=['pending', 'processing']
        )
        
        # Subquery for approved boosts
        approved_boosts = BoostRequest.objects.filter(
            service=OuterRef('pk'),
            status='approved'
        )
        
        # Subquery for rejected boosts
        rejected_boosts = BoostRequest.objects.filter(
            service=OuterRef('pk'),
            status='rejected'
        )
        
        # Subquery for expired boosts
        expired_boosts = BoostRequest.objects.filter(
            service=OuterRef('pk'),
            status='expired'
        )
        
        # Subquery for latest boost status
        latest_boost = BoostRequest.objects.filter(
            service=OuterRef('pk')
        ).order_by('-created_at').values('status')[:1]
        
        # Annotate all boost info in ONE query
        services_qs = services_qs.annotate(
            has_pending_boost=Exists(pending_boosts),
            has_approved_boost=Exists(approved_boosts),
            has_rejected_boost=Exists(rejected_boosts),
            has_expired_boost=Exists(expired_boosts),
            latest_boost_status=Subquery(latest_boost)
        )
        
        # Apply filters
        if service_filter == 'active':
            services_qs = services_qs.filter(service_status='Active')
        elif service_filter == 'boosted':
            services_qs = services_qs.filter(has_approved_boost=True)
        
        # Order by creation date
        services_qs = services_qs.order_by('-created_at')
        
        # Get counts in ONE query
        total_services = services_qs.count()
        active_count = services_qs.filter(service_status='Active').count()
        paused_count = services_qs.filter(service_status='Paused').count()
        
        # Paginate
        paginator = Paginator(services_qs, 8)
        page_number = request.GET.get('page', 1)
        services = paginator.get_page(page_number)
        
        # Convert to list to force evaluation
        service_list = list(services)
        
        context = {
            'craftsman': craftsman_profile,
            'services': services,
            'total_services': total_services,
            'has_services': total_services > 0,
            'active_count': active_count,
            'paused_count': paused_count,
            'CATEGORY_CHOICES': CATEGORY_CHOICES,
            'REGION_CHOICES': REGION_CHOICES,
            'AVAILABILITY_CHOICES': AVAILABILITY_CHOICES,
            'current_filter': service_filter,
        }
        
        # Cache for 5 minutes
        cache.set(cache_key, context, 300)
        
        # HTMX response
        if request.headers.get('HX-Request'):
            return render(request, "partials/service_grid.html", context)
        return render(request, "craftsman_dasboard.html", context)
        
    except CraftsmanProfile.DoesNotExist:
        return redirect("provider_onboarding")
        
    except Exception as e:
        logger.error(f"Error in craftsman_dasboard: {e}")
        return render(request, "craftsman_dasboard.html", {
            'has_services': False
        })
    



# STEP 1: The Basic "Ad"
class Step1BasicAdForm(forms.Form):
    title = forms.CharField(
        max_length=100,
        label="Service Title",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., Professional Wall Painting'
        }),
        help_text="Make it clear and attractive to customers"
    )
    
    category = forms.ChoiceField(
        choices=[
            ("", "Choose a category"),
            ("plumbing", "Plumber"),
            ("electrical", "Electrician"),
            ("ac_technician", "AC Technician"),
            ("carpentry", "Carpenter"),
            ("tiling", "Tiler"),
            ("painting", "Painter"),
            ("furniture_maker", "Furniture Maker"),
            ("fumigation", "Fumigator"),
            ("dstv_technician", "DSTV Technician"),
            ("gas_appliance", "Gas Appliance Technician"),
            ("pop_worker", "POP Worker"),
            ("cleaning", "Cleaner"),
            ("aluminium_worker", "Aluminium Worker"),
            ("welding", "Welder"),
            ("roofing", "Roof Technician"),
            ("solar_power", "Solar Power Technician"),
            ("masonry", "Mason"),
            ("glass_partitioning", "Glass/Partitioning Worker"),
            ("bricklayer", "Bricklayer / Plasterer"),
            ("foreman", "Foreman"),
            ("landscaping", "Landscaping"),
            ("appliance_repair", "Appliance Repair"),
            ("hvac", "HVAC Services"),
            ("security_installation", "CCTV / Security System Technician"),
            ("generator_technician", "Generator Technician"),
            ("interior_design", "Interior Designer"),
            ("flooring", "Flooring / Epoxy Work"),
            ("metal_fabrication", "Metal Fabrication"),
            ("waterproofing", "Waterproofing Specialist"),
            ("pest_control", "Pest Control"),
            ("scaffolding", "Scaffolding Worker"),
            ("site_supervisor", "Site Supervisor"),
            ("other", "Other"),
        ],
        label="Category",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    description = forms.CharField(
        label="Description",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': '4',
            'placeholder': 'Describe your service...\nExample: I provide professional painting services with high-quality materials. I specialize in interior walls, ceilings, and exterior surfaces. 10+ years experience.'
        }),
        help_text="Tell customers what you do and why they should choose you"
    )
    
    image = forms.ImageField(
        required=False,
        label="Photo of Your Work",
        widget=forms.FileInput(attrs={
            'class': 'file-input-hidden',
            'accept': 'image/*'
        }),
        help_text="Upload one photo showing your best work"
    )

# STEP 2: The Location & Money
class Step2LocationMoneyForm(forms.Form):
    region = forms.ChoiceField(
        choices=[
            ("", "Select your service region"),
            ("abruzzo", "Abruzzo"),
            ("aosta_valley", "Aosta Valley (Valle d'Aosta)"),
            ("apulia", "Apulia (Puglia)"),
            ("basilicata", "Basilicata"),
            ("calabria", "Calabria"),
            ("campania", "Campania"),
            ("emilia_romagna", "Emilia-Romagna"),
            ("friuli_venezia_giulia", "Friuli-Venezia Giulia"),
            ("lazio", "Lazio"),
            ("liguria", "Liguria"),
            ("lombardy", "Lombardy (Lombardia)"),
            ("marche", "Marche"),
            ("molise", "Molise"),
            ("piedmont", "Piedmont (Piemonte)"),
            ("sardinia", "Sardinia (Sardegna)"),
            ("sicily", "Sicily (Sicilia)"),
            ("trentino_south_tyrol", "Trentino-South Tyrol (Trentino-Alto Adige)"),
            ("tuscany", "Tuscany (Toscana)"),
            ("umbria", "Umbria"),
            ("veneto", "Veneto"),
        ],
        label="Where do you work?",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    price_type = forms.ChoiceField(
        choices=[
            ("hourly", "Hourly Rate"),
            ("fixed", "Fixed Price"),
        ],
        label="How do you charge?",
        widget=forms.RadioSelect,
        initial='hourly'
    )
    
    hourly_rate = forms.DecimalField(
        required=False,
        max_digits=8,
        decimal_places=2,
        label="Hourly Rate",
        widget=forms.NumberInput(attrs={
            'class': 'modal-currency-field',
            'placeholder': '0.00',
            'step': '0.01'
        }),
        help_text="€ per hour"
    )
    
    fixed_price = forms.DecimalField(
        required=False,
        max_digits=8,
        decimal_places=2,
        label="Fixed Price",
        widget=forms.NumberInput(attrs={
            'class': 'modal-currency-field',
            'placeholder': '0.00',
            'step': '0.01'
        }),
        help_text="Total € for the job"
    )
    
    estimated_duration = forms.CharField(
        max_length=100,
        required=False,
        label="Estimated Time",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 2-3 hours, Half day, Full day'
        }),
        help_text="For hourly jobs: estimated time needed"
    )
    
    travel_fee = forms.DecimalField(
        required=False,
        max_digits=6,
        decimal_places=2,
        label="Travel Fee (Optional)",
        widget=forms.NumberInput(attrs={
            'class': 'modal-currency-field',
            'placeholder': '0.00',
            'step': '0.01'
        }),
        help_text="Only if you want to charge for travel"
    )

# STEP 3: The "Finish Line"
class Step3FinishLineForm(forms.Form):
    availability = forms.ChoiceField(
        choices=[
            ("immediate", "Immediately Available"),
            ("24_hours", "Within 24 Hours"),
            ("48_hours", "Within 48 Hours"),
            ("scheduled", "By Appointment Only"),
        ],
        label="How fast can you show up?",
        widget=forms.Select(attrs={'class': 'form-control'}),
        initial='immediate'
    )
    
    # Optional extras
    materials_included = forms.BooleanField(
        required=False,
        label='Materials included in price',
        initial=False
    )
    
    # Hidden field to trigger final submission
    final_submit = forms.CharField(widget=forms.HiddenInput(), required=False)

# ✅ SIMPLE WIZARD VIEW
class ServiceWizardView(SessionWizardView):
    template_name = "service_wizard_page.html"
    file_storage = temp_storage
    
    # Define the form list
    form_list = [
        Step1BasicAdForm,      # Step 0: Basic Ad
        Step2LocationMoneyForm, # Step 1: Location & Money  
        Step3FinishLineForm     # Step 2: Finish Line
    ]
    
    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)
        # Add step information for template
        current_step = int(self.steps.current) + 1  # Convert to 1-based
        step_titles = {
            1: "The Basic Ad",
            2: "Location & Money", 
            3: "Finish Line"
        }
        context.update({
            'current_step': current_step,
            'total_steps': len(self.form_list),
            'step_title': step_titles.get(current_step, f"Step {current_step}")
        })
        return context
    
    def done(self, form_list, **kwargs):
        # Collect all form data
        form_data = {}
        image_file = None
        
        for i, form in enumerate(form_list):
            if form.is_valid():
                cleaned_data = form.cleaned_data
                
                # Handle image file from step 0 (Basic Ad)
                if i == 0 and 'image' in cleaned_data and cleaned_data['image']:
                    image_file = cleaned_data['image']
                    # Don't add file object to form_data
                    cleaned_data.pop('image')
                
                form_data.update(cleaned_data)
        
        try:
            # Get craftsman profile
            craftsman_profile = self.request.user.userprofile.craftsmanprofile
            
            # Determine price based on price type
            if form_data['price_type'] == 'hourly':
                hourly_rate = form_data.get('hourly_rate')
                fixed_price = None
            else:
                hourly_rate = None
                fixed_price = form_data.get('fixed_price')
            
            # Create the service object
            service = Service.objects.create(
                craftsman=craftsman_profile,
                title=form_data['title'],
                category=form_data['category'],
                region=form_data['region'],
                description=form_data['description'],
                price_type=form_data['price_type'],
                hourly_rate=hourly_rate,
                fixed_price=fixed_price,
                estimated_duration=form_data.get('estimated_duration', ''),
                min_hours='',  # Optional field
                availability=form_data['availability'],
                job_size='medium',  # Default value
                materials_included=form_data.get('materials_included', False),
                travel_fee=form_data.get('travel_fee'),
                features=[],  # Empty for now
                service_status="Active"  # Set initial status
            )
            
            # Handle image upload
            if image_file:
                service.image = image_file
                service.save()
            
            
            
        except Exception as e:
            print(f"Error creating service: {e}")
            
        
        # Clear wizard session
        try:
            self.storage.reset()
        except:
            pass
        
        # Redirect to dashboard
        return redirect('craftsman_dashboard')

@login_required
def edit_service(request):
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
            
            # Update service fields
            service.title = request.POST.get('title')
            service.category = request.POST.get('category')
            service.description = request.POST.get('description')
            service.price_type = request.POST.get('price_type')
            
            # Handle price based on type
            if service.price_type == 'hourly':
                service.hourly_rate = request.POST.get('hourly_rate')
                service.fixed_price = None
            else:
                service.fixed_price = request.POST.get('fixed_price')
                service.hourly_rate = None
            
            # Update optional fields
            service.region = request.POST.get('region', '')
            service.availability = request.POST.get('availability')
            service.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Service updated successfully',
                'service': {
                    'id': service.id,
                    'title': service.title,
                    'category': service.get_category_display(),
                    'description': service.description,
                    'price_type': service.price_type,
                    'hourly_rate': str(service.hourly_rate) if service.hourly_rate else '',
                    'fixed_price': str(service.fixed_price) if service.fixed_price else '',
                    'region': service.region,
                    'availability': service.availability
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    # GET request - return service data for modal
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
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method'
    }, status=400)



@login_required
def delete_service(request):
    if request.method == 'POST':
        try:
            service_id = request.POST.get('service_id')
            service = get_object_or_404(Service, id=service_id)
            
            # Check if the service belongs to the current user
            # Chain: service.craftsman.user_profile.user
            if service.craftsman.user_profile.user != request.user:
                
                return redirect('craftsman_dashboard')
            
            # Delete the service
            service_title = service.title
            service.delete()
            
            
            
            # Return JSON for AJAX or redirect
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Service deleted successfully'})
            
            return redirect('craftsman_dashboard')
            
        except Exception as e:
            
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': str(e)}, status=400)
            
            return redirect('craftsman_dashboard')
    
    return redirect('craftsman_dashboard')

@login_required
def check_boost_status(request, service_id):
    """Check if service already has pending boost"""
    try:
        service = Service.objects.get(id=service_id)
        
        # Check for pending boosts
        has_pending_boost = BoostRequest.objects.filter(
            service=service,
            status__in=['pending']
        ).exists()
        
        return JsonResponse({
            'has_pending_boost': has_pending_boost,
            'service_id': service_id
        })
        
    except Exception as e:
        return JsonResponse({
            'has_pending_boost': False,
            'error': str(e)
        })

@login_required
def craftsman_profile(request):
    try:
        craftsman_profile = request.user.userprofile.craftsmanprofile
    except:
        messages.error(request, "You need to complete provider onboarding first")
        return redirect("craftsman_dashboard")

    if request.method == "POST":

        service_id = request.POST.get('service_id')
        
        
        service = Service.objects.get(id=service_id)
        
        
        existing_boost = BoostRequest.objects.filter(
            service=service,
            status__in=['pending', 'processing']
        ).exists()
        
        if existing_boost:
            messages.error(request, 'You already have a pending boost request for this service. Please wait for approval.')
            return JsonResponse({
                'success': False,
                'message': 'You already have a pending boost request for this service.'
            })


        request.user.first_name = request.POST.get("first_name")
        request.user.last_name = request.POST.get("last_name")
        request.user.email = request.POST.get("email")
        request.user.save()

        request.user.userprofile.phone = request.POST.get("phone")
        request.user.userprofile.save()

        craftsman_profile.business_name = request.POST.get("business_name")
        craftsman_profile.years_of_experience = request.POST.get("years_of_experience")
        craftsman_profile.license_number = request.POST.get("license_number")
        craftsman_profile.has_license = bool(request.POST.get("license_number"))
        craftsman_profile.phone = request.POST.get("phone")

        if "profile_photo" in request.FILES:
            craftsman_profile.profile_photo = request.FILES["profile_photo"]

        craftsman_profile.save()

        messages.success(request, "Profile updated successfully")
        return redirect("craftsman_profile")

    context = {
        "user": request.user,
        "profile": request.user.userprofile,
        "craftsman": craftsman_profile,
    }
    return render(request, "craftsman_profile.html", context)


@login_required(login_url="home")
def boost_service(request):
    if request.method == "POST":
        try:
            service_id = request.POST.get("service_id")
            
            
            # Get the service
            service = Service.objects.get(id=service_id)
            
            # Permission check
            if service.craftsman.user_profile.user != request.user:
                return JsonResponse({
                    'success': False,
                    'error': 'You do not have permission to boost this service'
                }, status=403)
            
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

            print(f"Boost request created: {boost_request.id}")
            
            return JsonResponse({
                'success': True,
                'message': f'Boost request submitted successfully! Your service will be boosted for {boost_duration} days once payment is verified.'
            })

        except Service.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Service not found'
            }, status=404)
        except Exception as e:
            print(f"Error in boost_service: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': f'Error: {str(e)}'
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method'
    }, status=400)


def craftsman_public_profile(request, pk):
    """Public profile view - Simple optimized"""
    
    craftsman = get_object_or_404(
        CraftsmanProfile.objects.select_related(
            'user_profile',
            'user_profile__user'  # Add this
        ), 
        pk=pk
    )
    
    services = Service.objects.filter(
        craftsman=craftsman,
        service_status='Active'
    ).select_related(
        'craftsman',
        'craftsman__user_profile',
        'craftsman__user_profile__user',  
    ).prefetch_related(
        'boost_requests'
    ).order_by('-created_at')
    
    for service in services:
        service.craftsman_name = service.craftsman.business_name
        service.is_boosted = service.boost_requests.filter(
            status='approved',
            expires_at__gte=timezone.now()
        ).exists()
    
    context = {
        'craftsman': craftsman,
        'services': services,
        'total_services': services.count(),
    }
    
    return render(request, 'craftsman_public_profile.html', context)

def offline_page(request):
    return render(request, 'offline.html')



