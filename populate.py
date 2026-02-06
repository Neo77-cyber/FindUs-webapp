from django.contrib.auth.models import User
from findus.models import UserProfile, CraftsmanProfile, Service, CustomerProfile
import random

print("Creating test data (skipping existing users)...")

# List of test usernames
test_usernames = [f'testuser{i}' for i in range(1, 11)]

# Create users that don't exist yet
users = []
for username in test_usernames:
    if not User.objects.filter(username=username).exists():
        user = User.objects.create_user(
            username=username,
            email=f'{username}@example.com',
            password='password123',
            first_name=f'Test{username[-1]}',
            last_name='User'
        )
        users.append(user)
        print(f"✓ Created user: {username}")
    else:
        user = User.objects.get(username=username)
        users.append(user)
        print(f"→ User already exists: {username}")

# Only proceed if we have at least 5 users
if len(users) >= 5:
    categories = ['plumbing', 'electrical', 'carpentry', 'painting', 'cleaning', 'welding', 'roofing', 'masonry', 'landscaping', 'appliance_repair']
    regions = ['lazio', 'lombardy', 'tuscany', 'veneto', 'campania', 'emilia_romagna', 'sicily', 'piedmont', 'apulia', 'calabria']
    business_names = [
        "Elite Plumbing Solutions", "Spark Electric Masters", "Precision Carpentry Co", 
        "Color Masters Painting", "Clean Pro Services", "Expert Welding Works",
        "Roof Masters", "Masonry Experts", "Green Landscaping", "Appliance Fix Pros"
    ]

    # First 5 users become craftsmen
    for i, user in enumerate(users[:5]):
        # Create user profile if it doesn't exist
        user_profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={'user_type': 'craftsman'}
        )
        
        if created:
            user_profile.user_type = 'craftsman'
            user_profile.save()
        
        # Create craftsman profile if it doesn't exist
        craftsman, craftsman_created = CraftsmanProfile.objects.get_or_create(
            user_profile=user_profile,
            defaults={
                'business_name': business_names[i],
                'service_category': categories[i],
                'services_offered': f"Professional {categories[i]} services for residential and commercial clients",
                'service_area': f"{regions[i].capitalize()} region",
                'years_of_experience': random.choice(['0-1', '1-3', '3-5', '5+']),
                'description': f"Expert {categories[i]} professional with excellent reviews and customer satisfaction",
                'is_verified': random.choice([True, True, True, False]),
                'rating': round(random.uniform(3.5, 5.0), 1),
                'address': f"{i+1} Test Street",
                'city': "Test City",
                'state': "Test State",
                'country': "Italy",
                'postal_code': "00100",
                'phone': f"+39 123 456 78{i:02d}"
            }
        )
        
        if craftsman_created:
            print(f"✓ Created craftsman: {craftsman.business_name}")
            
            # Create 2 services for each craftsman
            for j in range(1, 3):
                price_type = random.choice(['hourly', 'fixed'])
                hourly_rate = random.randint(25, 80) if price_type == 'hourly' else None
                fixed_price = random.randint(100, 500) if price_type == 'fixed' else None
                
                service = Service.objects.create(
                    craftsman=craftsman,
                    title=f"{craftsman.business_name} - {categories[i]} Service {j}",
                    category=categories[i],
                    region=random.choice(regions),
                    description=f"Professional {categories[i]} services including installation, repair, and maintenance.",
                    price_type=price_type,
                    hourly_rate=hourly_rate,
                    fixed_price=fixed_price,
                    estimated_duration=f"{random.randint(1, 8)} hours",
                    min_hours=f"{random.randint(1, 4)} hours" if j % 2 == 0 else "",
                    availability=random.choice(['immediate', '24_hours', '48_hours', 'scheduled']),
                    job_size=random.choice(['small', 'medium', 'large', 'project']),
                    materials_included=random.choice([True, False]),
                    travel_fee=random.choice([None, 10.00, 20.00, 30.00]),
                    features=random.choice([[], ['verified'], ['licensed'], ['insured'], ['warranty'], ['verified', 'licensed']]),
                    service_status='Active'
                )
                print(f"  → Created service: {service.title}")
        else:
            print(f"→ Craftsman already exists: {craftsman.business_name}")

    # Create customer profiles for remaining users
    for user in users[5:10]:
        user_profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={'user_type': 'customer'}
        )
        
        if created:
            customer = CustomerProfile.objects.create(
                user_profile=user_profile,
                address=f"{random.randint(100, 999)} Customer Street",
                city="Customer City",
                state="Customer State",
                country="Italy",
                postal_code="00100",
                phone=f"+39 987 654 32{random.randint(10, 99)}"
            )
            print(f"✓ Created customer: {user.username}")
        else:
            print(f"→ User profile already exists: {user.username}")

    print("\n✅ Summary:")
    print(f"  • Total users: {User.objects.count()}")
    print(f"  • Craftsmen: {CraftsmanProfile.objects.count()}")
    print(f"  • Services: {Service.objects.count()}")
    print(f"  • Customers: {CustomerProfile.objects.count()}")

    print("\n🔑 Test Logins (all use password: password123):")
    for user in users[:5]:
        print(f"  Craftsman: {user.username}")
    for user in users[5:]:
        print(f"  Customer: {user.username}")
else:
    print("❌ Not enough users to create craftsmen and services.")