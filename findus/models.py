from django.db import models
from django.contrib.auth.models import User


CATEGORY_CHOICES = [
    ("plumbing", "Plumber"),
    ("electrical", "Electrician"),
    ("ac_technician", "AC Technician"),
    ("carpentry", "Carpenter"),
    ("tiling", "Tiler"),
    ("painting", "Painter"),
    ("furniture_maker", "Furniture Maker"),
    ("fumigation", "Fumigator"),
    ("dstv_technician", "DSTV Technician"),
    ("gas_appliance", "Gas Appliance Technician"),
    ("pop_worker", "POP Worker"),
    ("cleaning", "Cleaner"),
    ("aluminium_worker", "Aluminium Worker"),
    ("welding", "Welder"),
    ("roofing", "Roof Technician"),
    ("solar_power", "Solar Power Technician"),
    ("masonry", "Mason"),
    ("glass_partitioning", "Glass/Partitioning Worker"),
    ("bricklayer", "Bricklayer / Plasterer"),
    ("foreman", "Foreman"),
    ("landscaping", "Landscaping"),
    ("appliance_repair", "Appliance Repair"),
    ("hvac", "HVAC Services"),
    ("security_installation", "CCTV / Security System Technician"),
    ("generator_technician", "Generator Technician"),
    ("interior_design", "Interior Designer"),
    ("flooring", "Flooring / Epoxy Work"),
    ("metal_fabrication", "Metal Fabrication"),
    ("waterproofing", "Waterproofing Specialist"),
    ("pest_control", "Pest Control"),
    ("scaffolding", "Scaffolding Worker"),
    ("site_supervisor", "Site Supervisor"),
    ("other", "Other"),
]

REGION_CHOICES = [
    ("abruzzo", "Abruzzo"),
    ("aosta_valley", "Aosta Valley (Valle d'Aosta)"),
    ("apulia", "Apulia (Puglia)"),
    ("basilicata", "Basilicata"),
    ("calabria", "Calabria"),
    ("campania", "Campania"),
    ("emilia_romagna", "Emilia-Romagna"),
    ("friuli_venezia_giulia", "Friuli-Venezia Giulia"),
    ("lazio", "Lazio"),
    ("liguria", "Liguria"),
    ("lombardy", "Lombardy (Lombardia)"),
    ("marche", "Marche"),
    ("molise", "Molise"),
    ("piedmont", "Piedmont (Piemonte)"),
    ("sardinia", "Sardinia (Sardegna)"),
    ("sicily", "Sicily (Sicilia)"),
    ("trentino_south_tyrol", "Trentino-South Tyrol (Trentino-Alto Adige)"),
    ("tuscany", "Tuscany (Toscana)"),
    ("umbria", "Umbria"),
    ("veneto", "Veneto"),
]

PRICE_TYPE_CHOICES = [
    ("hourly", "Hourly Rate"),
    ("fixed", "Fixed Price"),
]

AVAILABILITY_CHOICES = [
    ("immediate", "Immediately Available"),
    ("24_hours", "Within 24 Hours"),
    ("48_hours", "Within 48 Hours"),
    ("scheduled", "By Appointment Only"),
]

SERVICE_SCOPE_CHOICES = [
    ("small", "Small Job (1-2 hours)"),
    ("medium", "Medium Job (Half day)"),
    ("large", "Large Job (Full day+)"),
    ("project", "Multi-day Project"),
]

EXPERIENCE_CHOICES = [
    ("0-1", "0-1 years"),
    ("1-3", "1-3 years"),
    ("3-5", "3-5 years"),
    ("5+", "5+ years"),
]

USER_TYPE_CHOICES = (
    ("customer", "Customer"),
    ("craftsman", "Craftsman"),
)

RATING_CHOICES = [
    (1, "1 Star"),
    (2, "2 Stars"),
    (3, "3 Stars"),
    (4, "4 Stars"),
    (5, "5 Stars"),
]

BOOST_STATUS_CHOICES = [
    ("pending", "Pending"),
    ("approved", "Approved"),
    ("rejected", "Rejected"),
    ("expired", "Expired"),
]


class Service(models.Model):
    craftsman = models.ForeignKey("CraftsmanProfile", on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    region = models.CharField(
        max_length=30,
        choices=REGION_CHOICES,
        help_text="Select the region where you provide this service",
        null=True,
        blank=True,
    )
    description = models.TextField()
    price_type = models.CharField(max_length=10, choices=PRICE_TYPE_CHOICES)
    hourly_rate = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True
    )
    fixed_price = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True
    )
    estimated_duration = models.CharField(max_length=100)
    min_hours = models.CharField(max_length=100, blank=True)
    image = models.ImageField(upload_to="service_images/", null=True, blank=True)
    availability = models.CharField(
        max_length=20, choices=AVAILABILITY_CHOICES, default="immediate"
    )
    job_size = models.CharField(
        max_length=20, choices=SERVICE_SCOPE_CHOICES, default="medium"
    )
    materials_included = models.BooleanField(default=False)
    travel_fee = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True
    )
    features = models.JSONField(default=list, blank=True)
    service_status = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.get_category_display()}"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)

    def __str__(self):
        return self.user.username


class CustomerProfile(models.Model):
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE)

    phone = models.CharField(max_length=20, blank=True, null=True)
    saved_services = models.ManyToManyField(
        Service, related_name="saved_by_customers", blank=True
    )

    def __str__(self):
        return self.user_profile.user.get_full_name()


class CraftsmanProfile(models.Model):
    user_profile = models.OneToOneField("UserProfile", on_delete=models.CASCADE)
    business_name = models.CharField(max_length=255)
    years_of_experience = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES)
    profile_photo = models.ImageField(
        upload_to="craftsman_profiles/", null=True, blank=True
    )
    has_license = models.BooleanField(default=False)
    license_number = models.CharField(max_length=100, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    rating = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    phone = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.user_profile.user.username}"

    def has_complete_profile(self):
        required_fields = [
            self.business_name,
            self.years_of_experience,
            self.profile_photo,
            self.phone,
        ]
        return all(required_fields)


class Review(models.Model):
    service = models.ForeignKey(
        Service, on_delete=models.CASCADE, related_name="reviews"
    )
    customer = models.ForeignKey(
        CustomerProfile, on_delete=models.CASCADE, related_name="reviews"
    )
    rating = models.IntegerField(choices=RATING_CHOICES)
    title = models.CharField(max_length=200)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_verified = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ["service", "customer"]

    def __str__(self):
        return f"{self.customer.user_profile.user.get_full_name()} - {self.service.title} - {self.rating} stars"


class BoostRequest(models.Model):
    service = models.ForeignKey(
        Service, on_delete=models.CASCADE, related_name="boost_requests"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    duration_days = models.IntegerField()
    payment_proof = models.FileField(upload_to="boost_payments/")
    notes = models.TextField(blank=True)
    status = models.CharField(
        max_length=20, choices=BOOST_STATUS_CHOICES, default="pending"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"Boost for {self.service.title} - {self.status}"


class WaitingList(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    category = models.CharField(
        max_length=50, choices=CATEGORY_CHOICES, blank=True, null=True
    )
    location = models.CharField(max_length=255)
    service_needed = models.CharField(max_length=255)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.service_needed}"
