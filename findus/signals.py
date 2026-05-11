from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import Service
from .services import CacheManager


@receiver([post_save, post_delete], sender=Service)
def invalidate_craftsman_dashboard_on_service_change(sender, instance, **kwargs):

    craftsman_id = getattr(instance, "craftsman_id", None)
    if craftsman_id is not None:
        CacheManager.invalidate_craftsman_dashboard(craftsman_id)
