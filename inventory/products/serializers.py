from django.db import models
from rest_framework import fields, serializers
from core.models import Product, ProductType, StockManagement, ProductManagement


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'product_name', 'product_code', 'category', 'type', 'asset', 'stock_management', 'product_management']
        depth = 1


class ProductTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductType
        fields = ['id', 'type_name']