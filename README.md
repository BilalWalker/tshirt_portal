# Deployment Instructions

## Local Development Setup
Do the steps in the order listed below

1. Clone the repository:
   ```
   git clone <repository-url>
   cd tshirt_portal
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root with the following variables:
   ```
   SECRET_KEY=your-secret-key
   DEBUG=True
   
   # Shopify API settings
   SHOPIFY_API_KEY=your-shopify-api-key
   SHOPIFY_API_SECRET=your-shopify-api-secret
   SHOPIFY_SHOP_NAME=your-shop-name
   ADMIN_API_ACCESS_TOKEN=your-admin-api-access-token
   ```

5. Run migrations:
   ```
   python manage.py migrate
   ```

6. Create a superuser:
   ```
   python manage.py createsuperuser
   ```

7. Start the development server:
   ```
   python manage.py runserver
   ```

## Shopify Setup

1. Create a Shopify store if you don't have one already.

2. Create a private app in your Shopify admin:
   - Go to Apps > Develop apps
   - Click "Create an app"
   - Name your app (e.g., "T-Shirt Design Portal")
   - Set appropriate permissions (read/write access for products and orders)
   - Install the app to get your API credentials

3. For API credentials, you'll need:
   - API key: Used as SHOPIFY_API_KEY
   - API secret key: Used as SHOPIFY_API_SECRET 
   - Admin API access token: Used as SHOPIFY_PASSWORD
   - Shop name: The subdomain part of your .myshopify.com URL, used as SHOPIFY_SHOP_NAME

4. Update your `.env` file with these credentials.

5. Test the connection by adding a design and attempting to publish it to Shopify.

## Troubleshooting Shopify Integration

If you encounter issues with the Shopify integration:

1. Check your API credentials carefully
2. Ensure your shop name is correct (just the subdomain part of your .myshopify.com URL)
3. Verify that your app has the necessary API permissions:
   - read_products, write_products
   - read_orders, write_orders
   - read_customers
   - read_inventory 
   - read_fulfillments
   - read_locations
4. Look at the error logs for specific error messages
5. Test the connection using the test_shopify_connection() function

## Production Deployment

For production deployment, consider using:
- PostgreSQL instead of SQLite
- Gunicorn as the WSGI server
- Nginx as a reverse proxy
- Django's collectstatic for static files
- A proper media storage solution (e.g., AWS S3)
