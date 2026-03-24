from django.contrib import admin
from .models import Category, ProductModel, Inventory, Request

# Register your models here.
admin.site.register(Category)
admin.site.register(ProductModel)
admin.site.register(Inventory)
admin.site.register(Request)