import datetime
from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User

# Create your models here.
class Manufacturer(models.Model):
    name = models.CharField(max_length = 40, unique = True)

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length = 40)
    parent = models.ForeignKey('self', on_delete = models.CASCADE, null = True, blank = True)

    class Meta:
        unique_together = ['name', 'parent']

    def __str__(self):
        if self.parent == None:
            return self.name
        else:
            return f"{self.parent} > {self.name}"

    def is_subcategory(self, other):
        if self.id == other.id:
            return True
        elif self.parent is None:
            return False
        else:
            return self.parent.is_subcategory(other)

class GearItem(models.Model):
    name = models.CharField(max_length = 70)
    manufacturer = models.ForeignKey(Manufacturer, on_delete = models.CASCADE)
    comment = models.TextField(null = True, blank = True)
    category = models.ForeignKey(Category, on_delete = models.CASCADE, null = False)
    minWeight = models.FloatField(null = False)
    maxWeight = models.FloatField(null = True, blank = True)
    purchaseDate = models.DateField(null = True, blank = True)
    isPublic = models.BooleanField()

    def __str__(self):
        return f"{self.name} ({self.manufacturer})"

    def is_in_category(self, category):
        return self.category.is_subcategory(category)

class GearOwnership(models.Model):
    owner = models.ForeignKey(User, on_delete = models.CASCADE)
    ownedItem = models.ForeignKey(GearItem, on_delete = models.CASCADE)

    class Meta:
        unique_together = ['owner', 'ownedItem']

    def __str__(self):
        return f"{self.owner} owns {self.ownedItem}"

class PackingList(models.Model):
    name = models.CharField(max_length = 70)
    comment = models.TextField(null = True, blank = True)
    tripStart = models.DateField(null = True, blank = True)
    tripEnd = models.DateField(null = True, blank = True)
    destination = models.CharField(max_length = 100, null = True, blank = True)
    creationDate = models.DateField(default = datetime.date.today)
    owner = models.ForeignKey(User, on_delete = models.CASCADE)

    class Meta:
        unique_together = ['name', 'owner']

    def __str__(self):
        return f"{self.name} by {self.owner}"

class GearItemGroup(models.Model):
    name = models.CharField(max_length = 70)

    def __str__(self):
        return self.name

class PackingListGearItemRelation(models.Model):
    packinglist = models.ForeignKey(PackingList, on_delete = models.CASCADE)
    item = models.ForeignKey(GearItem, on_delete = models.CASCADE)
    count = models.IntegerField(default = 1, validators = [MinValueValidator(1)])
    isPacked = models.BooleanField(default = False)
    addedByGroup = models.ForeignKey(GearItemGroup, on_delete = models.CASCADE, blank = True, null = True)

    class Meta:
        unique_together = ['packinglist', 'item']

    def __str__(self):
        return f"{self.packinglist} contains {self.count} item(s) {self.item}"

class GearItemGroupOwnership(models.Model):
    owner = models.ForeignKey(User, on_delete = models.CASCADE)
    ownedGroup = models.ForeignKey(GearItemGroup, on_delete = models.CASCADE)

    class Meta:
        unique_together = ['owner', 'ownedGroup']

    def __str__(self):
        return f"{self.owner} owns {self.ownedGroup}"

class GearItemGroupRelation(models.Model):
    group = models.ForeignKey(GearItemGroup, on_delete = models.CASCADE)
    item = models.ForeignKey(GearItem, on_delete = models.CASCADE)

    class Meta:
        unique_together = ['group', 'item']

    def __str__(self):
        return f"{self.group} contains {self.item}"

