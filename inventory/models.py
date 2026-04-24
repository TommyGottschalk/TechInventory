from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    category_name = models.CharField(max_length=100)

    def __str__(self):
        return self.category_name

class ProductModel(models.Model):
    model_name = models.CharField(max_length=100)
    manufacturer = models.CharField(max_length=100)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.manufacturer} {self.model_name}'

class Inventory(models.Model):
    serial_number = models.CharField(max_length=100, primary_key=True)
    is_available = models.BooleanField(default=True)
    storage_size = models.CharField(max_length=50)
    product_model = models.ForeignKey('ProductModel', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.product_model} {self.serial_number}'

class Request(models.Model):
    request_date = models.DateField(auto_now_add=True)
    return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    inventory = models.ForeignKey('Inventory', on_delete=models.CASCADE)
    charger_requested = models.BooleanField(default=False)

    REQUEST_STATUS = (
        ('pending', 'Pending'), ('approved', 'Approved'), ('returned', 'Returned'), ('denied', 'Denied'),
    )

    status = models.CharField(
        max_length=20,
        choices=REQUEST_STATUS,
        default='pending',
        help_text='Request status',
    )

    def __str__(self):
        return f'Request {self.pk} - {self.user}'