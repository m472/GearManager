from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name = 'index'),
    path('items/show/<int:item_id>', views.showItem, name = 'showItem'),
    path('items/edit/<int:item_id>', views.editItem, name = 'editItem'),
    path('items/create', views.createItem, name = 'createItem'),
    path('items/save', views.saveItem, name = 'saveItem'),
    path('items/listPublic', views.listPublicItems, name = 'listPublicItems'),
    path('items/listPersonal', views.listPersonalItems, name = 'listPersonalItems'),
    path('items/showByCategory/<int:category_id>&<str:is_public>', views.showByCategory, name = 'showByCategory'),
    path('lists/list', views.listLists, name = 'listLists'),
    path('lists/createList', views.createPackingList, name = 'createList'),
    path('lists/edit/<int:list_id>', views.editPackingList, name = 'editPackingList'),
    path('lists/save', views.savePackingList, name = 'savePackingList'),
    path('lists/show/<int:list_id>', views.showPackingList, name = 'showPackingList'),
    path('lists/delete', views.deletePackingList, name = 'deletePackingList'),
    path('lists/saveItems', views.savePackingListPacked, name = 'savePacked'),
    path('lists/addItem/<int:list_id>', views.addItemToList, name = 'addItem'),
    path('lists/removeItem/<int:list_id>', views.removeItemFromList, name = 'removeItem'),
    path('lists/saveCardinality/<int:list_id>', views.saveCardinality, name = 'saveCardinality'),
]
