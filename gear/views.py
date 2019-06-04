from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from django.forms import ModelForm
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from .models import GearItem, GearOwnership, Category, Manufacturer, PackingList, PackingListGearItemRelation

# Create your views here.
class GearItemForm(ModelForm):
    class Meta:
        model = GearItem
        fields = ['name', 'category', 'manufacturer', 'minWeight', 'maxWeight', 'isPublic']

class PackingListForm(ModelForm):
    class Meta:
        model = PackingList
        fields = ['name', 'comment', 'destination', 'tripStart', 'tripEnd']

class GearItemDetailView(DetailView):
    model = GearItem
    context_object_name = 'item'

class GearItemCreateView(CreateView):
    model = GearItem
    form_class = GearItemForm
    success_url = reverse_lazy('listPersonalItems')

    def form_valid(self, form):
        self.object = form.save()

        ownership = GearOwnership(owner = self.request.user, ownedItem = self.object)
        ownership.save()

        return redirect(self.get_success_url())

class GearItemUpdateView(UpdateView):
    model = GearItem
    form_class = GearItemForm

    def get_success_url(self):
        return reverse_lazy('showItem', args=(self.object.id,))

class PackingListListView(ListView):
    model = PackingList

class PackingListCreateView(CreateView):
    model = PackingList
    form_class = PackingListForm

    def form_valid(self, form):
        self.object = form.save(commit = False)
        self.object.owner_id = self.request.user.id
        self.object.save()
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('showPackingList', args=(self.object.id,))

class PackingListDeleteView(DeleteView):
    model = PackingList
    success_url = reverse_lazy('listLists')

def listPublicItems(request):
    items = GearItem.objects.filter(isPublic = True)
    return render(request, 'gear/gearitem_list.html', { 'isPublic' : True, 'items' : items })

def listPersonalItems(request):
    items = GearItem.objects.filter(gearownership__owner_id = request.user.id)
    return render(request, 'gear/gearitem_list.html', { 'isPublic' : False, 'items' : items })

def showByCategory(request, category_id, is_public):
    category = Category.objects.get(pk=category_id)
    items = filter(lambda item: item.is_in_category(category), GearItem.objects.all())
    return render(request, 'gear/list.html', { 'isPublic' : is_public, 'items' : items, 'category' : category})

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

def savePackingListPacked(request):
    print(list(request.POST.items()))
    list_id = request.POST.get("listId", None)
    if list_id is None:
        raise Http404("Packliste wurde nicht gefunden")

    checked_ids = [int(i) for i in request.POST.getlist("isPacked", [])]
    
    for rel in PackingListGearItemRelation.objects.filter(packinglist_id = list_id):
        checked = rel.id in checked_ids 

        if rel.isPacked != checked:
            rel.isPacked = checked
            rel.save()

    return redirect('showPackingList', list_id)

def addItemToList(request, list_id):
    packing_list = PackingList.objects.get(pk = list_id)
    item_id = request.POST.get("itemId", "")
    item = GearItem.objects.get(pk = item_id)

    PackingListGearItemRelation(packinglist = packing_list, item = item).save()

    return redirect('showPackingList', list_id)

def removeItemFromList(request, list_id):
    rel_id = request.POST.get('relationId', '')
    relation = PackingListGearItemRelation.objects.get(pk = rel_id)
    relation.delete()

    return redirect('showPackingList', list_id)

def saveCardinality(request, list_id):
    rel_id = request.POST.get('relationId', '')
    relation = PackingListGearItemRelation.objects.get(pk = rel_id)
    count = request.POST.get('count', '')
    relation.count = count
    relation.save()

    return redirect('showPackingList', list_id)

class PackingListDetailView(DetailView):
    model = PackingList

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['possibleItems'] = GearItem.objects.filter(gearownership__owner_id = self.request.user.id)
        context['relations'] = PackingListGearItemRelation.objects.filter(packinglist_id = self.object.id)
        return context

