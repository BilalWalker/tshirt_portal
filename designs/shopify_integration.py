import shopify
from django.conf import settings
import base64
import os
from PIL import Image
import io
import requests
import logging

logger = logging.getLogger(__name__)

def initialize_shopify_session():
    try:
        # Set up the API version and credentials
        api_version = settings.SHOPIFY_API_VERSION
        shop_name = settings.SHOPIFY_SHOP_NAME
        api_key = settings.SHOPIFY_API_KEY
        password = settings.SHOPIFY_PASSWORD  # This is the Admin API access token
        
        # Initialize the session directly using the private app credentials
        session = shopify.Session(f"{shop_name}.myshopify.com", api_version, password)
        shopify.ShopifyResource.activate_session(session)
        print('session', session)
        
        # Test the session
        shop = shopify.Shop.current()
        logger.info(f"Successfully connected to Shopify shop: {shop.name}")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize Shopify session: {str(e)}")
        return False

def image_to_base64(image_path):
    """Convert image to base64 string for Shopify API"""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

def test_shopify_connection():
    try:
        initialize_shopify_session()
        shop = shopify.Shop.current()
        return True, f"Connected to shop: {shop.name}"
    except Exception as e:
        return False, f"Error connecting to Shopify: {str(e)}"

def publish_to_shopify(design):
    """
    Publish a design to Shopify as a product
    Returns (success, product_id, product_url)
    """
    
    test_shopify_connection()
    try:
        initialize_shopify_session()
        print('hellllllllllo')
        
        # Create new product
        new_product = shopify.Product()
        new_product.title = design.title
        new_product.body_html = design.description
        new_product.product_type = "T-Shirt"
        new_product.vendor = "T-Shirt Design Portal"
        print('new_product',new_product)
        
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
            print('new_product.id', new_product.id)
            image.attachment = image_to_base64(image_path)
            image.save()
            
            # Get the product URL
            # product_url = f"https://{settings.SHOPIFY_SHOP_NAME}.myshopify.com/admin/products/{new_product.id}"
            product_url = f'https://wreck-tshirt.myshopify.com/admin/products/{new_product.id}'
            
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
