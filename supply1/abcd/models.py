
from django.db import models

from django.contrib.auth.models import AbstractUser

class NewUser(AbstractUser):
    USER_TYPE_CHOICES = [
        ('supplier', 'Supplier'),
        ('logistic_partner', 'Logistic Partner'),
        ('customer', 'Customer'),
    ]

    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    contact_no = models.CharField(max_length=15, unique=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)


    def __str__(self):
        return self.username



# models.py

class Warehouse(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100)
    sku = models.CharField(max_length=50, unique=True)
    quantity = models.PositiveIntegerField()
    restock_threshold = models.PositiveIntegerField()
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    supplier = models.ForeignKey(NewUser, on_delete=models.SET_NULL, null=True, limit_choices_to={'user_type': 'supplier'})

    def needs_restock(self):
        return self.quantity < self.restock_threshold



from django.utils import timezone

from django.db import models

class StockMovement(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    movement_type = models.CharField(max_length=10, choices=[('in', 'In'), ('out', 'Out'), ('adjust', 'Adjust')])
    quantity = models.PositiveIntegerField()
    reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} - {self.movement_type} - {self.quantity}"


class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
    ]

    order_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(NewUser, on_delete=models.CASCADE, limit_choices_to={'user_type': 'customer'}, related_name='orders')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    order_date = models.DateTimeField(default=timezone.now)
    order_status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Order {self.order_id} - {self.customer.full_name}"

class Shipment(models.Model):
    SHIPMENT_STATUS_CHOICES = [
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('delayed', 'Delayed'),
    ]

    shipment_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='shipments')
    logistics_partner = models.ForeignKey(NewUser, on_delete=models.SET_NULL, null=True, limit_choices_to={'user_type': 'logistic_partner'}, related_name='shipments')
    tracking_number = models.CharField(max_length=50, unique=True)
    shipment_status = models.CharField(max_length=20, choices=SHIPMENT_STATUS_CHOICES, default='in_transit')
    estimated_delivery = models.DateTimeField()
    current_location = models.CharField(max_length=200, blank=True, null=True)  # For GPS tracking simulation

    def __str__(self):
        return f"Shipment {self.tracking_number} - Order {self.order.order_id}"

class PaymentTransaction(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
    ]
    PAYMENT_METHOD_CHOICES = [
        ('credit_card', 'Credit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('upi', 'UPI'),
    ]

    transaction_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_date = models.DateTimeField(null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Transaction {self.transaction_id} - Order {self.order.order_id}"