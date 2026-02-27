"""
App signals: invalidate dashboard cache when services change (edit/delete from any source).
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import Service
from .services import CacheManager


@receiver([post_save, post_delete], sender=Service)
def invalidate_craftsman_dashboard_on_service_change(sender, instance, **kwargs):
    """Whenever a Service is saved or deleted, invalidate that craftsman's dashboard cache."""
    craftsman_id = getattr(instance, "craftsman_id", None)
    if craftsman_id is not None:
        CacheManager.invalidate_craftsman_dashboard(craftsman_id)
