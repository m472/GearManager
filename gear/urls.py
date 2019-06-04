from django.urls import path

from . import views

urlpatterns = [
    path('items/show/<int:pk>', views.GearItemDetailView.as_view(), name = 'showItem'), 
    path('items/edit/<int:pk>', views.GearItemUpdateView.as_view(), name = 'editItem'),
    path('items/create', views.GearItemCreateView.as_view(), name = 'createItem'),
    path('items/save/<int:pk>', views.GearItemUpdateView.as_view(), name = 'saveItem'),
    path('items/listPublic', views.listPublicItems, name = 'listPublicItems'),
    path('items/listPersonal', views.listPersonalItems, name = 'listPersonalItems'),
    path('items/showByCategory/<int:category_id>&<str:is_public>', views.showByCategory, name = 'showByCategory'),
    path('lists/list', views.PackingListListView.as_view(), name = 'listLists'),
    path('lists/create', views.PackingListCreateView.as_view(), name = 'createList'),
    path('lists/edit/<int:pk>', views.editPackingList, name = 'editPackingList'),
    path('lists/save', views.savePackingList, name = 'savePackingList'),
    path('lists/show/<int:pk>', views.PackingListDetailView.as_view(), name = 'showPackingList'),
    path('lists/delete/<int:pk>', views.PackingListDeleteView.as_view(), name = 'deletePackingList'),
    path('lists/saveItems', views.savePackingListPacked, name = 'savePacked'),
    path('lists/addItem/<int:list_id>', views.addItemToList, name = 'addItem'),
    path('lists/removeItem/<int:list_id>', views.removeItemFromList, name = 'removeItem'),
    path('lists/saveCardinality/<int:list_id>', views.saveCardinality, name = 'saveCardinality'),
]
