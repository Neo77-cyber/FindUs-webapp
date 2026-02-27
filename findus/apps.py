from django.apps import AppConfig


class FindusConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "findus"

    def ready(self):
        import findus.signals  # noqa: F401 - connect Service save/delete to cache invalidation
