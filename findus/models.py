from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify


CATEGORY_CHOICES = [
    ("plumbing", _("Plumber")),
    ("electrical", _("Electrician")),
    ("ac_technician", _("AC Technician")),
    ("carpentry", _("Carpenter")),
    ("tiling", _("Tiler")),
    ("painting", _("Painter")),
    ("furniture_maker", _("Furniture Maker")),
    ("fumigation", _("Fumigator")),
    ("dstv_technician", _("DSTV Technician")),
    ("gas_appliance", _("Gas Appliance Technician")),
    ("pop_worker", _("POP Worker")),
    ("cleaning", _("Cleaner")),
    ("aluminium_worker", _("Aluminium Worker")),
    ("welding", _("Welder")),
    ("roofing", _("Roof Technician")),
    ("solar_power", _("Solar Power Technician")),
    ("masonry", _("Mason")),
    ("glass_partitioning", _("Glass/Partitioning Worker")),
    ("bricklayer", _("Bricklayer / Plasterer")),
    ("foreman", _("Foreman")),
    ("landscaping", _("Landscaping")),
    ("appliance_repair", _("Appliance Repair")),
    ("hvac", _("HVAC Services")),
    ("security_installation", _("CCTV / Security System Technician")),
    ("generator_technician", _("Generator Technician")),
    ("interior_design", _("Interior Designer")),
    ("flooring", _("Flooring / Epoxy Work")),
    ("metal_fabrication", _("Metal Fabrication")),
    ("waterproofing", _("Waterproofing Specialist")),
    ("pest_control", _("Pest Control")),
    ("scaffolding", _("Scaffolding Worker")),
    ("site_supervisor", _("Site Supervisor")),
    ("other", _("Other")),
]

REGION_CHOICES = [
    ("abruzzo", _("Abruzzo")),
    ("aosta_valley", _("Aosta Valley (Valle d'Aosta)")),
    ("apulia", _("Apulia (Puglia)")),
    ("basilicata", _("Basilicata")),
    ("calabria", _("Calabria")),
    ("campania", _("Campania")),
    ("emilia_romagna", _("Emilia-Romagna")),
    ("friuli_venezia_giulia", _("Friuli-Venezia Giulia")),
    ("lazio", _("Lazio")),
    ("liguria", _("Liguria")),
    ("lombardy", _("Lombardy (Lombardia)")),
    ("marche", _("Marche")),
    ("molise", _("Molise")),
    ("piedmont", _("Piedmont (Piemonte)")),
    ("sardinia", _("Sardinia (Sardegna)")),
    ("sicily", _("Sicily (Sicilia)")),
    ("trentino_south_tyrol", _("Trentino-South Tyrol (Trentino-Alto Adige)")),
    ("tuscany", _("Tuscany (Toscana)")),
    ("umbria", _("Umbria")),
    ("veneto", _("Veneto")),
]

PRICE_TYPE_CHOICES = [
    ("hourly", _("Hourly Rate")),
    ("fixed", _("Fixed Price")),
]

AVAILABILITY_CHOICES = [
    ("immediate", _("Immediately Available")),
    ("24_hours", _("Within 24 Hours")),
    ("48_hours", _("Within 48 Hours")),
    ("scheduled", _("By Appointment Only")),
]

SERVICE_SCOPE_CHOICES = [
    ("small", _("Small Job (1-2 hours)")),
    ("medium", _("Medium Job (Half day)")),
    ("large", _("Large Job (Full day+)")),
    ("project", _("Multi-day Project")),
]

EXPERIENCE_CHOICES = [
    ("0-1", _("0-1 years")),
    ("1-3", _("1-3 years")),
    ("3-5", _("3-5 years")),
    ("5+", _("5+ years")),
]

USER_TYPE_CHOICES = (
    ("customer", _("Customer")),
    ("craftsman", _("Craftsman")),
)

RATING_CHOICES = [
    (1, _("1 Star")),
    (2, _("2 Stars")),
    (3, _("3 Stars")),
    (4, _("4 Stars")),
    (5, _("5 Stars")),
]

BOOST_STATUS_CHOICES = [
    ("pending", _("Pending")),
    ("approved", _("Approved")),
    ("rejected", _("Rejected")),
    ("expired", _("Expired")),
]


class Service(models.Model):
    craftsman = models.ForeignKey(
        "CraftsmanProfile", on_delete=models.CASCADE, verbose_name=_("craftsman")
    )
    title = models.CharField(_("title"), max_length=100)
    slug = models.SlugField(_("slug"), max_length=120, blank=True, null=True)
    category = models.CharField(_("category"), max_length=50, choices=CATEGORY_CHOICES)
    region = models.CharField(
        _("region"),
        max_length=30,
        choices=REGION_CHOICES,
        help_text=_("Select the region where you provide this service"),
        null=True,
        blank=True,
    )
    description = models.TextField(_("description"))
    price_type = models.CharField(
        _("price type"), max_length=10, choices=PRICE_TYPE_CHOICES
    )
    hourly_rate = models.DecimalField(
        _("hourly rate"), max_digits=8, decimal_places=2, null=True, blank=True
    )
    fixed_price = models.DecimalField(
        _("fixed price"), max_digits=8, decimal_places=2, null=True, blank=True
    )
    estimated_duration = models.CharField(_("estimated duration"), max_length=100)
    min_hours = models.CharField(_("minimum hours"), max_length=100, blank=True)
    image = models.ImageField(
        _("image"), upload_to="service_images/", null=True, blank=True
    )
    availability = models.CharField(
        _("availability"),
        max_length=20,
        choices=AVAILABILITY_CHOICES,
        default="immediate",
    )
    job_size = models.CharField(
        _("job size"), max_length=20, choices=SERVICE_SCOPE_CHOICES, default="medium"
    )
    materials_included = models.BooleanField(_("materials included"), default=False)
    travel_fee = models.DecimalField(
        _("travel fee"), max_digits=6, decimal_places=2, null=True, blank=True
    )
    features = models.JSONField(_("features"), default=list, blank=True)
    service_status = models.CharField(_("service status"), max_length=100)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        verbose_name = _("service")
        verbose_name_plural = _("services")
        indexes = [
            models.Index(fields=["service_status", "-created_at"]),
            models.Index(fields=["category", "service_status"]),
            models.Index(fields=["region", "service_status"]),
            models.Index(fields=["availability"]),
            models.Index(fields=["job_size"]),
            models.Index(fields=["price_type"]),
        ]

    def __str__(self):
        return f"{self.title} - {self.get_category_display()}"

    def save(self, *args, **kwargs):
        if not self.slug or self.slug == "":
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1

            existing = Service.objects.filter(slug=slug)
            if self.pk:
                existing = existing.exclude(pk=self.pk)
            while existing.exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
                existing = Service.objects.filter(slug=slug)
                if self.pk:
                    existing = existing.exclude(pk=self.pk)
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def latest_boost_status_display(self):
        """Label for annotated latest_boost_status (used in craftsman dashboard grid)."""
        status = getattr(self, "latest_boost_status", None)
        if not status:
            return ""
        return dict(BOOST_STATUS_CHOICES).get(status, str(status))


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name=_("user"))
    user_type = models.CharField(
        _("user type"), max_length=10, choices=USER_TYPE_CHOICES
    )

    class Meta:
        verbose_name = _("user profile")
        verbose_name_plural = _("user profiles")

    def __str__(self):
        return self.user.username


class CustomerProfile(models.Model):
    user_profile = models.OneToOneField(
        UserProfile, on_delete=models.CASCADE, verbose_name=_("user profile")
    )
    phone = models.CharField(_("phone"), max_length=20, blank=True, null=True)
    saved_services = models.ManyToManyField(
        Service,
        related_name="saved_by_customers",
        blank=True,
        verbose_name=_("saved services"),
    )

    class Meta:
        verbose_name = _("customer profile")
        verbose_name_plural = _("customer profiles")

    def __str__(self):
        return self.user_profile.user.get_full_name() or self.user_profile.user.username


class CraftsmanProfile(models.Model):
    user_profile = models.OneToOneField(
        "UserProfile", on_delete=models.CASCADE, verbose_name=_("user profile")
    )
    business_name = models.CharField(_("business name"), max_length=255)
    slug = models.SlugField(_("slug"), max_length=260, blank=True, null=True)
    years_of_experience = models.CharField(
        _("years of experience"), max_length=20, choices=EXPERIENCE_CHOICES
    )
    profile_photo = models.ImageField(
        _("profile photo"), upload_to="craftsman_profiles/", null=True, blank=True
    )
    has_license = models.BooleanField(_("has license"), default=False)
    license_number = models.CharField(
        _("license number"), max_length=100, blank=True, null=True
    )
    is_verified = models.BooleanField(_("is verified"), default=False)
    rating = models.FloatField(_("rating"), default=0.0)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)
    phone = models.CharField(_("phone"), max_length=20)

    class Meta:
        verbose_name = _("craftsman profile")
        verbose_name_plural = _("craftsman profiles")

    def __str__(self):
        return f"{self.user_profile.user.username}"

    def save(self, *args, **kwargs):
        if not self.slug or self.slug == "":

            if self.business_name and self.business_name.strip():
                base_string = self.business_name
            else:
                base_string = self.user_profile.user.username

            base_slug = slugify(base_string)
            slug = base_slug
            counter = 1

            existing = CraftsmanProfile.objects.filter(slug=slug)
            if self.pk:
                existing = existing.exclude(pk=self.pk)
            while existing.exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
                existing = CraftsmanProfile.objects.filter(slug=slug)
                if self.pk:
                    existing = existing.exclude(pk=self.pk)
            self.slug = slug
        super().save(*args, **kwargs)

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
        Service,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name=_("service"),
    )
    customer = models.ForeignKey(
        CustomerProfile,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name=_("customer"),
    )
    rating = models.IntegerField(_("rating"), choices=RATING_CHOICES)
    title = models.CharField(_("title"), max_length=200)
    comment = models.TextField(_("comment"))
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)
    is_verified = models.BooleanField(_("is verified"), default=False)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ["service", "customer"]
        verbose_name = _("review")
        verbose_name_plural = _("reviews")

    def __str__(self):
        return f"{self.customer} - {self.service.title} - {self.rating} stars"


class BoostRequest(models.Model):
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name="boost_requests",
        verbose_name=_("service"),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("user"))
    price = models.DecimalField(_("price"), max_digits=6, decimal_places=2)
    duration_days = models.IntegerField(_("duration days"))
    payment_proof = models.FileField(_("payment proof"), upload_to="boost_payments/")
    notes = models.TextField(_("notes"), blank=True)
    status = models.CharField(
        _("status"), max_length=20, choices=BOOST_STATUS_CHOICES, default="pending"
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    expires_at = models.DateTimeField(_("expires at"))

    class Meta:
        verbose_name = _("boost request")
        verbose_name_plural = _("boost requests")

    def __str__(self):
        return f"Boost for {self.service.title} - {self.status}"


class WaitingList(models.Model):
    name = models.CharField(_("name"), max_length=255)
    email = models.EmailField(_("email"))
    phone = models.CharField(_("phone"), max_length=20, blank=True, null=True)
    category = models.CharField(
        _("category"), max_length=50, choices=CATEGORY_CHOICES, blank=True, null=True
    )
    location = models.CharField(_("location"), max_length=255)
    service_needed = models.CharField(_("service needed"), max_length=255)
    notes = models.TextField(_("notes"), blank=True, null=True)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)

    class Meta:
        verbose_name = _("waiting list entry")
        verbose_name_plural = _("waiting list entries")

    def __str__(self):
        return f"{self.name} - {self.service_needed}"
