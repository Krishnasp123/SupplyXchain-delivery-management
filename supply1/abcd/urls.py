from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # General (Public) URLs
    path('', views.index, name='index'),  # Home page
    path('about/', views.about, name='about'),  # About page
    path('contact/', views.contact, name='contact'),  # Contact page
    path('services/', views.services, name='services'),  # Services page
    path('login/', views.user_login, name='user_login'),  # User login
    path('logout/', views.logout_view, name='logout_view'),  # User logout


    # Customer URLs
    path('add_customer/', views.add_customer, name='add_customer'),  # Matches /add_customer/  # Register new customer
    path('orders/place/', views.place_order, name='place_order'),  # Place an order
    path('orders/', views.order_list, name='order_list'),  # View customer orders
    path('shipments/track/<str:tracking_number>/', views.track_shipment, name='track_shipment'),  # Track shipment
    path('payments/process/<int:order_id>/', views.process_payment, name='process_payment'),  # Process payment

    # Supplier URLs
    path('supplier/dashboard/', views.supplier_dashboard, name='supplier_dashboard'),  # Supplier dashboard
    path('supplier/orders/', views.supplier_order_list, name='supplier_order_list'),  # View pending orders
    path('supplier/orders/confirm/<int:order_id>/', views.confirm_order, name='confirm_order'), 
    path('stock-movement/add/', views.add_stock_movement, name='add_stock_movement'),  
    path('stock-movement/list/', views.stock_movement_list, name='stock_movement_list'),

    # Logistics Partner URLs
    path('logistics/dashboard/', views.logistics_dashboard, name='logistics_dashboard'),  
    path('shipments/partner/', views.shipment_list_partner, name='shipment_list_partner'),  
    path('shipments/update/<str:shipment_id>/', views.update_shipment, name='update_shipment'),
    # Admin URLs
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),  # Admin dashboard
    # Supplier Management
    path('suppliers/', views.view_suppliers, name='view_suppliers'),
    path('suppliers/add/', views.add_supplier, name='add_supplier'), 
    path('suppliers/edit/<int:user_id>/', views.edit_supplier, name='edit_supplier'), 
    path('suppliers/delete/<int:user_id>/', views.delete_supplier, name='delete_supplier'),  
    # Logistics Partner Management
    path('logistic-partners/', views.view_logistic_partners, name='view_logistic_partners'),
    path('logistic-partners/add/', views.add_logistic_partner, name='add_logistic_partner'),  
    path('logistic-partners/edit/<int:user_id>/', views.edit_logistic_partner, name='edit_logistic_partner'),
    path('logistic-partners/delete/<int:user_id>/', views.delete_logistic_partner, name='delete_logistic_partner'),  

    # Warehouse Management
    path('warehouses/', views.warehouse_list, name='warehouse_list'),  # View all warehouses
    path('warehouses/add/', views.add_warehouse, name='add_warehouse'),  # Add warehouse
    path('warehouses/edit/<int:pk>/', views.edit_warehouse, name='edit_warehouse'),  # Edit warehouse
    path('warehouses/delete/<int:pk>/', views.delete_warehouse, name='delete_warehouse'),  # Delete warehouse
    # Product Management
    path('products/', views.product_list, name='product_list'),  # View all products
    path('products/add/', views.add_product, name='add_product'),  # Add product
    path('products/edit/<int:product_id>/', views.edit_product, name='edit_product'),  # Edit product
    path('products/delete/<int:product_id>/', views.delete_product, name='delete_product'),  # Delete product
    # Shipment Management
    path('shipments/create/<int:order_id>/', views.create_shipment, name='create_shipment'),  # Create shipment
    path('shipments/', views.shipment_list, name='shipment_list'),  # View all shipments
    # Analytics
    path('stock_chart/', views.stock_chart, name='stock_chart'),  # View stock analytics

    path('admin_order_list/', views.admin_order_list, name='admin_order_list'),
    path('shipments/create/<str:order_id>/', views.create_shipment, name='create_shipment'),
    path('shipments/', views.shipment_list, name='shipment_list'),
    path('track/<str:tracking_number>/', views.track_shipment_admin, name='track_shipment_admin'),
    path('orders/<str:order_id>/', views.order_detail_admin, name='order_detail_admin'),
    # In urls.py
    path('shipment/<str:tracking_number>/delivered/', views.mark_shipment_delivered, name='mark_shipment_delivered'),
    path('order/<int:order_id>/paid/', views.mark_order_paid, name='mark_order_paid'),
    # Existing URLs...
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)