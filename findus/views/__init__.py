"""
Views package initialization
Import all views to make them accessible
"""

# Auth views
from .auth_views import (
    register,
    register_craftsman,
    signin,
    change_password,
    user_logout,
)

# Customer views
from .customer_views import (
    customer_dashboard,
    service_detail,
    customer_profile,
    saved_services,
    save_service,
    submit_review,
    create_review,
)

# Craftsman views
from .craftsman_views import (
    craftsman_dashboard,
    delete_service,
    craftsman_profile,
    check_boost_status,
    boost_service,
    edit_service,
)

# Public views
from .public_views import (
    home,
    add_to_waiting_list,
    craftsman_public_profile,
    offline_page,
)

# Service wizard views
from .service_wizard_views import service_wizard_view

__all__ = [
    # Auth
    "register",
    "register_craftsman",
    "signin",
    "change_password",
    "user_logout",
    # Customer
    "customer_dashboard",
    "service_detail",
    "customer_profile",
    "saved_services",
    "save_service",
    "submit_review",
    "create_review",
    # Craftsman
    "craftsman_dashboard",
    "delete_service",
    "craftsman_profile",
    "check_boost_status",
    "boost_service",
    "edit_service",
    # Public
    "home",
    "add_to_waiting_list",
    "craftsman_public_profile",
    "offline_page",
    # Wizard
    "service_wizard_view",
]
