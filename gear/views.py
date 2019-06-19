from django.shortcuts import render, redirect
from django.forms import ModelForm
from django.conf import settings
from django.urls import reverse_lazy
from django.http import HttpResponse, Http404
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required 
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.utils import IntegrityError

from .models import GearItem, GearOwnership, Category, Manufacturer, \
                    PackingList, PackingListGearItemRelation, GearItemGroup, \
                    GearItemGroupRelation, GearItemGroupOwnership

# Create your views here.
class GearItemForm(ModelForm):
    class Meta:
        model = GearItem
        fields = ['name', 'category', 'manufacturer', 'minWeight', 'maxWeight', 'isPublic']

class PackingListForm(ModelForm):
    class Meta:
        model = PackingList
        fields = ['name', 'comment', 'destination', 'tripStart', 'tripEnd']

class GearItemGroupForm(ModelForm):
    class Meta:
        model = GearItemGroup
        fields = ['name']

def assert_single_ownership(obj, user, owner_attr_name = 'owner'):
    if not getattr(obj, owner_attr_name).id == user.id:
        print("assert_single_ownership check failed")
        raise Http404

def assert_multiple_ownership(obj, user, relation_model, owned_object_key_name, owner_key_name = 'owner'):
    relations = relation_model.objects.filter(**{ owned_object_key_name : obj })
    user_ids = relations.values_list(owner_key_name, flat=True)
    if not user.id in user_ids:
        print("assert_multiple_ownership check failed")
        raise Http404

class OwnerRequiredMixin:
    owner_attribute_name = "owner"
    
    def get_owner_ids(self, obj):
        return [getattr(obj, self.owner_attribute_name).id]

    def is_user_authorised(self, obj, user):
        return user.id in self.get_owner_ids(obj)

    def dispatch(self, request, *args, **kwargs):
        obj = self.model.objects.get(pk = kwargs[self.pk_url_kwarg])
        if self.is_user_authorised(obj, request.user):
            return super().dispatch(request, *args, **kwargs)
        else:
            print("OwnerRequiredMixin ownership check failed")
            raise Http404()

class PackingListWeights:
    def __init__(self, relations):
        self.currentMinWeight = 0
        self.currentMaxWeight = 0
        self.totalMinWeight = 0
        self.totalMaxWeight = 0

        for rel in relations:
            minW = rel.count * rel.item.minWeight
            maxW = rel.count * (rel.item.maxWeight or rel.item.minWeight)

            self.totalMinWeight += minW
            self.totalMaxWeight += maxW
            
            if rel.isPacked:
                self.currentMinWeight += minW
                self.currentMaxWeight += maxW

class GearItemDetailView(OwnerRequiredMixin, DetailView):
    model = GearItem
    context_object_name = 'item'

    def get_owner_ids(self, obj):
        return GearOwnership.objects.filter(ownedItem__id = obj.id).values_list('owner', flat=True)

    def is_user_authorised(self, obj, user):
        if obj.isPublic:
            return True
        else:
            return super().is_user_authorised(obj, user)

class GearItemCreateView(LoginRequiredMixin, CreateView):
    model = GearItem
    form_class = GearItemForm
    success_url = reverse_lazy('listPersonalItems')

    def form_valid(self, form):
        self.object = form.save()

        ownership = GearOwnership(owner = self.request.user, ownedItem = self.object)
        ownership.save()

        return redirect(self.get_success_url())

class GearItemUpdateView(LoginRequiredMixin, OwnerRequiredMixin, UpdateView):
    model = GearItem
    form_class = GearItemForm

    def get_success_url(self):
        return reverse_lazy('showItem', args=(self.object.id,))

    def get_owner_ids(self, obj):
        return GearOwnership.objects.filter(ownedItem__id = obj.id).values_list('owner', flat=True)

    def is_user_authorised(self, obj, user):
        if obj.isPublic:
            return True
        else:
            return super().is_user_authorised(obj, user)

class GearItemListPublic(ListView):
    model = GearItem
    queryset = GearItem.objects.filter(isPublic = True)
    template_name_suffix = "_listPublic"

class GearItemListPersonal(LoginRequiredMixin, ListView):
    model = GearItem
    template_name_suffix = "_listPersonal"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['itemGroups'] = GearItemGroup.objects.filter(gearitemgroupownership__owner_id = self.request.user.id)
        context['packinglists'] = PackingList.objects.filter(owner_id = self.request.user.id)
        return context

    def get_queryset(self):
        return GearItem.objects.filter(gearownership__owner_id = self.request.user.id)

def showByCategory(request, category_id, is_public):
    if not is_public and not request.user.is_authenticated:
        return redirect(f'{settings.LOGIN_URL}?next={request.path}')

    category = Category.objects.get(pk=category_id)

    if is_public:
        items = filter(lambda item: item.is_in_category(category), GearItem.objects.filter(isPublic = True))
        return render(request, 'gear/gearitem_listPublic.html', { 'gearitem_list' : items, 'category' : category})
    else:
        items = filter(lambda item: item.is_in_category(category), GearItem.objects.filter(gearownership__owner_id = request.user.id))
        return render(request, 'gear/gearitem_listPersonal.html', { 'gearitem_list' : items, 'category' : category})


class PackingListListView(LoginRequiredMixin, ListView):
    model = PackingList

    def get_queryset(self):
        return PackingList.objects.filter(owner__id = self.request.user.id)

class PackingListCreateView(LoginRequiredMixin, CreateView):
    model = PackingList
    form_class = PackingListForm

    def form_valid(self, form):
        self.object = form.save(commit = False)
        self.object.owner_id = self.request.user.id
        self.object.save()
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('showPackingList', args=(self.object.id,))

class PackingListUpdateView(LoginRequiredMixin, OwnerRequiredMixin, UpdateView):
    model = PackingList
    form_class = PackingListForm
    
    def get_success_url(self):
        return reverse_lazy('showPackingList', args=(self.object.id,))

class PackingListDeleteView(LoginRequiredMixin, OwnerRequiredMixin, DeleteView):
    model = PackingList
    success_url = reverse_lazy('listLists')

class PackingListDetailView(LoginRequiredMixin, OwnerRequiredMixin, DetailView):
    model = PackingList

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['possibleItems'] = GearItem.objects.filter(gearownership__owner_id = self.request.user.id) \
                                                   .exclude(packinglistgearitemrelation__packinglist_id = self.object.id)
        context['groups'] = GearItemGroup.objects.filter(gearitemgroupownership__owner_id = self.request.user.id) 
        relations = PackingListGearItemRelation.objects.filter(packinglist_id = self.object.id)
        context['relations'] = relations
        context['weights'] = PackingListWeights(relations)
        return context

class GearItemGroupListView(LoginRequiredMixin, ListView):
    model = GearItemGroup

    def get_queryset(self):
        return GearItemGroup.objects.filter(gearitemgroupownership__owner_id = self.request.user.id)

class GearItemGroupDetailView(LoginRequiredMixin, OwnerRequiredMixin, DetailView):
    model = GearItemGroup

    def get_owner_ids(self, obj):
        return GearItemGroupOwnership.objects.filter(ownedGroup__id = obj.id).values_list('owner', flat=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['possibleItems'] = GearItem.objects.filter(gearownership__owner_id = self.request.user.id) \
                                                   .exclude(gearitemgrouprelation__group_id = self.object.id)
        context['relations'] = GearItemGroupRelation.objects.filter(group__id = self.object.id)
        return context

class GearItemGroupCreateView(LoginRequiredMixin, CreateView):
    model = GearItemGroup
    form_class = GearItemGroupForm

    def get_success_url(self):
        return reverse_lazy('showGroup', args=(self.object.id,))

    def form_valid(self, form):
        self.object = form.save()

        ownership = GearItemGroupOwnership(owner = self.request.user, ownedGroup = self.object)
        ownership.save()

        return redirect(self.get_success_url())

class GearItemGroupUpdateView(LoginRequiredMixin, OwnerRequiredMixin, UpdateView):
    model = GearItemGroup
    form_class = GearItemGroupForm

    def get_owner_ids(self, obj):
        return GearItemGroupOwnership.objects.filter(ownedGroup__id = obj.id).values_list('owner', flat=True)
    
    def get_success_url(self):
        return reverse_lazy('showGroup', args=(self.object.id,))
    
class GearItemGroupDeleteView(LoginRequiredMixin, OwnerRequiredMixin, DeleteView):
    model = GearItemGroup
    success_url = reverse_lazy('listGroups')

    def get_owner_ids(self, obj):
        return GearItemGroupOwnership.objects.filter(ownedGroup__id = obj.id).values_list('owner', flat=True)

@login_required
def addItemToListOrGroup(request):
    selectedItemIds = request.POST.getlist("itemIds")

    if request.POST.get('addToList'):
        packinglist = PackingList.objects.get(pk = request.POST.get('packinglist'))
        assert_single_ownership(packinglist, request.user)

        for item_id in selectedItemIds:
            item = GearItem.objects.get(pk = item_id)
            assert_multiple_ownership(item, request.user, GearOwnership, 'ownedItem')
            PackingListGearItemRelation(packinglist = packinglist, item = item).save()
        return redirect('showPackingList', args=(packinglist.id,))

    if request.POST.get('addToGroup'):
        group = GearItemGroup.objects.get(pk = request.POST.get('group'))
        assert_multiple_ownership(group, request.user, GearItemGroupOwnership, 'ownedGroup')

        for item_id in selectedItemIds:
            item = GearItem.objects.get(pk = item_id)
            assert_multiple_ownership(item, request.user, GearOwnership, 'ownedItem')
            GearItemGroupRelation(group = group, item = item).save()
        return redirect('showGroup', args=(group.id,))

    raise Http404


@login_required
def addItemToPersonal(request):
    for item_id in request.POST.getlist("addItem"):
        item = GearItem.objects.get(pk = item_id)
        GearOwnership(owner = request.user, ownedItem = item).save()
    
    return redirect('listPersonalItems')

@login_required
def savePackingListPacked(request):
    list_id = request.POST.get("listId", None)
    if list_id is None:
        raise Http404("Packliste wurde nicht gefunden")

    packinglist = PackingList.objects.get(pk = list_id)
    assert_single_ownership(packinglist, request.user)

    checked_ids = [int(i) for i in request.POST.getlist("isPacked", [])]
    
    for rel in PackingListGearItemRelation.objects.filter(packinglist_id = list_id):
        checked = rel.id in checked_ids 

        if rel.isPacked != checked:
            rel.isPacked = checked
            rel.save()

    return redirect('showPackingList', list_id)

@login_required
def addItemToList(request, list_id):
    packing_list = PackingList.objects.get(pk = list_id)
    assert_single_ownership(packing_list, request.user)

    item_id = request.POST.get("itemId", "")
    item = GearItem.objects.get(pk = item_id)
    assert_multiple_ownership(item, request.user, GearOwnership, 'ownedItem')

    PackingListGearItemRelation(packinglist = packing_list, item = item).save()

    return redirect('showPackingList', list_id)

@login_required
def addGroupToList(request, list_id):
    packing_list = PackingList.objects.get(pk = list_id)
    assert_single_ownership(packing_list, request.user)
    group_id = request.POST.get("groupId", "")
    group = GearItemGroup.objects.get(pk = group_id)
    assert_multiple_ownership(group, request.user, GearItemGroupOwnership, 'ownedGroup')

    for relation in GearItemGroupRelation.objects.filter(group__id = group_id):
        try:
            PackingListGearItemRelation(packinglist = packing_list, item = relation.item, addedByGroup = group).save()
        except IntegrityError:
            pass

    return redirect('showPackingList', list_id)

@login_required
def removeItemFromList(request, list_id):
    rel_id = request.POST.get('relationId', '')
    relation = PackingListGearItemRelation.objects.get(pk = rel_id)
    assert_single_ownership(relation.packinglist, request.user)
    relation.delete()

    return redirect('showPackingList', list_id)

@login_required
def saveCardinality(request, list_id):
    rel_id = request.POST.get('relationId', '')
    relation = PackingListGearItemRelation.objects.get(pk = rel_id)
    assert_single_ownership(relation.packinglist, request.user)
    count = request.POST.get('count', '')
    relation.count = count
    relation.save()

    return redirect('showPackingList', list_id)

@login_required
def removeItemFromGroup(request, pk):
    rel_id = request.POST.get('relationId', '')
    relation = GearItemGroupRelation.objects.get(pk = rel_id)
    assert_single_ownership(relation.group, request.user)
    relation.delete()

    return redirect('showGroup', list_id)
