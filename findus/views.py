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
from findus.models import AVAILABILITY_CHOICES, SERVICE_SCOPE_CHOICES
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods

from .email_utils import send_welcome_email_async
from .forms import *
from .models import *

# Get logger for this module
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
        category_filter = request.GET.get("category", "")
        region_filter = request.GET.get("region", "")
        search_query = request.GET.get("search", "")
        price_min = request.GET.get("price_min", "")
        price_max = request.GET.get("price_max", "")
        rating = request.GET.get("rating", "")
        availability = request.GET.getlist("availability", [])
        features = request.GET.getlist("features", [])
        job_sizes = request.GET.getlist("job_size", [])
        sort_by = request.GET.get("sort", "relevance")

        # Check if filters are active
        filters_active = any(
            [
                category_filter,
                region_filter,
                search_query,
                price_min,
                price_max,
                rating,
                availability,
                job_sizes,
                features,
                sort_by != "relevance",
            ]
        )

        # Base context
        context = {
            "Service": Service,
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
        }

        # Initialize variables
        services = Service.objects.none()
        craftsmen = CraftsmanProfile.objects.none()
        page_obj = None

        if filters_active:
            try:
                services = Service.objects.filter(service_status="Active")

                if category_filter:
                    services = services.filter(category=category_filter)

                if region_filter:
                    services = services.filter(region=region_filter)

                if search_query and len(search_query.strip()) >= 2:
                    services = services.filter(
                        Q(title__icontains=search_query)
                        | Q(description__icontains=search_query)
                        | Q(craftsman__business_name__icontains=search_query)
                    )

                if price_min:
                    try:
                        price_min_val = float(price_min)
                        if price_min_val >= 0:
                            services = services.filter(
                                Q(hourly_rate__gte=price_min_val)
                                | Q(fixed_price__gte=price_min_val)
                            )
                    except:
                        pass

                if price_max:
                    try:
                        price_max_val = float(price_max)
                        if price_max_val >= 0:
                            services = services.filter(
                                Q(hourly_rate__lte=price_max_val)
                                | Q(fixed_price__lte=price_max_val)
                            )
                    except:
                        pass

                if rating:
                    try:
                        rating_val = float(rating)
                        if 0 <= rating_val <= 5:
                            services = services.filter(
                                craftsman__rating__gte=rating_val
                            )
                    except:
                        pass

                if availability:
                    services = services.filter(availability__in=availability)

                if job_sizes:
                    services = services.filter(job_size__in=job_sizes)

                if features:
                    for feature in features:
                        services = services.filter(features__contains=[feature])

                # Apply sorting
                services = apply_service_sorting(services, sort_by)

                context["services"] = services
                context["has_services"] = services.exists()

            except Exception as e:
                logger.error(f"Filter error: {e}")
                services = Service.objects.filter(service_status="Active")[:50]
                context["services"] = services
                context["has_services"] = services.exists()
                context["show_alert"] = "Showing limited results due to system issue"

        else:
            try:
                craftsmen = CraftsmanProfile.objects.filter().order_by("-rating")[:12]
                services = Service.objects.filter(service_status="Active")

                context["craftsmen"] = craftsmen
                context["has_services"] = services.exists()
            except Exception as e:
                logger.error(f"Default view error: {e}")
                context["craftsmen"] = []
                context["has_services"] = False
                context["show_alert"] = "Unable to load results at this time"

        # Get results count
        if filters_active:
            results_count = services.count()
        else:
            results_count = craftsmen.count()

        context["results_count"] = results_count

        # Pagination
        page = request.GET.get("page", 1)

        if filters_active:
            items = services
        else:
            items = craftsmen

        if items.exists():
            paginator = Paginator(items, 12)

            try:
                page_obj = paginator.page(page)
            except:
                page_obj = paginator.page(1)

            context["page_obj"] = page_obj
        else:

            paginator = Paginator([], 12)
            page_obj = Page([], 1, paginator)
            context["page_obj"] = page_obj

        # HTMX response
        if is_htmx:
            if filters_active:
                return render(request, "partials/filtered_results.html", context)
            else:
                return render(request, "partials/default_results.html", context)

        return render(request, "home.html", context)

    except Exception as e:
        # Log error but show simple alert to user
        logger.error(f"Home view error: {e}")

        # Simple context for error
        context = {
            "Service": Service,
            "filters_active": False,
            "results_count": 0,
            "has_services": False,
            "show_alert": "We're working on fixing this issue. Please try again later.",
        }

        return render(request, "home.html", context)


def apply_service_sorting(queryset, sort_by):

    if sort_by == "relevance":

        return queryset.order_by("-craftsman__rating", "-created_at")

    elif sort_by == "rating":
        return queryset.order_by("-craftsman__rating")

    elif sort_by == "price_low":

        return queryset.order_by(
            models.Case(
                models.When(hourly_rate__isnull=False, then="hourly_rate"),
                models.When(fixed_price__isnull=False, then="fixed_price"),
                default=999999,
                output_field=models.DecimalField(),
            )
        )

    elif sort_by == "price_high":

        return queryset.order_by(
            models.Case(
                models.When(hourly_rate__isnull=False, then=-models.F("hourly_rate")),
                models.When(fixed_price__isnull=False, then=-models.F("fixed_price")),
                default=999999,
                output_field=models.DecimalField(),
            )
        )

    elif sort_by == "distance":

        return queryset.order_by("-craftsman__rating")

    return queryset.order_by("-craftsman__rating")


def add_to_waiting_list(request):
    if request.method == "POST":
        try:

            logger.info(f"Form data: {dict(request.POST)}")

            waiting_list_entry = WaitingList.objects.create(
                name=request.POST.get("fullname"),
                email=request.POST.get("email"),
                phone=request.POST.get("phone"),
                service_needed=request.POST.get("service"),
                location=request.POST.get("location"),
                notes=request.POST.get("notes"),
            )

            logger.info(
                f"Created: {waiting_list_entry.name} - {waiting_list_entry.service_needed}"
            )

            if request.headers.get("HX-Request"):
                return HttpResponse("Success! Added to waiting list.")
            else:
                messages.success(request, "Success! Added to waiting list.")
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
                messages.error(request, "⚠️ Please correct the errors below.")
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
    if request.user.is_authenticated:
        logger.debug(
            f"Already authenticated user accessed signin: {request.user.username}"
        )

        if hasattr(request.user, "userprofile"):
            try:
                request.user.userprofile.craftsmanprofile
                logger.debug(
                    f"Redirecting craftsman to dashboard: {request.user.username}"
                )
                return redirect("craftsman_dashboard")
            except Exception as e:
                logger.debug(
                    f"Redirecting customer to dashboard: {request.user.username}"
                )
                return redirect("customer_dashboard")
        return redirect("customer_dashboard")

    if request.method == "POST":
        username_or_email = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()

        logger.info(f"Login attempt for: {username_or_email}")

        if not username_or_email or not password:
            logger.warning(f"Login attempt with missing credentials")
            messages.error(request, "Please enter both username/email and password.")
            return render(request, "signin.html", {"username_value": username_or_email})

        user = authenticate(request, username=username_or_email, password=password)

        if not user:
            try:
                user_by_email = User.objects.get(email=username_or_email)
                user = authenticate(
                    request, username=user_by_email.username, password=password
                )
            except User.DoesNotExist:
                user = None

        if user:
            if not user.is_active:
                logger.warning(
                    f"Login attempt for inactive account: {username_or_email}"
                )
                messages.error(request, "This account is inactive.")
                return render(
                    request, "signin.html", {"username_value": username_or_email}
                )

            login(request, user)
            logger.info(
                f"User logged in successfully: {user.username} ({user.email}) - IP: {request.META.get('REMOTE_ADDR')}"
            )

            if hasattr(user, "userprofile"):
                try:
                    user.userprofile.craftsmanprofile
                    logger.debug(
                        f"Redirecting craftsman to dashboard after login: {user.username}"
                    )
                    return redirect("craftsman_dashboard")
                except Exception as e:
                    logger.debug(
                        f"Redirecting customer to dashboard after login: {user.username}"
                    )
                    return redirect("customer_dashboard")
            logger.debug(
                f"Redirecting user without profile to dashboard: {user.username}"
            )
            return redirect("customer_dashboard")
        else:
            logger.warning(f"Failed login attempt for: {username_or_email}")

            user_exists = (
                User.objects.filter(username=username_or_email).exists()
                or User.objects.filter(email=username_or_email).exists()
            )

            if user_exists:
                logger.debug(
                    f"Username/email exists but password incorrect: {username_or_email}"
                )
                messages.error(request, "Incorrect password.")
            else:
                logger.debug(f"Username/email not found: {username_or_email}")
                messages.error(request, "No account found with this username/email.")

            return render(request, "signin.html", {"username_value": username_or_email})

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


def customer_dashboard(request):
    is_htmx = request.headers.get("HX-Request") == "true"

    try:
        # Get filter parameters
        category_filter = request.GET.get("category", "")
        region_filter = request.GET.get("region", "")
        search_query = request.GET.get("search", "")
        price_min = request.GET.get("price_min", "")
        price_max = request.GET.get("price_max", "")
        rating = request.GET.get("rating", "")
        availability = request.GET.getlist("availability", [])
        features = request.GET.getlist("features", [])
        job_sizes = request.GET.getlist("job_size", [])
        sort_by = request.GET.get("sort", "relevance")

        # Check if filters are active
        filters_active = any(
            [
                category_filter,
                region_filter,
                search_query,
                price_min,
                price_max,
                rating,
                availability,
                job_sizes,
                features,
            ]
        )

        # Base context
        context = {
            "Service": Service,
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
        }

        # Initialize variables
        services = Service.objects.none()
        page_obj = None

        # Always query services - either filtered or all active
        try:
            services = Service.objects.filter(service_status="Active")

            # Apply filters only if they exist
            if category_filter:
                services = services.filter(category=category_filter)

            if region_filter:
                services = services.filter(region=region_filter)

            if search_query and len(search_query.strip()) >= 2:
                services = services.filter(
                    Q(title__icontains=search_query)
                    | Q(description__icontains=search_query)
                    | Q(craftsman__business_name__icontains=search_query)
                )

            if price_min:
                try:
                    price_min_val = float(price_min)
                    if price_min_val >= 0:
                        services = services.filter(
                            Q(hourly_rate__gte=price_min_val)
                            | Q(fixed_price__gte=price_min_val)
                        )
                except:
                    pass

            if price_max:
                try:
                    price_max_val = float(price_max)
                    if price_max_val >= 0:
                        services = services.filter(
                            Q(hourly_rate__lte=price_max_val)
                            | Q(fixed_price__lte=price_max_val)
                        )
                except:
                    pass

            if rating:
                try:
                    rating_val = float(rating)
                    if 0 <= rating_val <= 5:
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

            # Apply sorting
            services = apply_service_sorting(services, sort_by)

            context["services"] = services
            context["has_services"] = services.exists()

        except Exception as e:
            logger.error(f"Filter error: {e}")
            services = Service.objects.filter(service_status="Active")[:50]
            context["services"] = services
            context["has_services"] = services.exists()
            context["show_alert"] = "Showing limited results due to system issue"

        # Get results count
        results_count = services.count()
        context["results_count"] = results_count

        # Pagination (only if we have results)
        if services.exists():
            page = request.GET.get("page", 1)
            paginator = Paginator(services, 12)

            try:
                page_obj = paginator.page(page)
            except:
                page_obj = paginator.page(1)

            context["page_obj"] = page_obj
        else:
            # Empty paginator for no results
            paginator = Paginator([], 12)
            page_obj = Page([], 1, paginator)
            context["page_obj"] = page_obj

        # HTMX response
        if is_htmx:
            return render(request, "partials/dashboard_results.html", context)

        return render(request, "customer_dashboard.html", context)

    except Exception as e:
        logger.error(f"Customer dashboard error: {e}")

        # Simple context for error
        context = {
            "Service": Service,
            "filters_active": False,
            "results_count": 0,
            "has_services": False,
            "show_alert": "We're working on fixing this issue. Please try again later.",
        }

        return render(request, "customer_dashboard.html", context)


def apply_service_sorting(queryset, sort_by):

    if sort_by == "relevance":
        return queryset.order_by("-craftsman__rating", "-created_at")

    elif sort_by == "rating":
        return queryset.order_by("-craftsman__rating")

    elif sort_by == "price_low":
        return queryset.order_by(
            models.Case(
                models.When(hourly_rate__isnull=False, then="hourly_rate"),
                models.When(fixed_price__isnull=False, then="fixed_price"),
                default=999999,
                output_field=models.DecimalField(),
            )
        )

    elif sort_by == "price_high":
        return queryset.order_by(
            models.Case(
                models.When(hourly_rate__isnull=False, then=-models.F("hourly_rate")),
                models.When(fixed_price__isnull=False, then=-models.F("fixed_price")),
                default=999999,
                output_field=models.DecimalField(),
            )
        )

    elif sort_by == "distance":

        return queryset.order_by("-craftsman__rating")

    return queryset.order_by("-craftsman__rating")


def service_detail(request, service_id):

    try:

        service = get_object_or_404(Service, pk=service_id, service_status="Active")

        craftsman = service.craftsman

        reviews = service.reviews.all().order_by("-created_at")[:5]

        avg_rating = (
            reviews.aggregate(Avg("rating"))["rating__avg"]
            if reviews.exists()
            else craftsman.rating
        )

        context = {
            "service": service,
            "craftsman": craftsman,
            "reviews": reviews,
            "reviews_count": reviews.count(),
            "avg_rating": avg_rating or 0,
        }

        return render(request, "service_detail.html", context)

    except Exception as e:

        print(f"Error in service_detail view: {e}")

        return render(
            request,
            "service_detail.html",
            {"error": "Service not found or unavailable"},
        )


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


@login_required(login_url="home")
def save_service(request, service_id):

    service = get_object_or_404(Service, id=service_id)

    try:

        customer_profile = request.user.userprofile.customerprofile

        if customer_profile.saved_services.filter(id=service_id).exists():

            customer_profile.saved_services.remove(service)
            is_saved = False
        else:

            customer_profile.saved_services.add(service)
            is_saved = True

        context = {
            "service": service,
            "is_saved": is_saved,
        }
        return render(request, "partials/save_button.html", context)

    except CustomerProfile.DoesNotExist:

        is_saved = request.user.userprofile.customerprofile.saved_services.filter(
            id=service.id
        ).exists()

        context = {
            "service": service,
            "is_saved": is_saved,
            "error": "Only customers can save services",
        }
        return render(request, "partials/save_button.html", context)


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
    try:
        craftsman = request.user.userprofile.craftsmanprofile
    except Exception as e:
        messages.error(request, "You need to be a registered craftsman")
        return redirect("home")

    service_id = request.GET.get("edit")
    delete_id = request.GET.get("delete")
    editing_service = None

    if delete_id:
        try:
            service_to_delete = Service.objects.get(id=delete_id, craftsman=craftsman)
            service_title = service_to_delete.title
            service_to_delete.delete()
            messages.success(
                request, f"Service '{service_title}' has been deleted successfully!"
            )
            return redirect("craftsman_dashboard")
        except Service.DoesNotExist:
            messages.error(request, "Service not found")
            return redirect("craftsman_dashboard")

    if service_id:
        try:
            editing_service = Service.objects.get(id=service_id, craftsman=craftsman)
        except Service.DoesNotExist:
            messages.error(request, "Service not found")
            return redirect("craftsman_dashboard")

    if request.method == "POST":
        if editing_service:
            form = ServiceForm(request.POST, request.FILES, instance=editing_service)
            action = "updated"
        else:
            form = ServiceForm(request.POST, request.FILES)
            action = "created"

        if form.is_valid():
            try:
                service = form.save(commit=False)
                if not editing_service:
                    service.craftsman = craftsman
                    service.service_status = "Active"

                service.save()
                form.save_m2m()

                messages.success(request, f"Service {action} successfully!")
                return redirect("craftsman_dashboard")

            except Exception as e:
                messages.error(request, f"Error saving service: {str(e)}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        if editing_service:
            form = ServiceForm(instance=editing_service)
        else:
            form = ServiceForm()

    services_list = (
        Service.objects.filter(craftsman=craftsman)
        .annotate(
            avg_rating=Coalesce(
                Avg("reviews__rating"), Value(0.0), output_field=models.FloatField()
            ),
            review_count=Count("reviews", distinct=True),
        )
        .order_by("-created_at")
    )

    paginator = Paginator(services_list, 6)

    page = request.GET.get("page")
    try:
        services = paginator.page(page)
    except PageNotAnInteger:
        services = paginator.page(1)
    except EmptyPage:
        services = paginator.page(paginator.num_pages)

    return render(
        request,
        "craftsman_dasboard.html",
        {
            "form": form,
            "services": services,
            "craftsman": craftsman,
            "editing_service": editing_service,
        },
    )


@login_required
def craftsman_profile(request):
    try:
        craftsman_profile = request.user.userprofile.craftsmanprofile
    except:
        messages.error(request, "You need to complete provider onboarding first")
        return redirect("provider_onboarding")

    if request.method == "POST":

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
            service = get_object_or_404(
                Service, id=service_id, craftsman__user_profile__user=request.user
            )

            payment_proof = request.FILES.get("payment_proof")
            if not payment_proof:
                messages.error(request, "Please upload payment proof")
                return redirect("craftsman_dashboard")

            allowed_extensions = [".jpg", ".jpeg", ".png", ".pdf"]
            file_extension = os.path.splitext(payment_proof.name)[1].lower()
            if file_extension not in allowed_extensions:
                messages.error(
                    request, "Invalid file type. Please upload JPG, PNG, or PDF"
                )
                return redirect("craftsman_dashboard")

            if payment_proof.size > 5 * 1024 * 1024:  # 5MB
                messages.error(request, "File size must be less than 5MB")
                return redirect("craftsman_dashboard")

            boost_duration = int(request.POST.get("boost_duration", 7))

            price_map = {7: 15, 14: 25, 30: 40}
            price = price_map.get(boost_duration, 15)

            expiry_date = datetime.now() + timedelta(days=boost_duration)

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

            messages.success(
                request,
                f"Boost request submitted successfully! Your service will be boosted for {boost_duration} days once payment is verified.",
            )

        except Service.DoesNotExist:
            messages.error(request, "Service not found")
        except Exception as e:
            messages.error(request, f"Error submitting boost request: {str(e)}")

    return redirect("craftsman_dashboard")


@login_required(login_url="home")
def craftsman_public_profile(request, craftsman_id):

    craftsman = get_object_or_404(
        CraftsmanProfile.objects.select_related("user_profile", "user_profile__user"),
        id=craftsman_id,
    )

    services = (
        Service.objects.filter(craftsman=craftsman, service_status="Active")
        .annotate(avg_rating=Avg("reviews__rating"), review_count=Count("reviews"))
        .order_by("-created_at")
    )

    paginator = Paginator(services, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    total_reviews = Review.objects.filter(service__craftsman=craftsman).count()
    avg_rating = (
        Review.objects.filter(service__craftsman=craftsman).aggregate(
            avg_rating=Avg("rating")
        )["avg_rating"]
        or 0
    )

    craftsman_stats = {
        "total_services": services.count(),
        "total_reviews": total_reviews,
        "avg_rating": round(avg_rating, 1) if avg_rating else 0,
        "member_since": craftsman.created_at,
    }

    context = {
        "craftsman": craftsman,
        "services": page_obj,
        "craftsman_stats": craftsman_stats,
    }

    return render(request, "craftsman_public_profile.html", context)

def offline_page(request):
    return render(request, 'offline.html')
