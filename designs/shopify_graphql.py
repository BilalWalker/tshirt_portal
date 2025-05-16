import json
import logging
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
from django.conf import settings
import base64

logger = logging.getLogger(__name__)

def get_graphql_client():
    """
    Initialize and return a GraphQL client for Shopify's Admin API
    """
    # Set up the transport with the Shopify Admin API endpoint and headers
    shop_name = settings.SHOPIFY_SHOP_NAME
    api_version = settings.SHOPIFY_API_VERSION
    admin_token = settings.SHOPIFY_PASSWORD
    
    # Construct the Shopify GraphQL endpoint URL
    endpoint = f"https://{shop_name}.myshopify.com/admin/api/{api_version}/graphql.json"
    
    # Set up headers with authentication
    headers = {
        "X-Shopify-Access-Token": admin_token,
        "Content-Type": "application/json"
    }
    
    # Create the transport with SSL verification disabled for development
    import requests
    # from requests.packages.urllib3.exceptions import InsecureRequestWarning
    # requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    
    transport = RequestsHTTPTransport(
        url=endpoint,
        headers=headers,
        use_json=True,
        verify=False,  # Disable SSL verification for development
    )
    
    # Create the client
    return Client(transport=transport, fetch_schema_from_transport=False)

def test_connection():
    """
    Test the GraphQL connection to Shopify
    """
    try:
        client = get_graphql_client()
        
        # A simple query to get the shop's name
        query = gql('''
        {
          shop {
            name
            primaryDomain {
              url
            }
          }
        }
        ''')
        
        # Execute the query
        result = client.execute(query)
        
        return True, f"Successfully connected to Shopify shop: {result['shop']['name']}"
    except Exception as e:
        logger.error(f"GraphQL connection error: {str(e)}")
        return False, f"Failed to connect to Shopify: {str(e)}"

def publish_product(design):
    """
    Publish a design to Shopify as a product using GraphQL
    Returns (success, product_id, product_url)
    """
    try:
        client = get_graphql_client()
        
        # Get the first location ID to use for inventory
        location_id = get_first_location_id(client)
        if not location_id:
            logger.error("Could not get a location ID for inventory")
            return False, None, None
        
        # Updated mutation format based on current Shopify GraphQL API schema
        mutation = gql('''
        mutation createProduct($input: ProductInput!) {
          productCreate(input: $input) {
            product {
              id
              title
              handle
            }
            userErrors {
              field
              message
            }
          }
        }
        ''')
        
        # Prepare the product input with correct format
        product_input = {
            "title": design.title,
            "descriptionHtml": design.description or "",
            "productType": "T-Shirt",
            "vendor": "T-Shirt Design Portal",
            "options": ["Size"],  # Simple string array
            "variants": [
                {
                    "price": "24.99", 
                    "options": ["S"], 
                    "inventoryItem": {"tracked": True},
                    "inventoryQuantities": [{"availableQuantity": 10, "locationId": location_id}]
                },
                {
                    "price": "24.99", 
                    "options": ["M"], 
                    "inventoryItem": {"tracked": True},
                    "inventoryQuantities": [{"availableQuantity": 10, "locationId": location_id}]
                },
                {
                    "price": "24.99", 
                    "options": ["L"], 
                    "inventoryItem": {"tracked": True},
                    "inventoryQuantities": [{"availableQuantity": 10, "locationId": location_id}]
                },
                {
                    "price": "24.99", 
                    "options": ["XL"], 
                    "inventoryItem": {"tracked": True},
                    "inventoryQuantities": [{"availableQuantity": 10, "locationId": location_id}]
                },
                {
                    "price": "24.99", 
                    "options": ["XXL"], 
                    "inventoryItem": {"tracked": True},
                    "inventoryQuantities": [{"availableQuantity": 10, "locationId": location_id}]
                }
            ],
            "status": "ACTIVE"
        }
        
        # Execute the mutation
        result = client.execute(mutation, variable_values={"input": product_input})
        
        # Check for errors
        if result["productCreate"]["userErrors"]:
            errors = ", ".join([error["message"] for error in result["productCreate"]["userErrors"]])
            logger.error(f"GraphQL product creation error: {errors}")
            return False, None, None
        
        # Extract the product ID (removing the prefix)
        product_gid = result["productCreate"]["product"]["id"]
        product_id = product_gid.split("/")[-1]
        
        # Get the product URL
        product_url = f"https://{settings.SHOPIFY_SHOP_NAME}.myshopify.com/admin/products/{product_id}"
        
        # Now add the image using a separate mutation
        add_image_to_product(client, product_gid, design.image.path)
        
        return True, product_id, product_url
        
    except Exception as e:
        logger.error(f"Error publishing product via GraphQL: {str(e)}")
        return False, None, None

def get_first_location_id(client):
    """
    Get the first location ID from the shop to use for inventory
    """
    try:
        query = gql('''
        {
          locations(first: 1) {
            edges {
              node {
                id
              }
            }
          }
        }
        ''')
        
        result = client.execute(query)
        
        if result["locations"]["edges"]:
            return result["locations"]["edges"][0]["node"]["id"]
        return None
    except Exception as e:
        logger.error(f"Error getting location ID: {str(e)}")
        return None

def add_image_to_product(client, product_id, image_path):
    """
    Add an image to a product using GraphQL
    """
    try:
        # Create the product image
        create_image_mutation = gql('''
        mutation createProductImage($input: ProductImageInput!) {
          productImageCreate(input: $input) {
            image {
              id
              url
            }
            userErrors {
              field
              message
            }
          }
        }
        ''')
        
        # Convert image to base64
        with open(image_path, "rb") as img_file:
            base64_image = base64.b64encode(img_file.read()).decode('utf-8')
        
        # Prepare the image input
        image_input = {
            "productId": product_id,
            "image": f"data:image/jpeg;base64,{base64_image}"
        }
        
        # Create the product image
        result = client.execute(create_image_mutation, 
                               variable_values={"input": image_input})
        
        # Check for errors
        if result["productImageCreate"]["userErrors"]:
            errors = ", ".join([error["message"] for error in result["productImageCreate"]["userErrors"]])
            logger.error(f"GraphQL image creation error: {errors}")
            return False
            
        return True
        
    except Exception as e:
        logger.error(f"Error adding image via GraphQL: {str(e)}")
        return False

def unpublish_product(product_id):
    """
    Remove a product from Shopify using GraphQL
    """
    try:
        client = get_graphql_client()
        
        # Convert the numeric ID to a global ID
        global_id = f"gid://shopify/Product/{product_id}"
        
        # Prepare the delete mutation
        mutation = gql('''
        mutation deleteProduct($input: ProductDeleteInput!) {
          productDelete(input: $input) {
            deletedProductId
            userErrors {
              field
              message
            }
          }
        }
        ''')
        
        # Execute the mutation
        result = client.execute(mutation, 
                               variable_values={"input": {"id": global_id}})
        
        # Check for errors
        if result["productDelete"]["userErrors"]:
            errors = ", ".join([error["message"] for error in result["productDelete"]["userErrors"]])
            logger.error(f"GraphQL product deletion error: {errors}")
            return False
            
        return True
        
    except Exception as e:
        logger.error(f"Error unpublishing product via GraphQL: {str(e)}")
        return False

def get_recent_orders(limit=10):
    """
    Get recent orders from Shopify using GraphQL
    """
    try:
        client = get_graphql_client()
        
        # Prepare the query
        query = gql('''
        query getOrders($first: Int!) {
          orders(first: $first, sortKey: CREATED_AT, reverse: true) {
            edges {
              node {
                id
                name
                createdAt
                displayFinancialStatus
                customer {
                  firstName
                  lastName
                  email
                }
                totalPriceSet {
                  shopMoney {
                    amount
                    currencyCode
                  }
                }
                lineItems(first: 10) {
                  edges {
                    node {
                      title
                      quantity
                      variant {
                        id
                        title
                        price
                        product {
                          id
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
        ''')
        
        # Execute the query
        result = client.execute(query, variable_values={"first": limit})
        
        # Process the results
        orders = []
        for edge in result["orders"]["edges"]:
            order = edge["node"]
            
            # Extract order details
            processed_order = {
                "id": order["id"].split("/")[-1],
                "name": order["name"],
                "created_at": order["createdAt"],
                "status": order["displayFinancialStatus"],
                "customer": {
                    "name": f"{order['customer']['firstName']} {order['customer']['lastName']}".strip(),
                    "email": order["customer"]["email"]
                },
                "total_price": float(order["totalPriceSet"]["shopMoney"]["amount"]),
                "currency": order["totalPriceSet"]["shopMoney"]["currencyCode"],
                "line_items": []
            }
            
            # Process line items
            for item_edge in order["lineItems"]["edges"]:
                item = item_edge["node"]
                line_item = {
                    "title": item["title"],
                    "quantity": item["quantity"],
                    "variant_title": item["variant"]["title"] if item["variant"] else "",
                    "price": float(item["variant"]["price"]) if item["variant"] else 0,
                    "product_id": item["variant"]["product"]["id"].split("/")[-1] if item["variant"] and item["variant"]["product"] else None
                }
                processed_order["line_items"].append(line_item)
            
            orders.append(processed_order)
            
        return orders
        
    except Exception as e:
        logger.error(f"Error getting orders via GraphQL: {str(e)}")
        return []