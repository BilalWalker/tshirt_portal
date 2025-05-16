from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .models import Order, OrderItem
from designs.models import Design
from users.views import is_admin

# Import both integration modules to give options
from designs.shopify_integration import sync_orders_from_shopify as sync_orders_from_shopify_rest
from designs.shopify_graphql import sync_orders_from_shopify as sync_orders_from_shopify_graphql

# Use the REST API by default
USE_GRAPHQL_API = True  # Set to True to use GraphQL API instead of REST

class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'orders/list.html'
    context_object_name = 'orders'
    ordering = ['-created_at']

class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'orders/detail.html'
    context_object_name = 'order'

@login_required
def sync_orders(request):
    if not is_admin(request.user):
        messages.error(request, "You don't have permission to sync orders.")
        return redirect('order_list')
    
    # Get orders from Shopify using selected API
    if USE_GRAPHQL_API:
        shopify_orders = sync_orders_from_shopify_graphql()
        print('------------------------',shopify_orders)
    else:
        shopify_orders = sync_orders_from_shopify_rest()
    
    sync_count = 0
    for shopify_order in shopify_orders:
        # Check if order already exists
        order_exists = Order.objects.filter(shopify_order_id=shopify_order.id).exists()
        if not order_exists:
            # Create new order
            new_order = Order(
                shopify_order_id=shopify_order.id,
                customer_name=f"{shopify_order.customer.first_name} {shopify_order.customer.last_name}",
                customer_email=shopify_order.customer.email,
                total_price=shopify_order.total_price,
                status=map_shopify_status_to_local(shopify_order.fulfillment_status),
                created_at=shopify_order.created_at
            )
            new_order.save()
            
            # Create order items
            for item in shopify_order.line_items:
                # Try to find the design
                design = None
                if hasattr(item, 'product_id'):
                    design = Design.objects.filter(shopify_product_id=item.product_id).first()
                
                order_item = OrderItem(
                    order=new_order,
                    design=design,
                    product_title=item.title,
                    shopify_product_id=item.product_id if hasattr(item, 'product_id') else "",
                    shopify_variant_id=item.variant_id if hasattr(item, 'variant_id') else "",
                    size=item.variant_title if hasattr(item, 'variant_title') else "",
                    quantity=item.quantity,
                    price=item.price
                )
                order_item.save()
            
            sync_count += 1
    
    messages.success(request, f"Successfully synced {sync_count} new orders from Shopify!")
    return redirect('order_list')

def map_shopify_status_to_local(shopify_status):
    """Map Shopify fulfillment status to local order status"""
    if shopify_status == "fulfilled":
        return "SHIPPED"
    elif shopify_status == "partial":
        return "PROCESSING"
    elif shopify_status == "null":
        return "PENDING"
    else:
        return "PENDING"