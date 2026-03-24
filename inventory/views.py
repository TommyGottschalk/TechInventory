from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, 'inventory/index.html')

def request_page(request):
    return render(request, 'inventory/request_page.html')

def return_page(request):
    return render(request, 'inventory/return_page.html')

def manage_page(request):
    return render(request, 'inventory/manage_page.html')

def add_page(request):
    return render(request, 'inventory/add_page.html')