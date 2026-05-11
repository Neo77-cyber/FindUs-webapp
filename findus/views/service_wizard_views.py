"""
Service creation wizard views
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from formtools.wizard.views import SessionWizardView
import os
import logging

from django import forms
from ..models import Service
from ..selectors import get_craftsman_profile

logger = logging.getLogger(__name__)

# Setup temp storage for wizard files
WIZARD_TEMP_DIR = os.path.join(settings.MEDIA_ROOT, "wizard_temp")
os.makedirs(WIZARD_TEMP_DIR, exist_ok=True)
temp_storage = FileSystemStorage(location=WIZARD_TEMP_DIR)


# STEP 1: Basic Service Info
class Step1BasicAdForm(forms.Form):
    """Basic service information"""

    title = forms.CharField(
        max_length=100,
        label="Service Title",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "e.g., Professional Wall Painting",
            }
        ),
        help_text="Make it clear and attractive to customers",
    )

    category = forms.ChoiceField(
        choices=[
            ("", "Choose a category"),
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
        ],
        label="Category",
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    description = forms.CharField(
        label="Description",
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": "4",
                "placeholder": "Describe your service...\nExample: I provide professional painting services with high-quality materials.",
            }
        ),
        help_text="Tell customers what you do and why they should choose you",
    )

    image = forms.ImageField(
        required=False,
        label="Photo of Your Work",
        widget=forms.FileInput(
            attrs={"class": "file-input-hidden", "accept": "image/*"}
        ),
        help_text="Upload one photo showing your best work",
    )


# STEP 2: Location & Pricing
class Step2LocationMoneyForm(forms.Form):
    """Location and pricing information"""

    region = forms.ChoiceField(
        choices=[
            ("", "Select your service region"),
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
            ("trentino_south_tyrol", "Trentino-South Tyrol"),
            ("tuscany", "Tuscany (Toscana)"),
            ("umbria", "Umbria"),
            ("veneto", "Veneto"),
        ],
        label="Where do you work?",
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    price_type = forms.ChoiceField(
        choices=[
            ("hourly", "Hourly Rate"),
            ("fixed", "Fixed Price"),
        ],
        label="How do you charge?",
        widget=forms.RadioSelect,
        initial="hourly",
    )

    hourly_rate = forms.DecimalField(
        required=False,
        max_digits=8,
        decimal_places=2,
        label="Hourly Rate",
        widget=forms.NumberInput(
            attrs={
                "class": "modal-currency-field",
                "placeholder": "0.00",
                "step": "0.01",
            }
        ),
        help_text="€ per hour",
    )

    fixed_price = forms.DecimalField(
        required=False,
        max_digits=8,
        decimal_places=2,
        label="Fixed Price",
        widget=forms.NumberInput(
            attrs={
                "class": "modal-currency-field",
                "placeholder": "0.00",
                "step": "0.01",
            }
        ),
        help_text="Total € for the job",
    )

    estimated_duration = forms.CharField(
        max_length=100,
        required=False,
        label="Estimated Time",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "e.g., 2-3 hours, Half day, Full day",
            }
        ),
        help_text="For hourly jobs: estimated time needed",
    )

    travel_fee = forms.DecimalField(
        required=False,
        max_digits=6,
        decimal_places=2,
        label="Travel Fee (Optional)",
        widget=forms.NumberInput(
            attrs={
                "class": "modal-currency-field",
                "placeholder": "0.00",
                "step": "0.01",
            }
        ),
        help_text="Only if you want to charge for travel",
    )

    def clean(self):
        """Validate that appropriate price field is filled"""
        cleaned_data = super().clean()
        price_type = cleaned_data.get("price_type")
        hourly_rate = cleaned_data.get("hourly_rate")
        fixed_price = cleaned_data.get("fixed_price")

        if price_type == "hourly" and not hourly_rate:
            raise forms.ValidationError("Please enter an hourly rate")

        if price_type == "fixed" and not fixed_price:
            raise forms.ValidationError("Please enter a fixed price")

        return cleaned_data


# STEP 3: Availability
class Step3FinishLineForm(forms.Form):
    """Availability and final details"""

    availability = forms.ChoiceField(
        choices=[
            ("immediate", "Immediately Available"),
            ("24_hours", "Within 24 Hours"),
            ("48_hours", "Within 48 Hours"),
            ("scheduled", "By Appointment Only"),
        ],
        label="How fast can you show up?",
        widget=forms.Select(attrs={"class": "form-control"}),
        initial="immediate",
    )

    materials_included = forms.BooleanField(
        required=False, label="Materials included in price", initial=False
    )


class ServiceWizardView(SessionWizardView):
    """Multi-step service creation wizard"""

    template_name = "service_wizard_page.html"
    file_storage = temp_storage

    form_list = [Step1BasicAdForm, Step2LocationMoneyForm, Step3FinishLineForm]

    def dispatch(self, request, *args, **kwargs):
        """Ensure user has craftsman profile"""
        if not request.user.is_authenticated:
            return redirect("signin")

        craftsman_profile = get_craftsman_profile(request.user)
        if not craftsman_profile:
            messages.error(request, "Please complete your craftsman profile first")
            return redirect("craftsman_dashboard")

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, form, **kwargs):
        """Add step information to context"""
        context = super().get_context_data(form=form, **kwargs)

        current_step = int(self.steps.current) + 1
        step_titles = {1: "The Basic Ad", 2: "Location & Money", 3: "Finish Line"}

        context.update(
            {
                "current_step": current_step,
                "total_steps": len(self.form_list),
                "step_title": step_titles.get(current_step, f"Step {current_step}"),
                "progress_percent": (current_step / len(self.form_list)) * 100,
            }
        )

        return context

    def done(self, form_list, **kwargs):
        """Process all form data and create service"""

        try:
            # Collect all form data
            form_data = {}
            image_file = None

            for i, form in enumerate(form_list):
                if form.is_valid():
                    cleaned_data = form.cleaned_data.copy()

                    # Handle image from step 0
                    if i == 0 and "image" in cleaned_data and cleaned_data["image"]:
                        image_file = cleaned_data["image"]
                        cleaned_data.pop("image")

                    form_data.update(cleaned_data)

            # Get craftsman profile
            craftsman_profile = get_craftsman_profile(self.request.user)

            if not craftsman_profile:
                raise Exception("Craftsman profile not found")

            # Determine prices based on type
            if form_data["price_type"] == "hourly":
                hourly_rate = form_data.get("hourly_rate")
                fixed_price = None
            else:
                hourly_rate = None
                fixed_price = form_data.get("fixed_price")

            # Create service
            service = Service.objects.create(
                craftsman=craftsman_profile,
                title=form_data["title"],
                category=form_data["category"],
                region=form_data["region"],
                description=form_data["description"],
                price_type=form_data["price_type"],
                hourly_rate=hourly_rate,
                fixed_price=fixed_price,
                estimated_duration=form_data.get("estimated_duration", ""),
                availability=form_data["availability"],
                job_size="medium",  # Default
                materials_included=form_data.get("materials_included", False),
                travel_fee=form_data.get("travel_fee"),
                features=[],
                service_status="Active",
            )

            # Handle image upload
            if image_file:
                service.image = image_file
                service.save()

            logger.info(
                f"Service created: {service.id} by {craftsman_profile.business_name}"
            )

        except Exception as e:
            logger.error(f"Error creating service: {e}", exc_info=True)
            messages.error(self.request, "Failed to create service. Please try again.")

        # Clear wizard session
        try:
            self.storage.reset()
        except:
            pass

        return redirect("craftsman_dashboard")


# Decorator to protect the wizard view
service_wizard_view = login_required(ServiceWizardView.as_view(), login_url="signin")
