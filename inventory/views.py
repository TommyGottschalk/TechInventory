from django.shortcuts import render
#from django.views import generic
from .models import Category, ProductModel, Inventory, Request

# Create your views here.
def index(request):
    inventory_list = Inventory.objects.filter(is_available=True).order_by('serial_number')

    context = {
        'inventory_list': inventory_list,
    }

    return render(request, 'index.html', context=context)

def request_page(request):
    return render(request, 'inventory/request_page.html')

def return_page(request):
    return render(request, 'inventory/return_page.html')

def manage_page(request):
    return render(request, 'inventory/manage_page.html')

def add_page(request):
    return render(request, 'inventory/add_page.html')