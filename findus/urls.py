from django.urls import path
from . import views
from django.contrib.staticfiles.views import serve
from django.views.decorators.cache import never_cache
from django.views.generic import TemplateView


urlpatterns = [
    path("", views.home, name="home"),
    path("waiting-list/", views.add_to_waiting_list, name="add_to_waiting_list"),
    path("signin/", views.signin, name="signin"),
    path(
        "register-as-a-craftsman/",
        views.register_craftsman,
        name="register_as_a_craftsman",
    ),
    path("register/", views.register, name="register"),
    path("change-password/", views.change_password, name="change_password"),
    path("customer-dashboard/", views.customer_dashboard, name="customer_dashboard"),
    path("service/<int:service_id>/", views.service_detail, name="service_detail"),
    path("customer-profile/", views.customer_profile, name="customer_profile"),
    path("craftsman-dashboard/", views.craftsman_dashboard, name="craftsman_dashboard"),
    path("craftsman-profile/", views.craftsman_profile, name="craftsman_profile"),
    path(
        "craftsman/<int:craftsman_id>/",
        views.craftsman_public_profile,
        name="craftsman_public_profile",
    ),
    
    path("saved-services/", views.saved_services, name="saved_services"),
    path("save-service/<int:service_id>/", views.save_service, name="save_service"),
    path(
        "service/<int:service_id>/create-review/",
        views.create_review,
        name="create_review",
    ),
    path('create-service/', views.create_service_start, name='create_service_start'),
    path('create-service/step2/', views.create_service_step2, name='create_service_step2'),
    path('create-service/step3/', views.create_service_step3, name='create_service_step3'),
    path('create-service/finalize/', views.create_service_finalize, name='create_service_finalize'),
    path(
        "service/<int:service_id>/submit-review/",
        views.submit_review,
        name="submit_review",
    ),
    path("boost-service/", views.boost_service, name="boost_service"),
    path("logout", views.user_logout, name="logout"),
    path("manifest.json", never_cache(serve), {"path": "manifest.json"}),
    path("service-worker.js", never_cache(serve), {"path": "service-worker.js"}),
    path('offline/', views.offline_page, name='offline'),
]
