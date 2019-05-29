from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.forms import ModelForm

from .models import GearItem, Category, Manufacturer, PackingList, PackingListGearItemRelation

# Create your views here.
class GearItemForm(ModelForm):
    class Meta:
        model = GearItem
        fields = ['name', 'category', 'manufacturer', 'minWeight', 'maxWeight', 'isPublic']

class PackingListForm(ModelForm):
    class Meta:
        model = PackingList
        fields = ['name', 'comment', 'destination', 'tripStart', 'tripEnd']

def index(request):
    return HttpResponse("Hello World! Youre at the index")

def showItem(request, item_id, allow_edit=False):
    if item_id is not None:
        try:
            item = GearItem.objects.get(pk=item_id)
        except GearItem.DoesNotExist:
            raise Http404("Item does not exist")
    else:
        item = None

    return render(request, 'gear/detail.html', { 'item' : item, 'allowEdit' : allow_edit, 'isPublic' : False } )

def saveItem(request):
    f = GearItemForm(request.POST)
    item = f.save()
    return showItem(request, item.id, False)

def editItem(request, item_id):
    item = GearItem.objects.get(pk = item_id)
    form = GearItemForm(item)
    return render(request, 'gear/editForm.html', { 'form' : form, 'saveUrl' : 'saveItem' })

def createItem(request):
    item = GearItem()
    return showItem(request, item.id, True)

def listPublicItems(request):
    items = GearItem.objects.filter(isPublic = True)
    return render(request, 'gear/list.html', { 'isPublic' : True, 'items' : items })

def listPersonalItems(request):
    items = GearItem.objects.filter(gearownership__owner_id = request.user.id)
    return render(request, 'gear/list.html', { 'isPublic' : False, 'items' : items })

def showByCategory(request, category_id, is_public):
    category = Category.objects.get(pk=category_id)
    items = filter(lambda item: item.is_in_category(category), GearItem.objects.all())
    return render(request, 'gear/list.html', { 'isPublic' : is_public, 'items' : items, 'category' : category})

def listLists(request):
    lists = PackingList.objects.filter(owner = request.user)
    return render(request, 'gear/packinglistOverview.html', { 'lists' : lists })

def editPackingList(request, list_id):
    if list_id is not None:
        try:
            packing_list = PackingList.objects.get(pk = list_id)
            form = PackingListForm(packing_list)
            title = packing_list.name
        except PackingList.DoesNotExist:
            raise Http404("Packing list not found")
    else:
        form = PackingListForm()
        title = "Neue Packliste"

    return render(request, 'gear/editForm.html', { 'title' : title, 'form' : form, 'saveUrl' : 'savePackingList'})

def savePackingList(request):
    packing_list = PackingListForm(request.POST).save(commit = False)
    packing_list.owner = request.user
    packing_list.save()
    return listLists(request)

def createPackingList(request):
    packing_list = PackingList()
    return editPackingList(request, None)

def deletePackingList(request):

    return listLists(request)

def savePackingListPacked(request):
    return showPackingList(request, list_id)

def addItemToList(request, list_id):
    packing_list = PackingList.objects.get(pk = list_id)
    item_id = request.POST.get("itemId", "")
    item = GearItem.objects.get(pk = item_id)

    PackingListGearItemRelation(packinglist = packing_list, item = item).save()

    return showPackingList(request, list_id)

def removeItemFromList(request, list_id):
    return showPackingList(request, list_id)

def saveCardinality(request, list_id):
    rel_id = request.POST.get('relationId', '')
    relation = PackingListGearItemRelation.objects.get(pk = rel_id)
    count = request.POST.get('count', '')
    relation.count = count
    relation.save()

    return showPackingList(request, list_id)

def showPackingList(request, list_id):
    try:
        packing_list = PackingList.objects.get(pk = list_id)
    except PackingList.DoesNotExist:
        raise Http404("No packinglist with this ID")

    items = GearItem.objects.filter(gearownership__owner_id = request.user.id)
    relations = PackingListGearItemRelation.objects.filter(packinglist_id = packing_list.id)

    return render(request, 'gear/showPackingList.html', { 'packing_list' : packing_list, 'relations' : relations, 'possibleItems' : items})

