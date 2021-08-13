from django.urls import path
from . views import AddProductView, FetchProductList, ManageStockView, ProductListView

app_name = 'products'

urlpatterns = [
    # Static urls
    path('product-list/', ProductListView.as_view(), name='product-list'),
    path('add-product/', AddProductView.as_view(), name='add-product'),
    path('manage-stock/', ManageStockView.as_view(), name='manage-stock'),

    # AJAX/ REST urls
    path('fetch-product-list/', FetchProductList.as_view(), name='fetch-product-list'),
]