"""
Flask API for Sales Dashboard
Deployable on Vercel as serverless functions
"""

import sys
import traceback
import os

# Print to stderr immediately (before logging is set up) to catch early errors
def emergency_log(message):
    """Log to stderr immediately, even if logging isn't set up."""
    print(f"[EMERGENCY] {message}", file=sys.stderr, flush=True)

try:
    emergency_log("=" * 80)
    emergency_log("Starting Flask application initialization...")
    emergency_log(f"Python version: {sys.version}")
    emergency_log(f"Working directory: {os.getcwd()}")
    emergency_log(f"Python path: {sys.path[:5]}")
    
    import logging
    
    # Configure verbose logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        stream=sys.stderr
    )
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    
    # Log startup
    logger.info("=" * 80)
    logger.info("Starting Flask application...")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Working directory: {os.getcwd()}")
    logger.info(f"Python path: {sys.path[:5]}")  # First 5 entries
    
except Exception as e:
    emergency_log(f"CRITICAL: Failed to set up logging: {e}")
    emergency_log(traceback.format_exc())
    raise

try:
    from flask import Flask, jsonify, request, send_file
    logger.info("✓ Flask imported successfully")
except Exception as e:
    error_msg = f"✗ Failed to import Flask: {e}"
    emergency_log(error_msg)
    emergency_log(traceback.format_exc())
    try:
        logger.error(error_msg)
        logger.error(traceback.format_exc())
    except:
        pass
    raise

try:
    from flask_cors import CORS
    logger.info("✓ flask_cors imported successfully")
except Exception as e:
    error_msg = f"✗ Failed to import flask_cors: {e}"
    emergency_log(error_msg)
    emergency_log(traceback.format_exc())
    try:
        logger.error(error_msg)
        logger.error(traceback.format_exc())
    except:
        pass
    raise

try:
    import pandas as pd
    logger.info("✓ pandas imported successfully")
except Exception as e:
    error_msg = f"✗ Failed to import pandas: {e}"
    emergency_log(error_msg)
    emergency_log(traceback.format_exc())
    try:
        logger.error(error_msg)
        logger.error(traceback.format_exc())
    except:
        pass
    raise

try:
    import gspread
    logger.info("✓ gspread imported successfully")
except Exception as e:
    error_msg = f"✗ Failed to import gspread: {e}"
    emergency_log(error_msg)
    emergency_log(traceback.format_exc())
    try:
        logger.error(error_msg)
        logger.error(traceback.format_exc())
    except:
        pass
    raise

try:
    from google.oauth2.service_account import Credentials
    logger.info("✓ google.oauth2 imported successfully")
except Exception as e:
    error_msg = f"✗ Failed to import google.oauth2: {e}"
    emergency_log(error_msg)
    emergency_log(traceback.format_exc())
    try:
        logger.error(error_msg)
        logger.error(traceback.format_exc())
    except:
        pass
    raise

try:
    from datetime import datetime
    import io
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    logger.info("✓ All other imports successful")
except Exception as e:
    error_msg = f"✗ Failed to import other dependencies: {e}"
    emergency_log(error_msg)
    emergency_log(traceback.format_exc())
    try:
        logger.error(error_msg)
        logger.error(traceback.format_exc())
    except:
        pass
    raise

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend
logger.info("✓ Flask app created")

# Google Sheets configuration
SPREADSHEET_ID = "1YAHO5rHhFVEReyAuxa7r2SDnoH7BnDfsmSEZ1LyjB8A"
CUSTOMER_ORDERS_SHEET_NAME = "Customer Orders"
BAKERY_PRODUCTS_SHEET_NAME = "Bakery Products Ordered "

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly"
]


def get_credentials():
    """Get Google Sheets credentials from environment variable or file."""
    import json
    import base64
    
    logger.info("Getting credentials...")
    logger.info(f"Environment variables available: {list(os.environ.keys())[:10]}...")  # First 10
    
    # Try environment variable first (for Vercel deployment)
    if 'GOOGLE_CREDENTIALS_BASE64' in os.environ:
        logger.info("Found GOOGLE_CREDENTIALS_BASE64 in environment")
        try:
            creds_b64 = os.environ['GOOGLE_CREDENTIALS_BASE64']
            logger.info(f"Credentials length: {len(creds_b64)} characters")
            logger.info(f"First 50 chars: {creds_b64[:50]}...")
            
            decoded = base64.b64decode(creds_b64)
            logger.info(f"Decoded length: {len(decoded)} bytes")
            
            creds_json = json.loads(decoded)
            logger.info(f"Parsed JSON successfully. Keys: {list(creds_json.keys())}")
            
            creds = Credentials.from_service_account_info(creds_json, scopes=SCOPES)
            logger.info("✓ Credentials created successfully from environment variable")
            return creds
        except Exception as e:
            logger.error(f"✗ Failed to decode GOOGLE_CREDENTIALS_BASE64: {e}")
            logger.error(traceback.format_exc())
            raise Exception(f"Failed to decode GOOGLE_CREDENTIALS_BASE64: {str(e)}")
    
    # Fallback to file (for local development)
    logger.info("GOOGLE_CREDENTIALS_BASE64 not found, trying file...")
    creds_path = os.path.join(os.path.dirname(__file__), "long-canto-360620-6858c5a01c13.json")
    logger.info(f"Looking for credentials file at: {creds_path}")
    logger.info(f"File exists: {os.path.exists(creds_path)}")
    
    if not os.path.exists(creds_path):
        error_msg = f"Credentials file not found: {creds_path}. Set GOOGLE_CREDENTIALS_BASE64 environment variable for Vercel deployment."
        logger.error(f"✗ {error_msg}")
        raise Exception(error_msg)
    
    logger.info("✓ Loading credentials from file")
    return Credentials.from_service_account_file(creds_path, scopes=SCOPES)


# Cache for data loading to reduce API calls
_data_cache = None
_cache_timestamp = None
CACHE_DURATION = 300  # Cache for 5 minutes

def load_data():
    """Load and merge data from Google Sheets with caching."""
    global _data_cache, _cache_timestamp
    
    logger.info("load_data() called")
    import time
    current_time = time.time()
    
    # Return cached data if available and not expired
    if _data_cache is not None and _cache_timestamp is not None:
        if current_time - _cache_timestamp < CACHE_DURATION:
            logger.info(f"Returning cached data (age: {current_time - _cache_timestamp:.1f}s)")
            return _data_cache
    
    try:
        logger.info("Getting credentials...")
        creds = get_credentials()
        logger.info("✓ Credentials obtained")
        
        logger.info("Authorizing gspread client...")
        client = gspread.authorize(creds)
        logger.info("✓ Client authorized")
        
        # Read Customer Orders
        logger.info(f"Opening spreadsheet: {SPREADSHEET_ID}")
        spreadsheet = client.open_by_key(SPREADSHEET_ID)
        logger.info(f"Opening worksheet: {CUSTOMER_ORDERS_SHEET_NAME}")
        orders_sheet = spreadsheet.worksheet(CUSTOMER_ORDERS_SHEET_NAME)
        logger.info("Reading customer orders data...")
        # Get all records as strings first to preserve date formats
        customer_orders_data = orders_sheet.get_all_records()
        logger.info(f"✓ Read {len(customer_orders_data)} customer orders")
        customer_orders_df = pd.DataFrame(customer_orders_data)
        logger.info(f"✓ Created DataFrame. Shape: {customer_orders_df.shape}")
        
        # Read Bakery Products
        logger.info(f"Opening worksheet: {BAKERY_PRODUCTS_SHEET_NAME}")
        products_sheet = spreadsheet.worksheet(BAKERY_PRODUCTS_SHEET_NAME)
        logger.info("Reading bakery products data...")
        bakery_products_data = products_sheet.get_all_records()
        logger.info(f"✓ Read {len(bakery_products_data)} bakery products")
        bakery_products_df = pd.DataFrame(bakery_products_data)
        logger.info(f"✓ Created DataFrame. Shape: {bakery_products_df.shape}")
        
        # Ensure date columns are read as strings/text
        date_columns = ['Order Date', 'Due Pickup Date', 'Pickup Timestamp', 'Due Date']
        for col in date_columns:
            if col in customer_orders_df.columns:
                customer_orders_df[col] = customer_orders_df[col].astype(str).replace('nan', '')
            if col in bakery_products_df.columns:
                bakery_products_df[col] = bakery_products_df[col].astype(str).replace('nan', '')
        
        # Parse dates from text
        customer_orders_df = parse_dates(customer_orders_df)
        bakery_products_df = parse_dates(bakery_products_df)
        
        # Merge data
        if 'OrderID' in customer_orders_df.columns and 'OrderID' in bakery_products_df.columns:
            customer_orders_df['OrderID'] = customer_orders_df['OrderID'].astype(str).str.strip().str.upper()
            bakery_products_df['OrderID'] = bakery_products_df['OrderID'].astype(str).str.strip().str.upper()
            
            merged_df = pd.merge(
                customer_orders_df,
                bakery_products_df,
                on='OrderID',
                how='left',
                suffixes=('_order', '_item')
            )
        else:
            merged_df = customer_orders_df
        
        # Cache the result
        logger.info("Caching merged data...")
        _data_cache = merged_df
        _cache_timestamp = current_time
        logger.info(f"✓ Data cached. Final shape: {merged_df.shape}")
        
        return merged_df
    
    except Exception as e:
        logger.error(f"✗ Error loading data: {e}")
        logger.error(traceback.format_exc())
        # If we have cached data, return it even if there's an error
        if _data_cache is not None:
            logger.info("Returning cached data due to error")
            return _data_cache
        raise Exception(f"Error loading data: {str(e)}")


def parse_dates(df):
    """Parse date columns from text, handling multiple formats."""
    df = df.copy()
    
    # Parse Order Date - convert from text to datetime
    if 'Order Date' in df.columns:
        # Convert to string first, handle empty values
        df['Order Date'] = df['Order Date'].astype(str).replace(['nan', 'None', ''], '')
        # First try MM-DD-YYYY format (most common: 11-11-2025, 09-11-2025)
        df['Order Date'] = pd.to_datetime(df['Order Date'], errors='coerce', format='%m-%d-%Y')
        # For any that didn't parse, try M/D/YYYY format
        mask_not_parsed = df['Order Date'].isna()
        if mask_not_parsed.any():
            df.loc[mask_not_parsed, 'Order Date'] = pd.to_datetime(
                df.loc[mask_not_parsed, 'Order Date'], 
                errors='coerce', 
                format='%m/%d/%Y'
            )
        # For any still not parsed, try default parsing
        mask_still_not_parsed = df['Order Date'].isna()
        if mask_still_not_parsed.any():
            df.loc[mask_still_not_parsed, 'Order Date'] = pd.to_datetime(
                df.loc[mask_still_not_parsed, 'Order Date'], 
                errors='coerce', 
                dayfirst=False, 
                yearfirst=False
            )
    
    # Parse Due Pickup Date - convert from text to datetime
    if 'Due Pickup Date' in df.columns:
        # Store original values as strings before parsing
        original_col = df['Due Pickup Date'].copy()
        df['Due Pickup Date'] = df['Due Pickup Date'].astype(str)
        df['Due Pickup Date'] = df['Due Pickup Date'].replace(['nan', 'None', 'NaT', 'NaN'], '')
        
        # Only parse non-empty strings
        mask_not_empty = df['Due Pickup Date'].str.strip() != ''
        
        if mask_not_empty.any():
            # Get original string values for parsing
            original_strings = original_col.astype(str).replace(['nan', 'None', 'NaT', 'NaN'], '')
            
            # First try MM-DD-YYYY format (e.g., 11-11-2025, 09-11-2025)
            parsed_dates = pd.to_datetime(
                original_strings.loc[mask_not_empty], 
                errors='coerce', 
                format='%m-%d-%Y'
            )
            df.loc[mask_not_empty, 'Due Pickup Date'] = parsed_dates
            
            # For any that didn't parse, try M/D/YYYY format
            mask_not_parsed = df['Due Pickup Date'].isna() & mask_not_empty
            if mask_not_parsed.any():
                df.loc[mask_not_parsed, 'Due Pickup Date'] = pd.to_datetime(
                    original_strings.loc[mask_not_parsed], 
                    errors='coerce', 
                    format='%m/%d/%Y'
                )
            
            # For any still not parsed, try default parsing
            mask_still_not_parsed = df['Due Pickup Date'].isna() & mask_not_empty
            if mask_still_not_parsed.any():
                df.loc[mask_still_not_parsed, 'Due Pickup Date'] = pd.to_datetime(
                    original_strings.loc[mask_still_not_parsed], 
                    errors='coerce', 
                    dayfirst=False, 
                    yearfirst=False
                )
    
    # Parse Pickup Timestamp - convert from text to datetime
    if 'Pickup Timestamp' in df.columns:
        df['Pickup Timestamp'] = df['Pickup Timestamp'].astype(str).replace(['nan', 'None', ''], '')
        df['Pickup Timestamp'] = pd.to_datetime(df['Pickup Timestamp'], errors='coerce', dayfirst=False, yearfirst=False)
    
    # Parse Due Date if it exists
    if 'Due Date' in df.columns:
        df['Due Date'] = df['Due Date'].astype(str).replace(['nan', 'None', ''], '')
        df['Due Date'] = pd.to_datetime(df['Due Date'], errors='coerce', format='%m-%d-%Y')
        mask_not_parsed = df['Due Date'].isna()
        if mask_not_parsed.any():
            df.loc[mask_not_parsed, 'Due Date'] = pd.to_datetime(
                df.loc[mask_not_parsed, 'Due Date'], 
                errors='coerce', 
                format='%m/%d/%Y'
            )
    
    return df


def filter_data(df, filters):
    """Apply filters to the dataframe."""
    filtered_df = df.copy()
    
    # Filter by Order Date
    if filters.get('date_start'):
        # Normalize to start of day
        start_date = pd.Timestamp(filters['date_start']).normalize()
        filtered_df = filtered_df[filtered_df['Order Date'].notna() & (filtered_df['Order Date'] >= start_date)]
    if filters.get('date_end'):
        # Normalize to end of day (23:59:59.999) to include the full end date
        end_date = pd.Timestamp(filters['date_end']).normalize() + pd.Timedelta(days=1) - pd.Timedelta(microseconds=1)
        filtered_df = filtered_df[filtered_df['Order Date'].notna() & (filtered_df['Order Date'] <= end_date)]
    
    # Filter by Order Type (supports multiple order types)
    if filters.get('order_type') and filters['order_type']:
        if 'Order Type ' in filtered_df.columns:
            # Handle comma-separated order type list
            order_types = [ot.strip() for ot in filters['order_type'].split(',') if ot.strip()]
            if order_types:
                # Create a mask that matches any of the selected order types
                mask = pd.Series([False] * len(filtered_df), index=filtered_df.index)
                for order_type in order_types:
                    mask |= (filtered_df['Order Type '] == order_type)
                filtered_df = filtered_df[mask]
    
    # Filter by Product Description (supports multiple products)
    if filters.get('product') and filters['product']:
        if 'Product Description' in filtered_df.columns:
            # Handle comma-separated product list
            products = [p.strip() for p in filters['product'].split(',') if p.strip()]
            if products:
                # Create a mask that matches any of the selected products
                # Use the same index as filtered_df to avoid alignment issues
                mask = pd.Series([False] * len(filtered_df), index=filtered_df.index)
                for product in products:
                    mask |= filtered_df['Product Description'].str.contains(
                        product, case=False, na=False
                    )
                filtered_df = filtered_df[mask]
    
    # Filter by Pickup Dates (supports multiple dates)
    if filters.get('pickup_dates') and filters['pickup_dates']:
        if 'Due Pickup Date' in filtered_df.columns:
            # Handle comma-separated list of dates
            pickup_dates = [d.strip() for d in filters['pickup_dates'].split(',') if d.strip()]
            if pickup_dates:
                # Convert dates to datetime for comparison
                pickup_date_objs = []
                for date_str in pickup_dates:
                    try:
                        date_obj = pd.to_datetime(date_str).normalize()
                        pickup_date_objs.append(date_obj)
                    except:
                        pass
                
                if pickup_date_objs:
                    # Filter to rows where Due Pickup Date matches any of the selected dates
                    mask = pd.Series([False] * len(filtered_df), index=filtered_df.index)
                    for date_obj in pickup_date_objs:
                        # Ensure Due Pickup Date is datetime before using .dt
                        if pd.api.types.is_datetime64_any_dtype(filtered_df['Due Pickup Date']):
                            # Compare normalized dates (date only, ignore time)
                            mask |= (
                                filtered_df['Due Pickup Date'].notna() & 
                                (filtered_df['Due Pickup Date'].dt.normalize() == date_obj)
                            )
                        else:
                            # If not datetime, try to parse and compare
                            try:
                                parsed_dates = pd.to_datetime(filtered_df['Due Pickup Date'], errors='coerce')
                                mask |= (
                                    parsed_dates.notna() & 
                                    (parsed_dates.dt.normalize() == date_obj)
                                )
                            except:
                                pass
                    filtered_df = filtered_df[mask]
    
    return filtered_df


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok", "message": "Flask app is working"})

@app.route('/test', methods=['GET'])
def test():
    """Test endpoint to verify Flask is working."""
    return jsonify({
        "status": "ok",
        "message": "Test endpoint working",
        "routes": [str(rule) for rule in app.url_map.iter_rules()]
    })


@app.route('/api/data', methods=['GET'])
def get_data():
    """Get filtered order data."""
    logger.info("=" * 80)
    logger.info("API /api/data called")
    logger.info(f"Request args: {dict(request.args)}")
    try:
        # Get filters from query parameters
        filters = {
            'date_start': request.args.get('date_start'),
            'date_end': request.args.get('date_end'),
            'product': request.args.get('product'),
            'pickup_dates': request.args.get('pickup_dates'),
            'order_type': request.args.get('order_type'),
        }
        logger.info(f"Filters: {filters}")
        
        # Load data
        logger.info("Loading data...")
        try:
            df = load_data()
            logger.info(f"✓ Data loaded successfully. Shape: {df.shape}")
        except Exception as e:
            logger.error(f"✗ Failed to load data: {e}")
            logger.error(traceback.format_exc())
            rate_limit_response = handle_rate_limit_error(e)
            if rate_limit_response:
                return rate_limit_response
            raise
        
        # Apply filters
        filtered_df = filter_data(df, filters)
        
        # Select columns to return
        display_columns = [
            'Due Pickup Date', 'Order Date', 'OrderID', 'Customer First Name', 'Customer Last Name',
            'Product Description', 'Unit Price', 'Subtotal (Calculated)',
            'Due Pickup Time', 'Order Type ', 'Total'
        ]
        
        available_columns = [col for col in display_columns if col in filtered_df.columns]
        result_df = filtered_df[available_columns].copy()
        
        # Convert dates to strings and handle NaN values
        for col in result_df.columns:
            if pd.api.types.is_datetime64_any_dtype(result_df[col]):
                result_df[col] = result_df[col].dt.strftime('%Y-%m-%d')
            elif col in ['Order Date', 'Due Pickup Date', 'Pickup Timestamp', 'Due Date']:
                # Try to parse as datetime if it's a date column
                try:
                    parsed = pd.to_datetime(result_df[col], errors='coerce')
                    result_df[col] = parsed.dt.strftime('%Y-%m-%d')
                except:
                    pass
        
        # Replace NaN/NaT values with None for JSON serialization
        # Use fillna with value parameter instead of replace for better compatibility
        for col in result_df.columns:
            result_df[col] = result_df[col].where(pd.notna(result_df[col]), None)
        
        # Convert to JSON - replace NaN values
        result = result_df.to_dict('records')
        
        # Clean up any remaining NaN values
        for record in result:
            for key, value in record.items():
                try:
                    if pd.isna(value):
                        record[key] = None
                    elif isinstance(value, float) and (pd.isna(value) or str(value) == 'nan'):
                        record[key] = None
                except (TypeError, ValueError):
                    # If value is not a type that can be checked with pd.isna, keep as is
                    pass
        
        return jsonify({
            "success": True,
            "data": result,
            "count": len(result)
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/summary', methods=['GET'])
def get_summary():
    """Get summary statistics."""
    try:
        filters = {
            'date_start': request.args.get('date_start'),
            'date_end': request.args.get('date_end'),
            'product': request.args.get('product'),
            'pickup_dates': request.args.get('pickup_dates'),
            'order_type': request.args.get('order_type'),
        }
        
        try:
            df = load_data()
        except Exception as e:
            rate_limit_response = handle_rate_limit_error(e)
            if rate_limit_response:
                return rate_limit_response
            raise
        
        filtered_df = filter_data(df, filters)
        
        # Calculate summary statistics
        total_orders = len(filtered_df['OrderID'].unique()) if 'OrderID' in filtered_df.columns else 0
        total_items = len(filtered_df)
        
        total_revenue = 0.0
        if 'Subtotal (Calculated)' in filtered_df.columns:
            revenue_series = pd.to_numeric(filtered_df['Subtotal (Calculated)'], errors='coerce')
            total_revenue = float(revenue_series.sum()) if revenue_series.notna().any() else 0.0
            if pd.isna(total_revenue):
                total_revenue = 0.0
        
        order_total = 0.0
        if 'Total' in filtered_df.columns and 'OrderID' in filtered_df.columns:
            try:
                # Get first Total per OrderID (to avoid double counting)
                order_totals = filtered_df.groupby('OrderID')['Total'].first()
                total_series = pd.to_numeric(order_totals, errors='coerce')
                order_total = float(total_series.sum()) if total_series.notna().any() else 0.0
                if pd.isna(order_total):
                    order_total = 0.0
            except Exception:
                order_total = 0.0
        
        # Sales by category
        category_sales = []
        if 'Category' in filtered_df.columns and 'Subtotal (Calculated)' in filtered_df.columns:
            try:
                # Convert to numeric first, then group
                filtered_df_copy = filtered_df.copy()
                filtered_df_copy['Subtotal (Calculated)'] = pd.to_numeric(
                    filtered_df_copy['Subtotal (Calculated)'], 
                    errors='coerce'
                ).fillna(0)
                
                category_df = filtered_df_copy.groupby('Category', as_index=False).agg({
                    'Subtotal (Calculated)': 'sum'
                })
                
                category_sales = []
                for _, row in category_df.iterrows():
                    category_sales.append({
                        'Category': str(row['Category']) if pd.notna(row['Category']) else '',
                        'Subtotal (Calculated)': float(row['Subtotal (Calculated)']) if pd.notna(row['Subtotal (Calculated)']) else 0.0
                    })
            except Exception as e:
                category_sales = []
        
        # Sales by product (Top 10)
        product_sales = []
        if 'Product Description' in filtered_df.columns and 'Subtotal (Calculated)' in filtered_df.columns:
            try:
                # Convert to numeric first, then group
                filtered_df_copy = filtered_df.copy()
                filtered_df_copy['Subtotal (Calculated)'] = pd.to_numeric(
                    filtered_df_copy['Subtotal (Calculated)'], 
                    errors='coerce'
                ).fillna(0)
                
                product_df = filtered_df_copy.groupby('Product Description', as_index=False).agg({
                    'Subtotal (Calculated)': 'sum'
                })
                product_df = product_df.sort_values('Subtotal (Calculated)', ascending=False).head(10)  # Top 10
                
                product_sales = []
                for _, row in product_df.iterrows():
                    product_sales.append({
                        'Product Description': str(row['Product Description']) if pd.notna(row['Product Description']) else 'Unknown',
                        'Subtotal (Calculated)': float(row['Subtotal (Calculated)']) if pd.notna(row['Subtotal (Calculated)']) else 0.0
                    })
            except Exception as e:
                product_sales = []
        
        # Sales by order type
        order_type_sales = []
        if 'Order Type ' in filtered_df.columns and 'Total' in filtered_df.columns:
            try:
                filtered_df_copy = filtered_df.copy()
                filtered_df_copy['Total'] = pd.to_numeric(filtered_df_copy['Total'], errors='coerce').fillna(0)
                
                order_type_df = filtered_df_copy.groupby('Order Type ', as_index=False).agg({
                    'Total': 'sum'
                })
                
                order_type_sales = []
                for _, row in order_type_df.iterrows():
                    order_type_sales.append({
                        'Order Type ': str(row['Order Type ']) if pd.notna(row['Order Type ']) else '',
                        'Total': float(row['Total']) if pd.notna(row['Total']) else 0.0
                    })
            except Exception as e:
                order_type_sales = []
        
        # Daily sales trend
        daily_sales = []
        if 'Order Date' in filtered_df.columns and filtered_df['Order Date'].notna().any():
            try:
                # Convert to numeric first before grouping
                filtered_df_copy = filtered_df.copy()
                filtered_df_copy['Subtotal (Calculated)'] = pd.to_numeric(
                    filtered_df_copy['Subtotal (Calculated)'], 
                    errors='coerce'
                ).fillna(0)
                
                # Ensure Order Date is datetime before using .dt
                if not pd.api.types.is_datetime64_any_dtype(filtered_df_copy['Order Date']):
                    filtered_df_copy['Order Date'] = pd.to_datetime(filtered_df_copy['Order Date'], errors='coerce')
                
                daily_df = filtered_df_copy.groupby(filtered_df_copy['Order Date'].dt.date).agg({
                    'Subtotal (Calculated)': 'sum',
                    'OrderID': 'nunique'
                }).reset_index()
                
                daily_df.columns = ['Date', 'Revenue', 'Orders']
                daily_df['Date'] = daily_df['Date'].astype(str)
                daily_df['Revenue'] = pd.to_numeric(daily_df['Revenue'], errors='coerce').fillna(0)
                daily_df['Orders'] = pd.to_numeric(daily_df['Orders'], errors='coerce').fillna(0)
                
                daily_sales = []
                for _, row in daily_df.iterrows():
                    daily_sales.append({
                        'Date': str(row['Date']),
                        'Revenue': float(row['Revenue']) if pd.notna(row['Revenue']) else 0.0,
                        'Orders': int(row['Orders']) if pd.notna(row['Orders']) else 0
                    })
            except Exception as e:
                daily_sales = []
        
        # Ensure all values are JSON serializable
        summary_data = {
            "total_orders": int(total_orders),
            "total_items": int(total_items),
            "total_revenue": float(total_revenue) if not pd.isna(total_revenue) else 0.0,
            "order_total": float(order_total) if not pd.isna(order_total) else 0.0
        }
        
        return jsonify({
            "success": True,
            "summary": summary_data,
            "category_sales": category_sales,
            "product_sales": product_sales,
            "order_type_sales": order_type_sales,
            "daily_sales": daily_sales
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/products', methods=['GET'])
def get_products():
    """Get list of all products."""
    try:
        df = load_data()
        if 'Product Description' in df.columns:
            products = sorted(df['Product Description'].dropna().unique().tolist())
            return jsonify({
                "success": True,
                "products": products
            })
        else:
            return jsonify({
                "success": True,
                "products": []
            })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


def handle_rate_limit_error(e):
    """Handle Google Sheets API rate limit and authentication errors."""
    error_str = str(e)
    
    # Rate limit errors
    if '429' in error_str or 'RATE_LIMIT' in error_str or 'RESOURCE_EXHAUSTED' in error_str:
        return jsonify({
            "success": False,
            "error": "Google Sheets API rate limit exceeded (60 requests/minute). Please wait a minute and refresh, or request a quota increase at https://cloud.google.com/docs/quotas/help/request_increase",
            "rate_limited": True
        }), 429
    
    # Authentication errors
    if '401' in error_str or 'Unauthorized' in error_str or 'invalid_grant' in error_str or 'Invalid credentials' in error_str:
        return jsonify({
            "success": False,
            "error": "Google Sheets API authentication failed. Please check that GOOGLE_CREDENTIALS_BASE64 environment variable is set correctly in Vercel.",
            "auth_error": True,
            "details": "Make sure the credentials are base64-encoded and the service account has access to the spreadsheet."
        }), 401
    
    return None

@app.route('/api/date-range', methods=['GET'])
def get_date_range():
    """Get min/max dates for filtering."""
    try:
        try:
            df = load_data()
        except Exception as e:
            rate_limit_response = handle_rate_limit_error(e)
            if rate_limit_response:
                return rate_limit_response
            raise
        
        result = {}
        
        if 'Order Date' in df.columns and df['Order Date'].notna().any():
            result['order_date_min'] = df['Order Date'].min().strftime('%Y-%m-%d')
            result['order_date_max'] = df['Order Date'].max().strftime('%Y-%m-%d')
        
        return jsonify({
            "success": True,
            "date_range": result
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/pickup-dates', methods=['GET'])
def get_pickup_dates():
    """Get list of all unique pickup dates."""
    try:
        try:
            df = load_data()
        except Exception as e:
            rate_limit_response = handle_rate_limit_error(e)
            if rate_limit_response:
                return rate_limit_response
            raise
        
        if 'Due Pickup Date' in df.columns:
            # Check if column contains datetime values
            if df['Due Pickup Date'].dtype == 'datetime64[ns]' or pd.api.types.is_datetime64_any_dtype(df['Due Pickup Date']):
                # Get unique dates, normalize to date only (remove time)
                unique_dates = df['Due Pickup Date'].dropna().dt.normalize().unique()
                # Convert to YYYY-MM-DD format strings
                pickup_dates = sorted([pd.Timestamp(date).strftime('%Y-%m-%d') for date in unique_dates], reverse=True)
            else:
                # If not datetime, try to parse and get unique dates
                # Convert to string first, then parse
                date_strings = df['Due Pickup Date'].dropna().astype(str)
                date_strings = date_strings[date_strings.str.strip() != '']
                date_strings = date_strings[~date_strings.str.lower().isin(['nan', 'none', 'nat'])]
                
                if len(date_strings) > 0:
                    # Parse dates
                    parsed_dates = pd.to_datetime(date_strings, errors='coerce')
                    unique_dates = parsed_dates.dropna().dt.normalize().unique()
                    pickup_dates = sorted([pd.Timestamp(date).strftime('%Y-%m-%d') for date in unique_dates], reverse=True)
                else:
                    pickup_dates = []
            
            return jsonify({
                "success": True,
                "pickup_dates": pickup_dates
            })
        else:
            return jsonify({
                "success": True,
                "pickup_dates": []
            })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/export/pdf', methods=['GET'])
def export_pdf():
    """Export filtered order data as PDF."""
    try:
        from io import BytesIO
        from flask import send_file
        
        # Get filters from query parameters
        filters = {
            'date_start': request.args.get('date_start'),
            'date_end': request.args.get('date_end'),
            'product': request.args.get('product'),
            'pickup_dates': request.args.get('pickup_dates'),
            'order_type': request.args.get('order_type'),
        }
        
        # Load and filter data
        try:
            df = load_data()
        except Exception as e:
            rate_limit_response = handle_rate_limit_error(e)
            if rate_limit_response:
                return rate_limit_response
            raise
        
        filtered_df = filter_data(df, filters)
        
        if len(filtered_df) == 0:
            return jsonify({
                "success": False,
                "error": "No data to export"
            }), 400
        
        # Group data by OrderID and Due Pickup Date (same logic as frontend)
        orders_by_id = {}
        for _, row in filtered_df.iterrows():
            order_id = row.get('OrderID', '')
            if order_id not in orders_by_id:
                orders_by_id[order_id] = []
            orders_by_id[order_id].append(row)
        
        # Group orders by Due Pickup Date
        grouped_by_date = {}
        for order_id, order_rows in orders_by_id.items():
            first_row = order_rows[0]
            pickup_date = first_row.get('Due Pickup Date', '')
            date_key = 'No Date'
            if pickup_date and pd.notna(pickup_date):
                try:
                    if isinstance(pickup_date, pd.Timestamp):
                        date_key = pickup_date.strftime('%m/%d/%Y')
                    else:
                        date_key = pd.to_datetime(pickup_date).strftime('%m/%d/%Y')
                except:
                    date_key = str(pickup_date)
            
            if date_key not in grouped_by_date:
                grouped_by_date[date_key] = []
            grouped_by_date[date_key].append({
                'order_id': order_id,
                'rows': order_rows
            })
        
        # Sort dates
        sorted_dates = sorted(grouped_by_date.keys(), key=lambda x: (
            1 if x == 'No Date' else 0,
            pd.to_datetime(x, errors='coerce') if x != 'No Date' else pd.Timestamp.min
        ), reverse=True)
        
        # Create PDF in memory
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
        story = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=20,
            alignment=1
        )
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=8,
            spaceBefore=12
        )
        normal_style = styles['Normal']
        
        # Title
        title = Paragraph("Order Details Report", title_style)
        story.append(title)
        
        # Date range info
        if filters.get('date_start') or filters.get('date_end'):
            date_range_text = "Date Range: "
            if filters.get('date_start'):
                date_range_text += filters['date_start']
            if filters.get('date_end'):
                date_range_text += f" to {filters['date_end']}"
            story.append(Paragraph(date_range_text, normal_style))
            story.append(Spacer(1, 0.2*inch))
        
        # Generate timestamp
        timestamp = Paragraph(
            f"Generated: {pd.Timestamp.now().strftime('%B %d, %Y at %I:%M %p')}",
            normal_style
        )
        story.append(timestamp)
        story.append(Spacer(1, 0.3*inch))
        
        # Define columns
        columns = ['Due Pickup Date', 'Due Pickup Time', 'Customer Name', 'Product Description', 'Order Date', 'OrderID']
        
        # Build table data
        table_data = [columns]  # Header row
        
        for date_key in sorted_dates:
            orders = grouped_by_date[date_key]
            
            # Date group header
            weekday = ''
            if date_key != 'No Date':
                try:
                    date_obj = pd.to_datetime(date_key)
                    weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                    weekday = f" ({weekdays[date_obj.weekday()]})"
                except:
                    pass
            
            # Add date separator row
            date_header = [''] * len(columns)
            date_header[0] = f"Due Pickup Date: {date_key}{weekday}"
            table_data.append(date_header)
            
            # Process each order
            for order in orders:
                order_rows = order['rows']
                first_row = order_rows[0]
                is_multi_line = len(order_rows) > 1
                
                # Order header row (for multi-line orders)
                if is_multi_line:
                    first_name = first_row.get('Customer First Name', '') or ''
                    last_name = first_row.get('Customer Last Name', '') or ''
                    full_name = f"{first_name} {last_name}".strip()
                    
                    order_header = [''] * len(columns)
                    order_header[0] = format_cell_value(first_row.get('Due Pickup Date'), 'Due Pickup Date')
                    order_header[1] = format_cell_value(first_row.get('Due Pickup Time'), 'Due Pickup Time')
                    order_header[2] = full_name
                    order_header[3] = f"Order: {len(order_rows)} items"
                    order_header[4] = format_cell_value(first_row.get('Order Date'), 'Order Date')
                    order_header[5] = format_cell_value(first_row.get('OrderID'), 'OrderID')
                    table_data.append(order_header)
                
                # Line items
                for idx, row in enumerate(order_rows):
                    line_item = [''] * len(columns)
                    
                    if is_multi_line:
                        # Only show product description for line items
                        line_item[3] = format_cell_value(row.get('Product Description'), 'Product Description')
                    else:
                        # Single item order - show all fields
                        first_name = row.get('Customer First Name', '') or ''
                        last_name = row.get('Customer Last Name', '') or ''
                        full_name = f"{first_name} {last_name}".strip()
                        
                        line_item[0] = format_cell_value(row.get('Due Pickup Date'), 'Due Pickup Date')
                        line_item[1] = format_cell_value(row.get('Due Pickup Time'), 'Due Pickup Time')
                        line_item[2] = full_name
                        line_item[3] = format_cell_value(row.get('Product Description'), 'Product Description')
                        line_item[4] = format_cell_value(row.get('Order Date'), 'Order Date')
                        line_item[5] = format_cell_value(row.get('OrderID'), 'OrderID')
                    
                    table_data.append(line_item)
        
        # Create table
        col_widths = [1.2*inch, 1*inch, 1.5*inch, 2.5*inch, 1*inch, 1*inch]
        pdf_table = Table(table_data, colWidths=col_widths, repeatRows=1)
        
        # Build table style - identify row types first
        table_style_commands = [
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 0), (-1, 0), 10),
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            
            # Default data rows
            ('FONTSIZE', (0, 1), (-1, -1), 8),
        ]
        
        # Apply styles to specific rows based on content
        for row_idx in range(1, len(table_data)):
            row_data = table_data[row_idx]
            first_cell = str(row_data[0]) if row_data[0] else ''
            product_cell = str(row_data[3]) if len(row_data) > 3 and row_data[3] else ''
            
            # Date header rows
            if first_cell.startswith('Due Pickup Date:'):
                table_style_commands.extend([
                    ('BACKGROUND', (0, row_idx), (-1, row_idx), colors.HexColor('#f0f0f0')),
                    ('FONTNAME', (0, row_idx), (-1, row_idx), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, row_idx), (-1, row_idx), 10),
                ])
            # Order header rows (multi-line orders)
            elif 'Order:' in product_cell and 'items' in product_cell:
                table_style_commands.extend([
                    ('BACKGROUND', (0, row_idx), (-1, row_idx), colors.HexColor('#e8f4f8')),
                    ('FONTNAME', (0, row_idx), (-1, row_idx), 'Helvetica-Bold'),
                ])
            # Regular data rows - alternate background
            else:
                bg_color = colors.white if row_idx % 2 == 1 else colors.HexColor('#f8f9fa')
                table_style_commands.append(('BACKGROUND', (0, row_idx), (-1, row_idx), bg_color))
        
        pdf_table.setStyle(TableStyle(table_style_commands))
        story.append(pdf_table)
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        
        # Generate filename
        filename = f"order_report_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        return send_file(
            buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/export/product-by-day/pdf', methods=['GET'])
def export_product_by_day_pdf():
    """Export Product by Day report as PDF."""
    try:
        from io import BytesIO
        from flask import send_file
        
        # Get filters from query parameters
        filters = {
            'date_start': request.args.get('date_start'),
            'date_end': request.args.get('date_end'),
            'product': request.args.get('product'),
            'pickup_dates': request.args.get('pickup_dates'),
            'order_type': request.args.get('order_type'),
        }
        
        # Load and filter data
        try:
            df = load_data()
        except Exception as e:
            rate_limit_response = handle_rate_limit_error(e)
            if rate_limit_response:
                return rate_limit_response
            raise
        
        filtered_df = filter_data(df, filters)
        
        if len(filtered_df) == 0:
            return jsonify({
                "success": False,
                "error": "No data to export"
            }), 400
        
        # Group data by Due Pickup Date, then by Product Description
        day_product_map = {}
        
        for _, row in filtered_df.iterrows():
            product = row.get('Product Description', 'Unknown Product')
            pickup_date = row.get('Due Pickup Date', '')
            
            # Format date key
            date_key = 'No Date'
            date_display = 'No Date'
            if pickup_date and pd.notna(pickup_date):
                try:
                    if isinstance(pickup_date, pd.Timestamp):
                        date_obj = pickup_date
                    else:
                        date_obj = pd.to_datetime(pickup_date, errors='coerce')
                    
                    if pd.notna(date_obj):
                        date_key = date_obj.strftime('%Y-%m-%d')
                        # Format date for display with weekday
                        weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                        weekday = weekdays[date_obj.weekday()]
                        date_display = date_obj.strftime(f'{weekday}, %b %d, %Y')
                except:
                    date_key = str(pickup_date)
                    date_display = str(pickup_date)
            
            # Initialize date group if needed
            if date_key not in day_product_map:
                day_product_map[date_key] = {
                    'date_display': date_display,
                    'products': {}
                }
            
            # Count products for this date
            if product not in day_product_map[date_key]['products']:
                day_product_map[date_key]['products'][product] = 0
            day_product_map[date_key]['products'][product] += 1
        
        # Sort dates ascending (oldest first)
        sorted_dates = sorted(day_product_map.keys(), key=lambda x: (
            1 if x == 'No Date' else 0,
            pd.to_datetime(x, errors='coerce') if x != 'No Date' else pd.Timestamp.min
        ))
        
        # Create PDF in memory
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
        story = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=20,
            alignment=1
        )
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=8,
            spaceBefore=12
        )
        normal_style = styles['Normal']
        
        # Title
        title = Paragraph("Product by Day Report", title_style)
        story.append(title)
        
        # Date range info
        if filters.get('date_start') or filters.get('date_end'):
            date_range_text = "Date Range: "
            if filters.get('date_start'):
                date_range_text += filters['date_start']
            if filters.get('date_end'):
                date_range_text += f" to {filters['date_end']}"
            story.append(Paragraph(date_range_text, normal_style))
            story.append(Spacer(1, 0.2*inch))
        
        # Generate timestamp
        timestamp = Paragraph(
            f"Generated: {pd.Timestamp.now().strftime('%B %d, %Y at %I:%M %p')}",
            normal_style
        )
        story.append(timestamp)
        story.append(Spacer(1, 0.3*inch))
        
        # Process each day
        grand_total = 0
        for date_key in sorted_dates:
            day_data = day_product_map[date_key]
            products = sorted(day_data['products'].keys())
            
            # Day header
            day_header = Paragraph(day_data['date_display'], heading_style)
            story.append(day_header)
            story.append(Spacer(1, 0.1*inch))
            
            # Products table for this day
            table_data = [['Product Description', 'Quantity']]  # Header row
            
            day_total = 0
            for product in products:
                count = day_data['products'][product]
                day_total += count
                table_data.append([product, str(count)])
            
            # Day total row
            table_data.append(['Total', str(day_total)])
            grand_total += day_total
            
            # Create table
            col_widths = [4.5*inch, 1.5*inch]
            pdf_table = Table(table_data, colWidths=col_widths, repeatRows=1)
            
            # Table style
            table_style_commands = [
                # Header row
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('TOPPADDING', (0, 0), (-1, 0), 10),
                
                # Grid
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                
                # Default data rows
                ('FONTSIZE', (0, 1), (-1, -2), 9),
                
                # Total row
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f0f0f0')),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, -1), (-1, -1), 10),
                ('TOPPADDING', (0, -1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, -1), (-1, -1), 8),
            ]
            
            pdf_table.setStyle(TableStyle(table_style_commands))
            story.append(pdf_table)
            story.append(Spacer(1, 0.3*inch))
        
        # Grand total
        grand_total_para = Paragraph(
            f"<b>Total Line Items: {grand_total:,}</b>",
            ParagraphStyle(
                'GrandTotal',
                parent=styles['Normal'],
                fontSize=12,
                textColor=colors.HexColor('#1a1a1a'),
                alignment=1,
                spaceBefore=12
            )
        )
        story.append(grand_total_para)
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        
        # Generate filename
        filename = f"product_by_day_report_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        return send_file(
            buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


def format_cell_value(value, col_name):
    """Format cell value for PDF display."""
    if pd.isna(value) or value is None or value == '':
        return ''
    elif isinstance(value, (int, float)):
        if 'Price' in col_name or 'Total' in col_name or 'Revenue' in col_name or 'Subtotal' in col_name:
            return f"${value:.2f}"
        else:
            return str(int(value))
    elif isinstance(value, pd.Timestamp):
        return value.strftime('%m/%d/%Y')
    else:
        str_val = str(value)
        # Truncate long values
        if len(str_val) > 50:
            return str_val[:47] + '...'
        return str_val


# Serve static files and frontend (must be after all API routes)
@app.route('/', methods=['GET'])
def index():
    """Serve the frontend index page."""
    logger.info("Root route (/) called")
    from flask import Response
    import os
    
    try:
        # Get the directory where this file is located
        current_dir = os.path.dirname(os.path.abspath(__file__))
        logger.info(f"Current directory (from __file__): {current_dir}")
        logger.info(f"Working directory (os.getcwd()): {os.getcwd()}")
        
        public_dir = os.path.join(current_dir, 'public')
        index_path = os.path.join(public_dir, 'index.html')
        logger.info(f"Looking for index.html at: {index_path}")
        logger.info(f"File exists: {os.path.exists(index_path)}")
        
        # Try to read the file
        if os.path.exists(index_path):
            logger.info("✓ Found index.html at primary path")
            with open(index_path, 'r', encoding='utf-8') as f:
                content = f.read()
            logger.info(f"✓ Read index.html successfully ({len(content)} characters)")
            return Response(content, mimetype='text/html; charset=utf-8')
        else:
            # Try alternative paths
            logger.info("Primary path not found, trying alternatives...")
            alt_paths = [
                os.path.join(os.getcwd(), 'public', 'index.html'),
                'public/index.html',
                './public/index.html',
            ]
            for alt_path in alt_paths:
                logger.info(f"Trying: {alt_path} (exists: {os.path.exists(alt_path)})")
                if os.path.exists(alt_path):
                    logger.info(f"✓ Found index.html at alternative path: {alt_path}")
                    with open(alt_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    return Response(content, mimetype='text/html; charset=utf-8')
            
            # Return error with debug info
            error_msg = f"index.html not found. Current dir: {os.getcwd()}, __file__: {__file__}, checked: {index_path}, {alt_paths}"
            logger.error(f"✗ {error_msg}")
            return Response(error_msg, status=404, mimetype='text/plain')
    except Exception as e:
        error_msg = f"Error reading index.html: {str(e)}. Current dir: {os.getcwd()}, __file__: {__file__}"
        logger.error(f"✗ {error_msg}")
        logger.error(traceback.format_exc())
        return Response(error_msg, status=500, mimetype='text/plain')

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files from public directory, excluding API routes."""
    # Skip API routes - they're handled by specific route handlers above
    if path.startswith('api/'):
        from flask import abort
        abort(404)
    
    from flask import send_from_directory, send_file
    import os
    public_dir = os.path.join(os.path.dirname(__file__), 'public')
    
    # Check if it's a file in public directory
    file_path = os.path.join(public_dir, path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return send_file(file_path)
    
    # If file not found, serve index.html for SPA routing
    index_path = os.path.join(public_dir, 'index.html')
    if os.path.exists(index_path):
        return send_file(index_path)
    
    # If index.html doesn't exist, return 404
    from flask import abort
    abort(404)

# Export handler for Vercel
# Vercel expects the Flask app to be accessible as 'app' or 'handler'
try:
    handler = app
    __all__ = ['app', 'handler']
    emergency_log("✓ Handler exported successfully")
    logger.info("✓ Handler exported successfully")
except Exception as e:
    error_msg = f"CRITICAL: Failed to export handler: {e}"
    emergency_log(error_msg)
    emergency_log(traceback.format_exc())
    # Create a minimal error app as fallback
    try:
        from flask import Flask, jsonify
        error_app = Flask(__name__)
        @error_app.route('/', defaults={'path': ''})
        @error_app.route('/<path:path>')
        def error_handler(path):
            return jsonify({
                "error": f"Failed to initialize Flask app: {str(e)}",
                "traceback": traceback.format_exc(),
                "path": path
            }), 500
        handler = error_app
        app = error_app
        emergency_log("✓ Error handler app created as fallback")
    except Exception as e2:
        emergency_log(f"CRITICAL: Failed to create error handler: {e2}")
        emergency_log(traceback.format_exc())
        raise

# For local development and traditional hosting (Railway, Render, etc.)
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=True, port=port, host='0.0.0.0')

