from django.contrib import admin
from .models import GearItem, Manufacturer, Category, GearOwnership, PackingList, PackingListGearItemRelation

# Register your models here.
admin.site.register(GearItem)
admin.site.register(Manufacturer)
admin.site.register(Category)
admin.site.register(GearOwnership)
admin.site.register(PackingList)
admin.site.register(PackingListGearItemRelation)

