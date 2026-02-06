from django.contrib import admin
from .models import *


admin.site.register(UserProfile)
admin.site.register(CustomerProfile)
admin.site.register(CraftsmanProfile)
admin.site.register(Service)
admin.site.register(BoostRequest)
admin.site.register(WaitingList)
admin.site.register(Review)
