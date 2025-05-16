import shopify
from django.conf import settings
import base64
import os
from PIL import Image
import io
import requests

def initialize_shopify_session():

    shop_url = f"https://{settings.SHOPIFY_API_KEY}:{settings.SHOPIFY_API_SECRET}@{settings.SHOPIFY_SHOP_NAME}.myshopify.com/admin/api/{settings.SHOPIFY_API_VERSION}"
    print(shop_url)
    shopify.ShopifyResource.set_site(shop_url)
    return True

def image_to_base64(image_path):
    """Convert image to base64 string for Shopify API"""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

def publish_to_shopify(design):
    """
    Publish a design to Shopify as a product
    Returns (success, product_id, product_url)
    """
    try:
        initialize_shopify_session()
        
        # Create new product
        new_product = shopify.Product()
        new_product.title = design.title
        new_product.body_html = design.description
        new_product.product_type = "T-Shirt"
        new_product.vendor = "T-Shirt Design Portal"
        
        # Add variants for different sizes
        sizes = ["S", "M", "L", "XL", "XXL"]
        variants = []
        for size in sizes:
            variant = shopify.Variant()
            variant.option1 = size
            variant.price = "24.99"  # Default price
            variant.inventory_management = "shopify"
            variant.inventory_quantity = 10  # Default inventory
            variants.append(variant)
        
        new_product.variants = variants
        
        # Add size option
        option = shopify.Option()
        option.name = "Size"
        option.values = sizes
        new_product.options = [option]
        
        # Save the product first
        if new_product.save():
            # Now add the image
            image_path = design.image.path
            image = shopify.Image()
            image.product_id = new_product.id
            image.attachment = image_to_base64(image_path)
            image.save()
            
            # Get the product URL
            product_url = f"https://{settings.SHOPIFY_SHOP_NAME}.myshopify.com/admin/products/{new_product.id}"
            
            return True, str(new_product.id), product_url
        else:
            # Handle errors
            print(f"Failed to save product: {new_product.errors.full_messages()}")
            return False, None, None
    
    except Exception as e:
        print(f"Error publishing to Shopify: {str(e)}")
        return False, None, None

def unpublish_from_shopify(product_id):
    """
    Remove a product from Shopify
    Returns success (True/False)
    """
    try:
        initialize_shopify_session()
        product = shopify.Product.find(product_id)
        return product.destroy()
    except Exception as e:
        print(f"Error unpublishing from Shopify: {str(e)}")
        return False

def sync_orders_from_shopify():
    """
    Fetch orders from Shopify
    Returns a list of orders
    """
    try:
        initialize_shopify_session()
        orders = shopify.Order.find(status="any", limit=250)
        return orders
    except Exception as e:
        print(f"Error syncing orders from Shopify: {str(e)}")
        return []
