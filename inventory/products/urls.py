from django.urls import path
from . views import FetchProductList, ProductListView

app_name = 'products'

urlpatterns = [
    path('product-list/', ProductListView.as_view(), name='product-list'),
    path('fetch-product-list/', FetchProductList.as_view(), name='fetch-product-list')
]