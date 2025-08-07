from django.urls import path
from . import views

app_name = "inventory"

urlpatterns = [
    path('', views.all_products_view, name="all_products_view"),
    path('create/', views.create_product_view, name="create_product_view"),
    path('detail/<int:product_id>/', views.product_detail_view, name="product_detail_view"),
    path('update/<int:product_id>/', views.update_product_view, name="update_product_view"),
    path('delete/<int:product_id>/', views.delete_product_view, name="delete_product_view"),
    path('search/', views.search_products_view, name="search_products_view"),

    path('categories/', views.list_categories_view, name="list_categories_view"),
    path('categories/create/', views.create_category_view, name="create_category_view"),
    path('categories/update/<int:category_id>/', views.update_category_view, name="update_category_view"),
    path('categories/delete/<int:category_id>/', views.delete_category_view, name="delete_category_view"),

    path('suppliers/', views.list_suppliers_view, name="list_suppliers_view"),
    path('suppliers/create/', views.create_supplier_view, name="create_supplier_view"),
    path('suppliers/update/<int:supplier_id>/', views.update_supplier_view, name="update_supplier_view"),
    path('suppliers/delete/<int:supplier_id>/', views.delete_supplier_view, name="delete_supplier_view"),
    path('suppliers/detail/<int:supplier_id>/', views.supplier_detail_view, name="supplier_detail_view"),
]
