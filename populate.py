import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'handyman_project.settings')
django.setup()

from django.contrib.auth.models import User
from findus.models import UserProfile, CraftsmanProfile, Service, CustomerProfile
import random
from decimal import Decimal

print("=== CREATING TEST DATA WITH ALL FIELDS ===")

# Delete existing test users first
User.objects.filter(username__startswith='testuser').delete()
print("Cleaned up old test users")

# Create 10 test users
users = []
for i in range(1, 11):
    user = User.objects.create_user(
        username=f'testuser{i}',
        email=f'testuser{i}@example.com',
        password='password123',
        first_name=f'Test{i}',
        last_name='User'
    )
    users.append(user)
    print(f"✓ User: testuser{i}")

print("\n=== CREATING CRAFTSMEN ===")
craftsmen = []
business_names = [
    "Mario Plumbing Solutions",
    "Luca Electrical Experts", 
    "Anna Cleaning Services",
    "Giorgio Carpentry Masters",
    "Sofia Painting Professionals"
]

for i in range(5):
    user = users[i]
    
    user_profile = UserProfile.objects.create(
        user=user,
        user_type='craftsman'
    )
    
    craftsman = CraftsmanProfile.objects.create(
        user_profile=user_profile,
        business_name=business_names[i],
        years_of_experience=random.choice(['0-1', '1-3', '3-5', '5+']),
        phone=f"+39 333 444 55{i:02d}",
        is_verified=random.choice([True, True, False]),  # 2/3 chance of verified
        rating=round(random.uniform(3.5, 5.0), 1),
        has_license=random.choice([True, False]),
        license_number=f"LIC-00{random.randint(1000, 9999)}" if random.choice([True, False]) else ""
    )
    craftsmen.append(craftsman)
    print(f"✓ Craftsman: {craftsman.business_name} (Rating: {craftsman.rating})")

print("\n=== CREATING SERVICES WITH ALL FIELDS ===")
services_created = 0

# Define available choices from your model
CATEGORIES = ['plumbing', 'electrical', 'ac_technician', 'carpentry', 'cleaning', 
              'painting', 'welding', 'roofing', 'masonry', 'landscaping']
REGIONS = ['lazio', 'lombardy', 'tuscany', 'veneto', 'campania', 'emilia_romagna', 'sicily']
AVAILABILITY_CHOICES = ['immediate', '24_hours', '48_hours', 'scheduled']
JOB_SIZES = ['small', 'medium', 'large', 'project']
FEATURES_OPTIONS = [
    [],
    ['24/7 Support'],
    ['Licensed', 'Insured'],
    ['Free Estimate'],
    ['Emergency Service'],
    ['Guaranteed Work'],
    ['Same Day Service']
]

for craftsman in craftsmen:
    # Each craftsman gets 2-4 services
    num_services = random.randint(2, 4)
    
    for j in range(1, num_services + 1):
        # Determine price type and values
        price_type = random.choice(['hourly', 'fixed'])
        
        if price_type == 'hourly':
            hourly_rate = Decimal(str(round(random.uniform(25.0, 80.0), 2)))
            fixed_price = None
            estimated_duration = f"{random.randint(1, 8)} hours"
            min_hours = f"{random.randint(1, 4)} hours" if random.choice([True, False]) else ""
        else:  # fixed price
            hourly_rate = None
            fixed_price = Decimal(str(round(random.uniform(100.0, 1000.0), 2)))
            estimated_duration = f"{random.randint(1, 5)} days"
            min_hours = ""
        
        # Determine travel fee (50% chance)
        travel_fee = None
        if random.choice([True, False]):
            travel_fee = Decimal(str(round(random.uniform(10.0, 50.0), 2)))
        
        # Create service with ALL fields from your model
        service = Service.objects.create(
            # Required fields
            craftsman=craftsman,
            title=f"{craftsman.business_name.split()[0]} {CATEGORIES[j-1].title()} Service",
            category=CATEGORIES[j-1],
            
            # Optional fields with values
            region=random.choice(REGIONS),
            description=f"""Professional {CATEGORIES[j-1].replace('_', ' ')} services provided by {craftsman.business_name}. 
            Our team has {craftsman.years_of_experience} of experience and we guarantee quality workmanship. 
            We serve the {random.choice(['residential', 'commercial'])} sector with attention to detail.""",
            
            # Price related fields
            price_type=price_type,
            hourly_rate=hourly_rate,
            fixed_price=fixed_price,
            estimated_duration=estimated_duration,
            min_hours=min_hours,
            
            # ✅ CRITICAL FIELDS THAT WERE MISSING:
            availability=random.choice(AVAILABILITY_CHOICES),
            job_size=random.choice(JOB_SIZES),
            
            # Boolean and other fields
            materials_included=random.choice([True, False]),
            travel_fee=travel_fee,
            features=random.choice(FEATURES_OPTIONS),
            service_status=random.choice(['Active', 'Active', 'Active', 'Pending'])
        )
        
        services_created += 1
        print(f"  → Service: {service.title}")
        print(f"     Category: {service.get_category_display()}")
        print(f"     Price: {'$' + str(service.hourly_rate) + '/hour' if service.hourly_rate else '$' + str(service.fixed_price) + ' fixed'}")
        print(f"     Availability: {service.get_availability_display()}")
        print(f"     Job Size: {service.get_job_size_display()}")
        print(f"     Status: {service.service_status}")
        print()

print("\n=== CREATING CUSTOMERS ===")
for i in range(5, 10):
    user = users[i]
    
    user_profile = UserProfile.objects.create(
        user=user,
        user_type='customer'
    )
    
    customer = CustomerProfile.objects.create(
        user_profile=user_profile,
        phone=f"+39 322 555 66{i-4:02d}"
    )
    print(f"✓ Customer: {user.username}")

print("\n" + "="*60)
print("✅ COMPLETE DATA CREATED WITH ALL SERVICE FIELDS!")
print("="*60)
print(f"Total Users: {User.objects.count()}")
print(f"Craftsmen: {CraftsmanProfile.objects.count()}")
print(f"Services: {Service.objects.count()}")
print(f"Customers: {CustomerProfile.objects.count()}")
print("\n📊 SERVICE FIELD BREAKDOWN:")
print(f"• All services have 'availability' field")
print(f"• All services have 'job_size' field") 
print(f"• All services have 'service_status' field")
print(f"• Mix of hourly/fixed pricing")
print(f"• Various categories and regions")
print("\n🔑 TEST LOGINS (password: password123):")
print("Craftsmen: testuser1 to testuser5")
print("Customers: testuser6 to testuser10")