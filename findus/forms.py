import re

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import transaction

from .models import (
    CraftsmanProfile,
    CustomerProfile,
    Review,
    Service,
    UserProfile,
    CATEGORY_CHOICES,
    PRICE_TYPE_CHOICES,
    AVAILABILITY_CHOICES,
    REGION_CHOICES,
)


User = get_user_model()


class BaseUserForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(max_length=254, required=True)

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        )


class CustomerSignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=20, required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2", "phone"]

    def clean_email(self):
        email = self.cleaned_data.get("email").lower().strip()

        if User.objects.filter(email=email).exists():
            raise ValidationError("This email is already registered.")

        return email

    def clean_phone(self):
        
        phone = self.cleaned_data.get("phone", "")
        
        # Make sure it's a string
        phone = str(phone).strip()
        
        # Remove everything except digits and +
        phone = re.sub(r'[^\d+]', '', phone)
        
        # Check if empty after cleaning
        if not phone:
            raise ValidationError("Please enter a phone number.")
        
        # Check if already exists
        if CustomerProfile.objects.filter(phone=phone).exists():
            raise ValidationError("This phone number is already registered.")
        
        # Store in +39XXXXXXXXXX format
        if phone.startswith('+39'):
            # Already has +39
            pass
        elif phone.startswith('39'):
            # Has 39 without +
            phone = '+' + phone
        elif phone.startswith('3') or phone.startswith('0'):
            # Italian mobile (3) or landline (0)
            phone = '+39' + phone
        
        

        return phone

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"].lower()

        if commit:
            user.save()

            user_profile = UserProfile.objects.create(user=user, user_type="customer")

            CustomerProfile.objects.create(
                user_profile=user_profile,
                phone=self.cleaned_data.get("phone"),
            )

        return user


class CraftsmanSignUpForm(UserCreationForm):

    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=20, required=True)
    profile_photo = forms.ImageField(required=False)
    has_license = forms.BooleanField(required=False)
    license_number = forms.CharField(max_length=100, required=False)
    years_of_experience = forms.ChoiceField(
        choices=CraftsmanProfile._meta.get_field("years_of_experience").choices,
        required=True,
    )

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def clean_email(self):
        email = self.cleaned_data["email"].lower().strip()
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email already registered")
        return email

    def clean_phone(self):
        
        phone = self.cleaned_data.get("phone", "")
        
        # Make sure it's a string
        phone = str(phone).strip()
        
        # Remove everything except digits and +
        phone = re.sub(r'[^\d+]', '', phone)
        
        # Check if empty after cleaning
        if not phone:
            raise ValidationError("Please enter a phone number.")
        
        # Check if already exists
        if CustomerProfile.objects.filter(phone=phone).exists():
            raise ValidationError("This phone number is already registered.")
        
        # Store in +39XXXXXXXXXX format
        if phone.startswith('+39'):
            # Already has +39
            pass
        elif phone.startswith('39'):
            # Has 39 without +
            phone = '+' + phone
        elif phone.startswith('3') or phone.startswith('0'):
            # Italian mobile (3) or landline (0)
            phone = '+39' + phone
        
        

        return phone

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("has_license") and not cleaned_data.get("license_number"):
            raise ValidationError("Please enter license number")
        return cleaned_data

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"].lower()

        if commit:
            user.save()

            user_profile = UserProfile.objects.create(user=user, user_type="craftsman")

            craftsman = CraftsmanProfile.objects.create(
                user_profile=user_profile,
                years_of_experience=self.cleaned_data["years_of_experience"],
                phone=self.cleaned_data["phone"],
                has_license=self.cleaned_data.get("has_license", False),
                license_number=self.cleaned_data.get("license_number", ""),
                is_verified=False,
                rating=0.0,
            )

            if self.cleaned_data.get("profile_photo"):
                craftsman.profile_photo = self.cleaned_data["profile_photo"]
                craftsman.save()

        return user


class ServiceForm(forms.ModelForm):
    image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={"class": "form-control", "accept": "image/*"}),
        help_text="Upload one service image, You can upload an image of your self or an image of a tool you work with",
    )

    AVAILABILITY_CHOICES = [
        ("immediate", "Immediately Available"),
        ("24_hours", "Within 24 Hours"),
        ("48_hours", "Within 48 Hours"),
        ("scheduled", "By Appointment Only"),
    ]

    REGION_CHOICES = [
        ("", "-- Select a Region --"),
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

    SERVICE_SCOPE_CHOICES = [
        ("small", "Small Job (1-2 hours)"),
        ("medium", "Medium Job (Half day)"),
        ("large", "Large Job (Full day+)"),
        ("project", "Multi-day Project"),
    ]

    SERVICE_FEATURES = [
        ("emergency", "24/7 Emergency Service"),
        ("warranty", "Service Warranty Included"),
        ("licensed", "Fully Licensed"),
        ("insured", "Insured & Bonded"),
        ("free_estimate", "Free Estimate"),
        ("senior_discount", "Senior Discount"),
    ]

    availability = forms.ChoiceField(
        choices=AVAILABILITY_CHOICES,
        widget=forms.RadioSelect(attrs={"class": "form-check-input"}),
        initial="immediate",
    )

    job_size = forms.ChoiceField(
        choices=SERVICE_SCOPE_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    materials_included = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
        help_text="Materials included in price",
    )

    travel_fee = forms.DecimalField(
        max_digits=6,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "e.g., 25.00"}
        ),
        help_text="Additional travel fee",
    )

    features = forms.MultipleChoiceField(
        choices=SERVICE_FEATURES,
        widget=forms.CheckboxSelectMultiple(attrs={"class": "form-check-input"}),
        required=False,
    )

    region = forms.ChoiceField(
        choices=REGION_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"}),
        help_text="Select the region where you provide this service",
    )

    class Meta:
        model = Service
        fields = [
            "title",
            "category",
            "description",
            "price_type",
            "hourly_rate",
            "fixed_price",
            "estimated_duration",
            "min_hours",
            "image",
            "availability",
            "job_size",
            "region",
            "materials_included",
            "travel_fee",
            "features",
        ]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g., Emergency Plumbing Repair",
                }
            ),
            "category": forms.Select(attrs={"class": "form-control"}),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Describe your service in detail...",
                }
            ),
            "price_type": forms.RadioSelect(attrs={"class": "form-check-input"}),
            "hourly_rate": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "e.g., 50.00"}
            ),
            "fixed_price": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "e.g., 200.00"}
            ),
            "estimated_duration": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "e.g., 2-3 hours"}
            ),
            "min_hours": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "e.g., 1 hour"}
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        price_type = cleaned_data.get("price_type")
        hourly_rate = cleaned_data.get("hourly_rate")
        fixed_price = cleaned_data.get("fixed_price")

        if price_type == "hourly" and not hourly_rate:
            raise forms.ValidationError("Hourly rate is required for hourly pricing")
        if price_type == "fixed" and not fixed_price:
            raise forms.ValidationError("Fixed price is required for fixed pricing")

        return cleaned_data


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "title", "comment"]
        widgets = {
            "rating": forms.RadioSelect(attrs={"class": "form-check-input"}),
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Brief summary of your experience",
                }
            ),
            "comment": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Share details of your experience with this service...",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["rating"].widget.choices = [
            (5, "⭐⭐⭐⭐⭐ Excellent"),
            (4, "⭐⭐⭐⭐ Very Good"),
            (3, "⭐⭐⭐ Good"),
            (2, "⭐⭐ Fair"),
            (1, "⭐ Poor"),
        ]

class ServiceBasicInfoForm(forms.ModelForm):
    title = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g., Emergency Plumbing Repair"}),
        label="Service Title"
    )
    category = forms.ChoiceField(
        choices=CATEGORY_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Category"
    )
    price_type = forms.ChoiceField(
        choices=PRICE_TYPE_CHOICES,
        widget=forms.RadioSelect(attrs={"class": "modal-radio-input"}), 
        initial="hourly",
        label="Pricing Type"
    )
    
    hourly_rate = forms.DecimalField(
        max_digits=8, decimal_places=2, required=False,
        widget=forms.NumberInput(attrs={"class": "modal-currency-field", "placeholder": "0.00"}),
        label="Hourly Rate"
    )
    fixed_price = forms.DecimalField(
        max_digits=8, decimal_places=2, required=False,
        widget=forms.NumberInput(attrs={"class": "modal-currency-field", "placeholder": "0.00"}),
        label="Fixed Price"
    )

    class Meta:
        model = Service
        fields = ["title", "category", "price_type", "hourly_rate", "fixed_price"]

    def clean(self):
        cleaned_data = super().clean()
        price_type = cleaned_data.get("price_type")
        hourly_rate = cleaned_data.get("hourly_rate")
        fixed_price = cleaned_data.get("fixed_price")

        if price_type == "hourly" and not hourly_rate:
            self.add_error('hourly_rate', "Hourly rate is required for hourly pricing")
        if price_type == "fixed" and not fixed_price:
            self.add_error('fixed_price', "Fixed price is required for fixed pricing")
        
        return cleaned_data


class ServiceDetailsForm(forms.ModelForm):
    description = forms.CharField(
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Describe what you offer..."}),
        label="Description"
    )
    image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={"class": "file-input-hidden", "accept": "image/*"}),
        label="Service Image"
    )
    features = forms.MultipleChoiceField(
        choices=ServiceForm.SERVICE_FEATURES, 
        widget=forms.CheckboxSelectMultiple(attrs={"class": "checkbox-input"}),
        required=False,
        label="Key Features"
    )

    class Meta:
        model = Service
        fields = ["description", "image", "features"]


class ServiceLocationForm(forms.ModelForm):
    availability = forms.ChoiceField(
        choices=AVAILABILITY_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Availability"
    )
    travel_fee = forms.DecimalField(
        max_digits=6,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={"class": "modal-currency-field", "placeholder": "0.00"}),
        label="Travel Fee"
    )
    region = forms.ChoiceField(
        choices=REGION_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"}), # Or custom widget for multiselect if single region isn't enough, but model says CharField
        label="Service Region"
    )
    materials_included = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "checkbox-input"}),
        label="Materials included"
    )

    class Meta:
        model = Service
        fields = ["availability", "travel_fee", "region", "materials_included"]
