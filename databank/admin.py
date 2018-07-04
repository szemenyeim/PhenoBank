from django.contrib import admin

# Register your models here.
from .models import Location, Species, Individual, Subspecies, Option, Property_base, Property, Profile, Image

admin.site.register(Location)
admin.site.register(Species)
admin.site.register(Subspecies)
admin.site.register(Option)
admin.site.register(Property_base)
admin.site.register(Property)
admin.site.register(Individual)
admin.site.register(Profile)
admin.site.register(Image)