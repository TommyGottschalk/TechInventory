from django.shortcuts import render, redirect
#import inventory
#from django.views import generic
from .models import Category, ProductModel, Inventory, Request
from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from .forms import UserAddForm, UserEditForm
from django.db import IntegrityError

# Create your views here.
def index(request):
    inventory_list = Inventory.objects.filter(is_available=True).order_by('serial_number')

    context = {
        'inventory_list': inventory_list,
    }

    return render(request, 'index.html', context=context)

def request_page(request):
    #Data to display on the page
    available_items = Inventory.objects.filter(is_available=True)
    user_requests = Request.objects.filter(user=request.user)

    if request.method == 'POST':
        #Get data from the form
        serial_number = request.POST.get('device')
        return_date = request.POST.get('returnDate')
        charger = request.POST.get('charger') == 'on'

        inventory_item = Inventory.objects.get(serial_number=serial_number)
        #Request in the database
        Request.objects.create(
            user=request.user,
            inventory=inventory_item,
            return_date=return_date,
            charger_requested=charger,
            status='pending'
        )

        inventory_item.is_available = False
        inventory_item.save()

        return redirect('request_page')

    context = {
        'available_items': available_items,
        'user_requests': user_requests,
    }
    return render(request, 'inventory/request_page.html', context)

def return_page(request):
    return render(request, 'inventory/return_page.html')

def manage_page(request):
    return render(request, 'inventory/manage_page.html')

def add_page(request):
    if request.method == 'POST':
        #Extract data from the submitted HTML form
        device_type = request.POST.get('device_type')
        manufacturer = request.POST.get('manufacturer')
        model_name = request.POST.get('model_name')
        serial_number = request.POST.get('serial_number')
        storage_size = request.POST.get('storage_size')

        #Check if the status is set to 'Available'
        is_available = request.POST.get('status') == 'Available'

        #Get or create the Category
        category_obj, created = Category.objects.get_or_create(
            category_name=device_type,
        )

        #Get or create the ProductModel, linking the Category
        product_obj, created = ProductModel.objects.get_or_create(
            model_name=model_name,
            manufacturer=manufacturer,
            category=category_obj,
        )

        #Create the actual Inventory item
        Inventory.objects.create(
            serial_number=serial_number,
            storage_size=storage_size,
            is_available=is_available,
            product_model=product_obj,
        )

        #Redirect to the home page after successfully adding
        return redirect('index')
    #If it's a GET request, just show the empty form
    return render(request, 'inventory/add_page.html')

def user_list(request):
    users_list = User.objects.all().order_by('username')

    context = {
        'user_list': users_list,
    }
    return render(request, 'inventory/user_list.html', context)

def user_create(request):
    if request.method == 'POST':
        form = UserAddForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "User has been created successfully.")
            return redirect('user_list')
    else:
        form = UserAddForm()

    context = {
        'form': form,
    }
    return render(request, 'inventory/user_form.html', context)

def user_update(request, pk):
    user_obj = get_object_or_404(User, pk=pk)

    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user_obj)
        if form.is_valid():
            form.save()
            messages.success(request, "User has been updated successfully.")
            return redirect('user_list')
    else:
        form = UserEditForm(instance=user_obj)

    context = {
        'form': form,
    }
    return render(request, 'inventory/user_form.html', context)

def user_delete(request, pk):
    user_obj = get_object_or_404(User, pk=pk)

    if user_obj.pk == request.user.pk:
        messages.success(request, "You cannot delete your own account.")
        return redirect('user_list')

    try:
        username = user_obj.username
        user_obj.delete()
        messages.success(request, username + " has been deleted.")
    except IntegrityError:
        messages.success(request, user_obj.username + " cannot be deleted.")
    return redirect('user_list')