"""
Authentication views (login, register, logout)
"""
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError
from django.db import IntegrityError, DatabaseError
from django.core.cache import cache
import logging

from ..forms import CustomerSignUpForm, CraftsmanSignUpForm
from ..email_utils import send_welcome_email_async
from ..selectors import get_craftsman_profile

logger = logging.getLogger(__name__)


@csrf_protect
def register(request):
    """Customer registration"""
    
    # Redirect if already authenticated
    if request.user.is_authenticated:
        if hasattr(request.user, "userprofile"):
            try:
                request.user.userprofile.craftsmanprofile
                logger.debug(f"Authenticated craftsman redirected: {request.user.username}")
                return redirect("craftsman_dashboard")
            except:
                logger.debug(f"Authenticated customer redirected: {request.user.username}")
                return redirect("customer_dashboard")

    if request.method == "POST":
        form = CustomerSignUpForm(request.POST)

        if form.is_valid():
            try:
                user = form.save()
                login(request, user)

                # Send welcome email asynchronously
                if user.email:
                    send_welcome_email_async(
                        user_email=user.email,
                        is_craftsman=False,
                    )

                messages.success(request, "Welcome! Your account has been created.")
                return redirect("customer_dashboard")

            except ValidationError as e:
                logger.warning(f"Validation error during registration: {str(e)}")
                messages.error(request, f"Validation error: {str(e)}")

            except IntegrityError as e:
                logger.error(f"Integrity error during registration: {str(e)}")
                messages.error(
                    request,
                    "This email or username is already registered. Please use different credentials.",
                )

            except DatabaseError as e:
                logger.error(f"Database error during registration: {str(e)}")
                messages.error(
                    request,
                    "A database error occurred. Please try again or contact support.",
                )

            except Exception as e:
                logger.error(f"Unexpected error during registration: {str(e)}", exc_info=True)
                messages.error(request, "An unexpected error occurred. Please try again later.")
        else:
            # Log form errors
            logger.warning(f"Form validation failed - Errors: {form.errors}")

            # Display field errors
            for field, errors in form.errors.items():
                if field == "__all__":
                    for error in errors:
                        messages.error(request, f"{error}")
                else:
                    field_name = field.replace("_", " ").title()
                    for error in errors:
                        messages.error(request, f"{field_name}: {error}")
    else:
        form = CustomerSignUpForm()

    return render(request, "register.html", {"form": form})


@csrf_protect
def register_craftsman(request):
    """Craftsman registration"""
    
    # Redirect if already authenticated
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

                # Send welcome email
                if user.email:
                    logger.info(f"Sending welcome email to {user.email}")
                    try:
                        send_welcome_email_async(
                            user_email=user.email,
                            is_craftsman=True,
                        )
                        logger.info(f"Welcome email queued for {user.email}")
                    except Exception as e:
                        logger.error(f"Failed to queue welcome email: {str(e)}")

                messages.success(request, "Welcome! Your craftsman account has been created.")
                return redirect("craftsman_dashboard")

            except ValidationError as e:
                logger.warning(f"Validation error during craftsman registration: {str(e)}")
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
                logger.error(f"Unexpected error during craftsman registration: {str(e)}", exc_info=True)
                messages.error(
                    request,
                    "An unexpected error occurred. Please try again later.",
                )
        else:
            # Log and display errors
            logger.debug(f"Form validation failed: {form.errors}")

            for field, errors in form.errors.items():
                if field == "__all__":
                    for error in errors:
                        messages.error(request, f"{error}")
                else:
                    field_name = (
                        form.fields[field].label
                        if field in form.fields
                        else field.replace("_", " ").title()
                    )
                    for error in errors:
                        messages.error(request, f"{field_name}: {error}")
    else:
        form = CraftsmanSignUpForm()

    context = {
        "form": form,
        "title": "Register as Craftsman",
    }

    return render(request, "register_craftsman.html", context)


@csrf_protect
@require_http_methods(["GET", "POST"])
def signin(request):
    """User login"""
    
    # Early redirect for authenticated users
    if request.user.is_authenticated:
        if hasattr(request.user, "userprofile"):
            try:
                request.user.userprofile.craftsmanprofile
                return redirect("craftsman_dashboard")
            except:
                return redirect("customer_dashboard")
        return redirect("customer_dashboard")

    if request.method == "POST":
        username = request.POST.get("username", "").strip().lower()
        password = request.POST.get("password", "").strip()
        
        if not username or not password:
            messages.error(request, "Please provide both username and password.")
            return render(request, "signin.html", {"username_value": username})

        # Try cache first (optimization)
        cache_key = f"user_auth_{username}"
        cached_user_id = cache.get(cache_key)
        
        user = None
        if cached_user_id:
            try:
                user = User.objects.get(id=cached_user_id)
                # Verify password still matches
                if not user.check_password(password):
                    user = None
                    cache.delete(cache_key)
            except User.DoesNotExist:
                cache.delete(cache_key)
        
        # If not in cache, authenticate
        if not user:
            user = authenticate(request, username=username, password=password)
            
            # Try email lookup if username fails
            if not user:
                try:
                    user_by_email = User.objects.get(email__iexact=username)
                    user = authenticate(
                        request, 
                        username=user_by_email.username, 
                        password=password
                    )
                except User.DoesNotExist:
                    pass
            
            # Cache successful login
            if user:
                cache.set(cache_key, user.id, 3600)  # 1 hour

        if user and user.is_active:
            login(request, user)
            
            # Set session expiry
            if not request.POST.get("remember"):
                request.session.set_expiry(0)  # Browser close
            
            logger.info(f"User logged in: {user.username}")
            
            # Redirect based on user type
            if hasattr(user, "userprofile"):
                try:
                    user.userprofile.craftsmanprofile
                    return redirect("craftsman_dashboard")
                except:
                    return redirect("customer_dashboard")
            return redirect("customer_dashboard")
        
        # Failed login
        logger.warning(f"Failed login attempt for username: {username}")
        messages.error(request, "Invalid username or password.")
        return render(request, "signin.html", {"username_value": username})

    return render(request, "signin.html", {"username_value": ""})


def _profile_redirect(request):
    """Redirect to the correct profile (craftsman or customer) after password change."""
    return redirect("craftsman_profile" if get_craftsman_profile(request.user) else "customer_profile")


@login_required
def change_password(request):
    """Change user password"""
    
    if request.method != "POST":
        return _profile_redirect(request)
    
    current = request.POST.get("current_password")
    new = request.POST.get("new_password")
    confirm = request.POST.get("confirm_password")

    # Validate current password
    if not request.user.check_password(current):
        messages.error(request, "Current password is incorrect")
        return _profile_redirect(request)

    # Validate new password length
    if len(new) < 6:
        messages.error(request, "New password must be at least 6 characters")
        return _profile_redirect(request)

    # Validate password confirmation
    if new != confirm:
        messages.error(request, "New passwords do not match")
        return _profile_redirect(request)

    # Update password
    request.user.set_password(new)
    request.user.save()

    # Keep user logged in
    update_session_auth_hash(request, request.user)
    
    # Clear auth cache
    cache_key = f"user_auth_{request.user.username.lower()}"
    cache.delete(cache_key)
    
    logger.info(f"Password changed for user: {request.user.username}")
    messages.success(request, "Password updated successfully")

    return _profile_redirect(request)


def user_logout(request):
    """User logout"""
    
    # Clear auth cache
    if request.user.is_authenticated:
        cache_key = f"user_auth_{request.user.username.lower()}"
        cache.delete(cache_key)
        logger.info(f"User logged out: {request.user.username}")
    
    auth_logout(request)
    return redirect("home")