from django.urls import path, register_converter

from . import views, converters

register_converter(converters.BooleanConverter, 'bool')

urlpatterns = [
    path('items/show/<int:pk>', views.GearItemDetailView.as_view(), name = 'showItem'), 
    path('items/edit/<int:pk>', views.GearItemUpdateView.as_view(), name = 'editItem'),
    path('items/create', views.GearItemCreateView.as_view(), name = 'createItem'),
    path('items/save/<int:pk>', views.GearItemUpdateView.as_view(), name = 'saveItem'),
    path('items/listPublic', views.GearItemListPublic.as_view(), name = 'listPublicItems'),
    path('items/listPersonal', views.GearItemListPersonal.as_view(), name = 'listPersonalItems'),
    path('items/addToListOrGroup', views.addItemToListOrGroup, name = 'addToListOrGroup'),
    path('items/showByCategory/<int:category_id>&<bool:is_public>', views.showByCategory, name = 'showByCategory'),
    path('items/addToPersonal', views.addItemToPersonal, name = 'addItemToPersonal'),
    path('lists/list', views.PackingListListView.as_view(), name = 'listLists'),
    path('lists/create', views.PackingListCreateView.as_view(), name = 'createList'),
    path('lists/edit/<int:pk>', views.PackingListUpdateView.as_view(), name = 'editPackingList'),
    path('lists/show/<int:pk>', views.PackingListDetailView.as_view(), name = 'showPackingList'),
    path('lists/delete/<int:pk>', views.PackingListDeleteView.as_view(), name = 'deletePackingList'),
    path('lists/saveItems', views.savePackingListPacked, name = 'savePacked'),
    path('lists/addItem/<int:list_id>', views.addItemToList, name = 'addItem'),
    path('lists/addGroup/<int:list_id>', views.addGroupToList, name = 'addGroup'),
    path('lists/removeItem/<int:list_id>', views.removeItemFromList, name = 'removeItem'),
    path('lists/saveCardinality/<int:list_id>', views.saveCardinality, name = 'saveCardinality'),
    path('groups/list', views.GearItemGroupListView.as_view(), name = 'listGroups'),
    path('groups/show/<int:pk>', views.GearItemGroupDetailView.as_view(), name = 'showGroup'),
    path('groups/create', views.GearItemGroupCreateView.as_view(), name = 'createGroup'),
    path('groups/removeItem/<int:pk>', views.removeItemFromGroup, name = 'removeItemFromGroup'),
    path('groups/edit/<int:pk>', views.GearItemGroupUpdateView.as_view(), name = 'editGroup'),
    path('groups/delete/<int:pk>', views.GearItemGroupDeleteView.as_view(), name = 'deleteGroup'),
    path('groups/addItem/<int:pk>', views.addItemToGroup, name = 'addItemToGroup'),
]
