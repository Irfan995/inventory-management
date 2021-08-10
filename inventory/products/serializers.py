from rest_framework import fields, serializers
from core.models import Product, ProductType, StockManagement, ProductManagement


class ProductSerializer(serializers.Serializer):
    class Meta:
        model = Product
        fields = ['id', 'product_name', 'product_code', 'category', 'type', 'asset', 'stock_management', 'product_management']
        depth = 1