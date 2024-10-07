from django.urls import path
from .views import *

urlpatterns=[
    path('',login_view,name='login'),
    path('order_list',view_orders,name='view_orders'),
     path('table_list',view_table,name='view_tables'),
     path('create_table/',create_table,name='create_table'),
     path('edit_table/<str:pk>/',edit_table,name='edit_table'),
     path('delete_table/<str:pk>/',delete_table,name='delete_table'),
     path('create_order/',create_order,name='create_order'),
     path('order_detail/<str:pk>',order_detail,name='order_detail'),
     path('edit_order/<str:pk>/',edit_order,name='edit_order'),
     path('delete_order/<str:pk>/',delete_order,name='delete_order'),
     path('menu_item_list/',menuitem_list,name='view_menu_item'),
     path('create_menu_item/',create_menu_item,name='create_menu_item'),
     path('edit_menu_item/<str:pk>/',edit_menu_item,name='edit_menu_item'),
     path('delete_menu_item/<str:pk>/',delete_menu_item,name='delete_menu_item'),
     path('create_employee/',create_employee,name="create_employee"),
     path('employee_list',employee_list,name='view_employee'),
     path('employee_detail/<str:pk>',employee_detail,name='employee_detail'),
     path('edit_employee/<str:pk>/',employee_edit,name='edit_employee'),
     path('delete_employee/<str:pk>/',delete_employee,name='delete_employee'),
     path('inventory_list/',view_inventory,name='view_inventory'),
     path('create_inventory/',create_inventory,name='create_inventory'),
     path('edit_inventory/<str:pk>/',edit_inventory,name='edit_inventory'),
     path('delete_inventory/<str:pk>/',delete_inventory,name='delete_inventory'),
     
    
]