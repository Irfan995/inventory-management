from django.contrib import admin
from django.contrib.auth import get_user_model
from core.models import Product, StockManagement, ProductManagement, ProductType

# Register your models here.
UserProfile = get_user_model()
admin.site.register(UserProfile)
admin.site.register(Product)
admin.site.register(StockManagement)
admin.site.register(ProductManagement)
admin.site.register(ProductType)
