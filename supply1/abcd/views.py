from django.utils import timezone
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.db.models import F
from .models import NewUser, Order, PaymentTransaction, Product, Shipment, StockMovement, Warehouse
import random
import string

# --- Helper Functions for User Type Checks ---
def is_admin(user):
    return user.is_superuser

def is_supplier(user):
    return user.user_type == 'supplier'

def is_logistic_partner(user):
    return user.user_type == 'logistic_partner'

def is_customer(user):
    return user.user_type == 'customer'

# --- General Views (Accessible to All or Unauthenticated) ---

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect('admin_dashboard')
            elif user.user_type == 'supplier':
                return redirect('supplier_dashboard')
            elif user.user_type == 'logistic_partner':
                return redirect('logistics_dashboard')
            elif user.user_type == 'customer':
                return redirect('index')
            else:
                messages.error(request, "Invalid user type.")
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('user_login')


def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

def services(request):
    return render(request, 'services.html')

# ---======================== Admin Views ---=====================================================

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    context = {
        'suppliers_count': NewUser.objects.filter(user_type='supplier').count(),
        'logistic_partners_count': NewUser.objects.filter(user_type='logistic_partner').count(),
        'orders_count': Order.objects.count(),
        'shipments_count': Shipment.objects.filter(shipment_status='in_transit').count(),
        'recent_orders': Order.objects.order_by('-order_date')[:5],
    }
    return render(request, 'admin1/admin-dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def view_suppliers(request):
    suppliers = NewUser.objects.filter(user_type='supplier')
    return render(request, 'admin1/view_suppliers.html', {'suppliers': suppliers})

@login_required
@user_passes_test(is_admin)
def edit_supplier(request, user_id):
    supplier = get_object_or_404(NewUser, id=user_id, user_type='supplier')
    if request.method == 'POST':
        supplier.full_name = request.POST.get('full_name')
        supplier.email = request.POST.get('email')
        supplier.contact_no = request.POST.get('phone')
        password = request.POST.get('password')
        if password:
            supplier.password = make_password(password)
        supplier.save()
        messages.success(request, "Supplier updated successfully.")
        return redirect('view_suppliers')
    return render(request, 'admin1/edit_supplier.html', {'supplier': supplier})

@login_required
@user_passes_test(is_admin)
def delete_supplier(request, user_id):
    supplier = get_object_or_404(NewUser, id=user_id, user_type='supplier')
    supplier.delete()
    messages.success(request, "Supplier deleted successfully.")
    return redirect('view_suppliers')

@login_required
@user_passes_test(is_admin)
def view_logistic_partners(request):
    logistic_partners = NewUser.objects.filter(user_type='logistic_partner')
    return render(request, 'admin1/view_logistic_partners.html', {'logistic_partners': logistic_partners})

@login_required
@user_passes_test(is_admin)
def edit_logistic_partner(request, user_id):
    partner = get_object_or_404(NewUser, id=user_id, user_type='logistic_partner')
    if request.method == 'POST':
        partner.full_name = request.POST.get('full_name')
        partner.email = request.POST.get('email')
        partner.contact_no = request.POST.get('phone')
        password = request.POST.get('password')
        if password:
            partner.password = make_password(password)
        partner.save()
        messages.success(request, "Logistic Partner updated successfully.")
        return redirect('view_logistic_partners')
    return render(request, 'admin1/edit_logistic_partner.html', {'partner': partner})

@login_required
@user_passes_test(is_admin)
def delete_logistic_partner(request, user_id):
    partner = get_object_or_404(NewUser, id=user_id, user_type='logistic_partner')
    partner.delete()
    messages.success(request, "Logistic Partner deleted successfully.")
    return redirect('view_logistic_partners')

@login_required
@user_passes_test(is_admin)
def add_warehouse(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        location = request.POST.get('location')
        if name and location:
            Warehouse.objects.create(name=name, location=location)
            messages.success(request, 'Warehouse added successfully.')
            return redirect('warehouse_list')
        else:
            messages.error(request, 'Both fields are required.')
    return render(request, 'admin1/add_warehouse.html')

@login_required
@user_passes_test(is_admin)
def warehouse_list(request):
    warehouses = Warehouse.objects.all()
    return render(request, 'admin1/warehouse_list.html', {'warehouses': warehouses})

@login_required
@user_passes_test(is_admin)
def edit_warehouse(request, pk):
    warehouse = get_object_or_404(Warehouse, id=pk)
    if request.method == 'POST':
        warehouse.name = request.POST['name']
        warehouse.location = request.POST['location']
        warehouse.save()
        messages.success(request, 'Warehouse updated successfully.')
        return redirect('warehouse_list')
    return render(request, 'admin1/edit_warehouse.html', {'warehouse': warehouse})

@login_required
@user_passes_test(is_admin)
def delete_warehouse(request, pk):
    get_object_or_404(Warehouse, id=pk).delete()
    messages.success(request, 'Warehouse deleted successfully.')
    return redirect('warehouse_list')

@login_required
@user_passes_test(is_admin)
def product_list(request):
    products = Product.objects.all()
    return render(request, 'admin1/product_list.html', {'products': products})

@login_required
@user_passes_test(is_admin)
def add_product(request):
    suppliers = NewUser.objects.filter(user_type='supplier')
    warehouses = Warehouse.objects.all()
    if request.method == 'POST':
        name = request.POST['name']
        sku = request.POST['sku']
        quantity = request.POST['quantity']
        restock_threshold = request.POST['restock_threshold']
        warehouse_id = request.POST['warehouse']
        supplier_id = request.POST['supplier']
        Product.objects.create(
            name=name,
            sku=sku,
            quantity=quantity,
            restock_threshold=restock_threshold,
            warehouse_id=warehouse_id,
            supplier_id=supplier_id
        )
        messages.success(request, 'Product added successfully.')
        return redirect('product_list')
    return render(request, 'admin1/add_product.html', {'suppliers': suppliers, 'warehouses': warehouses})

@login_required
@user_passes_test(is_admin)
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    warehouses = Warehouse.objects.all()
    suppliers = NewUser.objects.filter(user_type='supplier')
    if request.method == 'POST':
        product.name = request.POST['name']
        product.sku = request.POST['sku']
        product.quantity = request.POST['quantity']
        product.restock_threshold = request.POST['restock_threshold']
        product.warehouse_id = request.POST['warehouse']
        product.supplier_id = request.POST['supplier']
        product.save()
        messages.success(request, 'Product updated successfully.')
        return redirect('product_list')
    return render(request, 'admin1/edit_product.html', {
        'product': product,
        'warehouses': warehouses,
        'suppliers': suppliers,
    })

@login_required
@user_passes_test(is_admin)
def delete_product(request, product_id):
    get_object_or_404(Product, id=product_id).delete()
    messages.success(request, 'Product deleted successfully.')
    return redirect('product_list')

@login_required
@user_passes_test(is_admin)
def create_shipment(request, order_id):
    try:
        order = Order.objects.get(order_id=order_id, order_status='processing')
    except Order.DoesNotExist:
        messages.error(request, f"No 'processing' order with ID {order_id} found.")
        return redirect('admin_order_list')

    logistics_partners = NewUser.objects.filter(user_type='logistic_partner')

    if request.method == 'POST':
        logistics_partner_id = request.POST.get('logistics_partner')
        estimated_delivery = request.POST.get('estimated_delivery')

        logistics_partner = get_object_or_404(NewUser, id=logistics_partner_id)
        tracking_number = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

        Shipment.objects.create(
            order=order,
            logistics_partner=logistics_partner,
            tracking_number=tracking_number,
            shipment_status='in_transit',
            estimated_delivery=estimated_delivery,
            current_location=order.product.warehouse.location
        )

        order.order_status = 'shipped'
        order.save()

        messages.success(request, f"Shipment created for Order {order_id} with tracking {tracking_number}.")
        return redirect('admin_order_list')

    return render(request, 'admin1/create_shipment.html', {
        'order': order,
        'logistics_partners': logistics_partners
    })

@login_required
@user_passes_test(is_admin)
def mark_shipment_delivered(request, tracking_number):
    shipment = get_object_or_404(Shipment, tracking_number=tracking_number)
    shipment.shipment_status = 'delivered'
    shipment.save()
    shipment.order.order_status = 'delivered'
    shipment.order.save()
    messages.success(request, f"Shipment {tracking_number} marked as Delivered.")
    return redirect('admin_order_list')

@login_required
@user_passes_test(is_admin)
def mark_order_paid(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    order.order_status = 'paid'
    order.save()
    messages.success(request, f"Order {order_id} marked as Paid.")
    return redirect('admin_order_list')




@login_required
@user_passes_test(is_admin)
def shipment_list(request):
    processing_orders = Order.objects.filter(order_status__in=['pending', 'processing'])
    return render(request, 'admin1/shipment_list.html', {'processing_orders': processing_orders})

@login_required
@user_passes_test(is_admin)
def stock_chart(request):
    products = Product.objects.all()
    labels = [product.name for product in products]
    data = [product.quantity for product in products]
    return render(request, 'admin1/stock_chart.html', {'labels': labels, 'data': data})


@login_required
@user_passes_test(is_admin)
def track_shipment_admin(request, tracking_number):
    try:
        shipment = Shipment.objects.get(tracking_number=tracking_number)
    except Shipment.DoesNotExist:
        messages.error(request, f"No shipment with tracking number {tracking_number} found.")
        return redirect('admin_order_list')
    return render(request, 'admin1/track_shipment.html', {'shipment': shipment})

@login_required
@user_passes_test(is_admin)
def admin_order_list(request):
    orders = Order.objects.all().order_by('-order_id')  # Latest orders first
    order_shipment_map = {}

    for order in orders:
        # Get the first shipment for each order, if exists
        shipment = order.shipments.first()
        if shipment:
            order_shipment_map[order.order_id] = shipment

    return render(request, 'admin1/order_list.html', {
        'orders': orders,
        'order_shipment_map': order_shipment_map
    })


@login_required
@user_passes_test(is_admin)
def order_detail_admin(request, order_id):
    try:
        order = Order.objects.get(order_id=order_id)
    except Order.DoesNotExist:
        messages.error(request, f"No order with ID {order_id} found.")
        return redirect('admin_order_list')
    return render(request, 'admin1/order_detail.html', {'order': order})
# --------------------------------------- Supplier Views --------------------------------------------------

def add_supplier(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        contact_no = request.POST.get('phone')
        password = request.POST.get('password')
        username = email if email else contact_no

        if NewUser.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return render(request, 'supplier/add_supplier.html')
        if NewUser.objects.filter(contact_no=contact_no).exists():
            messages.error(request, "Phone number already exists.")
            return render(request, 'supplier/add_supplier.html')

        NewUser.objects.create(
            username=username,
            full_name=full_name,
            email=email,
            contact_no=contact_no,
            password=make_password(password),
            user_type='supplier',
        )
        messages.success(request, "Supplier added successfully. Please login.")
        return redirect('add_supplier')
    return render(request, 'supplier/add_supplier.html')

@login_required
@user_passes_test(is_supplier)
def supplier_dashboard(request):
    products = Product.objects.filter(supplier=request.user)
    movements = StockMovement.objects.filter(product__supplier=request.user)
    context = {
        'total_movements': movements.count(),
        'stock_in_movements': movements.filter(movement_type='in').count(),
        'stock_out_movements': movements.filter(movement_type='out').count(),
        'low_stock_products': products.filter(quantity__lt=F('restock_threshold')).count(),
        'recent_movements': movements.order_by('-created_at')[:5],
    }
    return render(request, 'supplier/dashboard.html', context)

@login_required
@user_passes_test(is_supplier)
def stock_movement_list(request):
    movements = StockMovement.objects.filter(product__supplier=request.user).order_by('-created_at')
    movement_type = request.GET.get('type')
    if movement_type in ['in', 'out', 'adjust']:
        movements = movements.filter(movement_type=movement_type)
    context = {
        'movements': movements,
        'total_movements': StockMovement.objects.filter(product__supplier=request.user).count(),
        'stock_in_movements': StockMovement.objects.filter(product__supplier=request.user, movement_type='in').count(),
        'stock_out_movements': StockMovement.objects.filter(product__supplier=request.user, movement_type='out').count(),
        'adjust_movements': StockMovement.objects.filter(product__supplier=request.user, movement_type='adjust').count(),
    }
    return render(request, 'supplier/stock_movement_list.html', context)

@login_required
@user_passes_test(is_supplier)
def add_stock_movement(request):
    products = Product.objects.filter(supplier=request.user)
    if request.method == 'POST':
        product_id = request.POST.get('product')
        movement_type = request.POST.get('movement_type')
        quantity = request.POST.get('quantity')
        reason = request.POST.get('reason', '')
        if not all([product_id, movement_type, quantity]):
            messages.error(request, "All required fields must be filled.")
            return render(request, 'supplier/add_stock_movement.html', {'products': products})
        try:
            quantity = int(quantity)
            if quantity < 0:
                raise ValueError("Quantity cannot be negative.")
        except ValueError:
            messages.error(request, "Invalid quantity. Please enter a valid number.")
            return render(request, 'supplier/add_stock_movement.html', {'products': products})
        product = get_object_or_404(Product, id=product_id, supplier=request.user)
        if movement_type not in ['in', 'out', 'adjust']:
            messages.error(request, "Invalid movement type.")
            return render(request, 'supplier/add_stock_movement.html', {'products': products})
        if movement_type == 'in':
            product.quantity += quantity
        elif movement_type == 'out':
            if product.quantity < quantity:
                messages.error(request, "Insufficient stock for this operation.")
                return render(request, 'supplier/add_stock_movement.html', {'products': products})
            product.quantity -= quantity
        elif movement_type == 'adjust':
            product.quantity = quantity
        product.save()
        StockMovement.objects.create(
            product=product,
            movement_type=movement_type,
            quantity=quantity,
            reason=reason
        )
        messages.success(request, "Stock movement added successfully.")
        return redirect('stock_movement_list')
    return render(request, 'supplier/add_stock_movement.html', {'products': products})

@login_required
@user_passes_test(is_supplier)
def supplier_order_list(request):
    orders = Order.objects.filter(product__supplier=request.user, order_status='pending')
    return render(request, 'supplier/order_list.html', {'orders': orders})

@login_required
@user_passes_test(is_supplier)
def confirm_order(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, order_status='pending')
    order.order_status = 'processing'
    order.save()
    messages.success(request, f"Order {order_id} confirmed.")
    return redirect('supplier_order_list')

# --- ===================================Logistic Partner Views =========================================---

def add_logistic_partner(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        contact_no = request.POST.get('phone')
        password = request.POST.get('password')
        username = email if email else contact_no

        if NewUser.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return render(request, 'logistics/add_logistic_partner.html')
        if NewUser.objects.filter(contact_no=contact_no).exists():
            messages.error(request, "Phone number already exists.")
            return render(request, 'logistics/add_logistic_partner.html')

        NewUser.objects.create(
            username=username,
            full_name=full_name,
            email=email,
            contact_no=contact_no,
            password=make_password(password),
            user_type='logistic_partner',
        )
        messages.success(request, "Logistic partner added successfully. Please login.")
        return redirect('add_logistic_partner')
    return render(request, 'logistics/add_logistic_partner.html')

@login_required
@user_passes_test(is_logistic_partner)
def logistics_dashboard(request):
    shipments = Shipment.objects.filter(logistics_partner=request.user)
    context = {
        'total_shipments': shipments.count(),
        'in_transit_shipments': shipments.filter(shipment_status='in_transit').count(),
        'delivered_shipments': shipments.filter(shipment_status='delivered').count(),
        'recent_shipments': shipments.order_by('-estimated_delivery')[:5],
    }
    return render(request, 'logistics/dashboard.html', context)

@login_required
@user_passes_test(is_logistic_partner)
def shipment_list_partner(request):
    shipments = Shipment.objects.filter(logistics_partner=request.user)
    return render(request, 'logistics/shipment_list.html', {'shipments': shipments})

@login_required
@user_passes_test(is_logistic_partner)
def update_shipment(request, shipment_id):
    try:
        shipment = Shipment.objects.get(tracking_number=shipment_id, logistics_partner=request.user)
    except Shipment.DoesNotExist:
        messages.error(request, f"No shipment with tracking number {shipment_id} assigned to you.")
        return redirect('shipment_list_partner')
    if request.method == 'POST':
        shipment_status = request.POST.get('shipment_status')
        current_location = request.POST.get('current_location')
        shipment.shipment_status = shipment_status
        shipment.current_location = current_location
        if shipment_status == 'delivered':
            shipment.order.order_status = 'delivered'
            shipment.order.save()
        shipment.save()
        messages.success(request, f"Shipment {shipment_id} updated successfully.")
        return redirect('shipment_list_partner')
    return render(request, 'logistics/update_shipment.html', {'shipment': shipment})

# --================================================- Customer Views ---=========================

def add_customer(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        contact_no = request.POST.get('phone')
        password = request.POST.get('password')
        username = email if email else contact_no

        if NewUser.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return render(request, 'register.html')
        if NewUser.objects.filter(contact_no=contact_no).exists():
            messages.error(request, "Phone number already exists.")
            return render(request, 'register.html')

        NewUser.objects.create(
            username=username,
            full_name=full_name,
            email=email,
            contact_no=contact_no,
            password=make_password(password),
            user_type='customer',
        )

        if email:
            try:
                send_mail(
                    subject="Registration Successful",
                    message=f"Dear {full_name},\n\nYour registration was successful. You can now log in to the Supply Chain Management System.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False,
                )
            except Exception as e:
                messages.warning(request, f"User registered, but failed to send email: {e}")

        messages.success(request, "User added successfully. Please login.")
        return redirect('user_login')
    return render(request, 'register.html')




@login_required
@user_passes_test(is_customer)
def place_order(request):
    products = Product.objects.all()
    if request.method == 'POST':
        product_id = request.POST.get('product')
        quantity = request.POST.get('quantity')
        try:
            quantity = int(quantity)
            if quantity <= 0:
                raise ValueError("Quantity must be positive.")
        except ValueError:
            messages.error(request, "Invalid quantity. Please enter a valid number.")
            return render(request, 'place_order.html', {'products': products})
        product = get_object_or_404(Product, id=product_id)
        if product.quantity < quantity:
            messages.error(request, f"Insufficient stock for {product.name}. Available: {product.quantity}")
            return render(request, 'place_order.html', {'products': products})
        total_amount = product.quantity * quantity  # Adjust if Product has a unit_price field
        order = Order.objects.create(
            customer=request.user,
            product=product,
            quantity=quantity,
            total_amount=total_amount,
            order_status='pending'
        )
        product.quantity -= quantity
        product.save()
        StockMovement.objects.create(
            product=product,
            movement_type='out',
            quantity=quantity,
            reason=f"Order {order.order_id}"
        )
        messages.success(request, f"Order {order.order_id} placed successfully.")
        return redirect('order_list')
    return render(request, 'place_order.html', {'products': products})

@login_required
@user_passes_test(is_customer)
def order_list(request):
    orders = Order.objects.filter(customer=request.user).order_by('-order_id')
    valid_statuses = ['shipped', 'delivered', 'paid']  # pass this to template
    
    context = {
        'orders': orders,
        'has_orders': orders.exists(),
        'valid_statuses': valid_statuses,
    }
    return render(request, 'order_list.html', context)


@login_required
@user_passes_test(is_customer)
def track_shipment(request, tracking_number):
    try:
        shipment = Shipment.objects.get(tracking_number=tracking_number, order__customer=request.user)
    except Shipment.DoesNotExist:
        messages.error(request, f"No shipment with tracking number {tracking_number} found.")
        return redirect('order_list')
    return render(request, 'track_shipment.html', {'shipment': shipment})

from django.core.mail import send_mail
from django.conf import settings

@login_required
@user_passes_test(is_customer)
def process_payment(request, order_id):
    try:
        order = Order.objects.get(order_id=order_id, customer=request.user, order_status__iexact='delivered')
    except Order.DoesNotExist:
        messages.error(request, f"Order {order_id} is not available for payment.")
        return redirect('order_list')
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        PaymentTransaction.objects.create(
            order=order,
            payment_method=payment_method,
            payment_status='paid',
            payment_date=timezone.now(),
            amount=order.total_amount
        )
        order.order_status = 'paid'
        order.save()

        # Send email notification to customer
        subject = f"Payment Confirmation for Order #{order.order_id}"
        message = f"Dear {order.customer.full_name or order.customer.username},\n\n" \
                  f"Thank you for your payment for Order #{order.order_id}.\n" \
                  f"The total amount of {order.total_amount} has been successfully paid using {payment_method}.\n\n" \
                  f"Your order will be processed shortly.\n\n" \
                  f"Best regards,\nYour Store Team"
        recipient_list = [order.customer.email]

        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list, fail_silently=False)

        messages.success(request, f"Payment for Order {order_id} processed successfully.")
        return redirect('order_list')
    
    return render(request, 'process_payment.html', {'order': order})
