from django.urls import path
from . views import AddProductStock, AddProductView, FetchProductCode, FetchProductInformation, ProductList, FetchProductType, ProductTypeList, ManageStockView, ProductListView, ProductTypeListView

app_name = 'products'

urlpatterns = [
    # Static urls
    path('product-list/', ProductListView.as_view(), name='product-list'),
    path('add-product/', AddProductView.as_view(), name='add-product'),
    path('manage-stock/', ManageStockView.as_view(), name='manage-stock'),
    path('product-type-list/', ProductTypeListView.as_view(), name='product-type-list'),

    # AJAX/ REST urls
    path('fetch-product-list/', ProductList.as_view(), name='fetch-product-list'),
    path('fetch-product-type-list/', ProductTypeList.as_view(), name='fetch-product-type-list'),
    path('fetch-product-type/', FetchProductType.as_view(), name='fetch-product-type'),
    path('submit-product/', ProductList.as_view(), name='submit-product'),
    path('fetch-product-code/', FetchProductCode.as_view(), name='fetch-product-code'),
    path('fetch-product-information/', FetchProductInformation.as_view(), name='fetch-product-information'),
    path('submit-product-stock/', AddProductStock.as_view(), name='submit-product-stock'),
]