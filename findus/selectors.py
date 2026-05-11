from django.shortcuts import get_object_or_404
from django.core.cache import cache
from django.utils import timezone
import logging

from .models import Service, CraftsmanProfile, Review, BoostRequest

logger = logging.getLogger(__name__)


def get_service_by_id(service_id, with_reviews=False):

    query = Service.objects.select_related(
        "craftsman", "craftsman__user_profile", "craftsman__user_profile__user"
    )

    if with_reviews:
        query = query.prefetch_related("reviews__customer__user_profile__user")

    return get_object_or_404(query, pk=service_id)


def get_craftsman_profile(user):

    if not user or not user.is_authenticated:
        return None
    return (
        CraftsmanProfile.objects.select_related("user_profile", "user_profile__user")
        .filter(user_profile__user=user)
        .first()
    )


def get_service_reviews(service, limit=10):

    return (
        Review.objects.filter(service=service)
        .select_related("customer__user_profile__user")
        .order_by("-created_at")[:limit]
    )


def check_pending_boost(service):

    return BoostRequest.objects.filter(
        service=service, status__in=["pending", "processing"]
    ).exists()


def check_active_boost(service):

    return BoostRequest.objects.filter(
        service=service, status="approved", expires_at__gte=timezone.now()
    ).exists()
