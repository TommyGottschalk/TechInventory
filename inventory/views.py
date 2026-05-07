#from django.contrib.sites import requests
from django.shortcuts import render, redirect
#import inventory
#from django.views import generic
from .models import Category, ProductModel, Inventory, Request
from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from .forms import UserAddForm, UserEditForm, RequestEditForm, SignUpForm, InventoryEditForm
from django.db import IntegrityError
#from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from datetime import datetime, date

# Create your views here.
def index(request):
    inventory_list = Inventory.objects.all().order_by('serial_number')

    categories = Category.objects.all()
    manufacturers = ProductModel.objects.values_list('manufacturer', flat=True).distinct()

    category = request.GET.get('category')
    manufacturer = request.GET.get('manufacturer')
    available = request.GET.get('available')
    storage_size = request.GET.get('storage_size')


    if category:
        inventory_list = inventory_list.filter(product_model__category__category_name=category)
    
    if manufacturer:
        inventory_list = inventory_list.filter(product_model__manufacturer=manufacturer)

    if storage_size:
        inventory_list = inventory_list.filter(storage_size=storage_size)
    
    if available == "yes":
        inventory_list = inventory_list.filter(is_available=True)
    elif available == "no":
        inventory_list = inventory_list.filter(is_available=False)

    active_requests = Request.objects.filter(
        status='approved',
        actual_return_date__isnull=True)

    loaned_users = {
        req.inventory.serial_number: req.user.username
        for req in active_requests}

    for item in inventory_list:
        item.loaned_user = loaned_users.get(
            item.serial_number,
            "Available" if item.is_available else "Unavailable")

    context = {
        'inventory_list': inventory_list,
        'categories': categories,
        'manufacturers': manufacturers,
        'category': category,
        'manufacturer': manufacturer,
        'storage_size': storage_size,
        'available': available,
        'loaned_users': loaned_users,
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
    if request.method == 'POST':
        request_id = request.POST.get('loans')

        if request_id:
            loan = get_object_or_404(
                Request,
                id=request_id,
                user=request.user,
                status='approved',
                actual_return_date__isnull=True
            )

            loan.status = 'returned'
            loan.actual_return_date = date.today()
            loan.save()

            loan.inventory.is_available = True
            loan.inventory.save()

        return redirect('return_page')

    approved_loans = Request.objects.filter(
        user = request.user,
        status = 'approved',
        actual_return_date__isnull = True
    )

    user_requests = Request.objects.filter(user=request.user).exclude(status__in=['returned', 'denied'])

    active_requests = Request.objects.exclude(status='returned')
    return_dates1 = active_requests.values_list(
        'return_date', flat=True).distinct().order_by('return_date')

    return_dates = []
    for d in return_dates1:
        return_dates.append({
            'value': d.strftime('%Y-%m-%d'),
            'label': d.strftime('%B %d, %Y'),
        })

    context = {
        'approved_loans': approved_loans,
        'user_requests': user_requests,
        'return_dates': return_dates,
    }

    return render(request, 'inventory/return_page.html', context=context)

def manage_page(request):
    if request.method == 'POST':
        request_id = request.POST.get('request_id')
        action = request.POST.get('action')

        req = Request.objects.get(id=request_id)

        if action == 'approve':
            req.status = 'approved'
            req.save()

        elif action == 'deny':
            req.status = 'denied'
            req.save()

            req.inventory.is_available = True
            req.inventory.save()

        return redirect('manage_page')

    active_requests = Request.objects.exclude(status='returned')

    users = User.objects.all().order_by('username')
    username = request.GET.get('username')
    return_date = request.GET.get('return_date')

    if username:
        active_requests = active_requests.filter(user__username=username)

    return_dates1 = active_requests.values_list(
        'return_date', flat=True).distinct().order_by('return_date')

    return_dates = []
    for d in return_dates1:
        return_dates.append({
            'value': d.strftime('%Y-%m-%d'),
            'label': d.strftime('%B %d, %Y'),
        })

    if return_date:
        filter_return_date = datetime.strptime(return_date, '%Y-%m-%d').date()
        active_requests = active_requests.filter(return_date=filter_return_date)

    context = {
        'active_requests': active_requests,
        'users': users,
        'username': username,
        'return_date': return_date,
        'return_dates': return_dates,
    }

    return render(request, 'inventory/manage_page.html', context=context)

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


def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  
            return redirect("index")
    else:
        form = SignUpForm()

    return render(request, "registration/signup.html", {"form": form})

def request_update(request, pk):
    req = get_object_or_404(Request, pk=pk)

    if request.method == 'POST':
        form = RequestEditForm(request.POST, instance=req)
        if form.is_valid():
            updated_request = form.save()

            if updated_request.status == 'returned' or updated_request.status == 'denied':
                updated_request.inventory.is_available = True
                updated_request.inventory.save()
            elif updated_request.status == 'approved':
                updated_request.inventory.is_available = False
                updated_request.inventory.save()

            messages.success(request, "Request has been updated successfully.")
            return redirect('manage_page')
    else:
        form = RequestEditForm(instance=req)

    context = {
        'form': form,
        'req': req,
    }

    return render(request, 'inventory/request_form.html', context)

def inventory_admin(request):
    inventory_list = Inventory.objects.all().order_by('serial_number')

    context = {
        'inventory_list': inventory_list,
    }

    return render(request, 'inventory/inventory_list.html', context)

def inventory_update(request, pk):
    item = get_object_or_404(Inventory, pk=pk)

    if request.method == 'POST':
        form = InventoryEditForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, "Inventory item has been updated successfully.")
            return redirect('inventory_admin')
    else:
        form = InventoryEditForm(instance=item)

    context = {
        'form': form,
        'item': item,
    }

    return render(request, 'inventory/inventory_form.html', context)


def inventory_delete(request, pk):
    item = get_object_or_404(Inventory, pk=pk)

    try:
        serial_number = item.serial_number
        item.delete()
        messages.success(request, serial_number + " has been deleted.")
    except IntegrityError:
        messages.success(request, item.serial_number + " cannot be deleted.")

    return redirect('inventory_admin')