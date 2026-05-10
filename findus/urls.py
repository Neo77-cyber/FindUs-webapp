from django.urls import path
from django.contrib.staticfiles.views import serve
from django.views.decorators.cache import never_cache

# Import from the new views structure
from .views import (
    # Auth views
    register, register_craftsman, signin, user_logout, change_password,
    # Customer views
    customer_dashboard, service_detail, customer_profile, saved_services,
    save_service, submit_review,
    # Craftsman views
    craftsman_dashboard, delete_service, craftsman_profile,
    check_boost_status, boost_service, edit_service,
    # Public views
    home, add_to_waiting_list, craftsman_public_profile, offline_page,
    # Wizard
    service_wizard_view
)

urlpatterns = [
    # ============== PUBLIC ROUTES ==============
    path("", home, name="home"),
    path("waiting-list/", add_to_waiting_list, name="add_to_waiting_list"),
    path('offline/', offline_page, name='offline'),
    path('craftsman/<slug:craftsman_slug>/', craftsman_public_profile, name='craftsman_public_profile'),
    
    # ============== AUTH ROUTES ==============
    path("signin/", signin, name="signin"),
    path("register/", register, name="register"),
    path("register-as-a-craftsman/", register_craftsman, name="register_as_a_craftsman"),
    path("logout", user_logout, name="logout"),
    path("change-password/", change_password, name="change_password"),
    
    
    # ============== CUSTOMER ROUTES ==============
    path("customer-dashboard/", customer_dashboard, name="customer_dashboard"),
    path("customer-profile/", customer_profile, name="customer_profile"),
    path("saved-services/", saved_services, name="saved_services"),
    path("save-service/<slug:service_slug>/", save_service, name="save_service"),
    
    # ============== SERVICE ROUTES ==============
    path("service/<slug:service_slug>/", service_detail, name="service_detail"),
    path("service/<slug:service_slug>/submit-review/", submit_review, name="submit_review"),
    
    # ============== CRAFTSMAN ROUTES ==============
    path("craftsman-dashboard/", craftsman_dashboard, name="craftsman_dashboard"),
    path("craftsman-profile/", craftsman_profile, name="craftsman_profile"),
    
    # Service management
    path('services/add/', service_wizard_view, name='service_wizard'),
    path('services/delete/', delete_service, name='delete_service'),
    path('edit-service/', edit_service, name='edit_service'),
    
    # Boost management
    path("boost-service/", boost_service, name="boost_service"),
    path('check-boost-status/<int:service_id>/', check_boost_status, name='check_boost_status'),
    
    # ============== PWA ROUTES ==============
    path("manifest.json", never_cache(serve), {"path": "manifest.json"}),
    path("service-worker.js", never_cache(serve), {"path": "service-worker.js"}),
]