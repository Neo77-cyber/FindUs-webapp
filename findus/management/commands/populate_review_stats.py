from django.core.management.base import BaseCommand
from django.db.models import Avg, Count
from findus.models import Service, Review


class Command(BaseCommand):
    help = 'Populate review_count and avg_rating for all services'

    def handle(self, *args, **options):
        services = Service.objects.all()
        updated = 0
        
        for service in services:
            stats = Review.objects.filter(service=service).aggregate(
                avg_rating=Avg('rating'),
                review_count=Count('id')
            )
            
            service.avg_rating = stats['avg_rating'] or 0.0
            service.review_count = stats['review_count']
            service.save(update_fields=['avg_rating', 'review_count'])
            updated += 1
            
            if updated % 100 == 0:
                self.stdout.write(f'Updated {updated} services...')
        
        self.stdout.write(self.style.SUCCESS(f'Successfully updated {updated} services'))