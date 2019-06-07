from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(GearItem)
admin.site.register(Manufacturer)
admin.site.register(Category)
admin.site.register(GearOwnership)
admin.site.register(PackingList)
admin.site.register(PackingListGearItemRelation)
admin.site.register(GearItemGroup)
admin.site.register(GearItemGroupRelation)
admin.site.register(GearItemGroupOwnership)

