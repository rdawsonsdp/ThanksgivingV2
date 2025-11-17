"""
Shared utilities for API functions
This module contains common functions used across all API endpoints
"""

import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import os
import json
import base64
import time

# Google Sheets configuration
SPREADSHEET_ID = "1YAHO5rHhFVEReyAuxa7r2SDnoH7BnDfsmSEZ1LyjB8A"
CUSTOMER_ORDERS_SHEET_NAME = "Customer Orders"
BAKERY_PRODUCTS_SHEET_NAME = "Bakery Products Ordered "

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly"
]

# Cache for data loading to reduce API calls
_data_cache = None
_cache_timestamp = None
CACHE_DURATION = 300  # Cache for 5 minutes


def get_credentials():
    """Get Google Sheets credentials from environment variable or file."""
    # Try environment variable first (for Vercel deployment)
    if 'GOOGLE_CREDENTIALS_BASE64' in os.environ:
        creds_json = json.loads(base64.b64decode(os.environ['GOOGLE_CREDENTIALS_BASE64']))
        return Credentials.from_service_account_info(creds_json, scopes=SCOPES)
    
    # Fallback to file (for local development)
    creds_path = os.path.join(os.path.dirname(__file__), "long-canto-360620-6858c5a01c13.json")
    return Credentials.from_service_account_file(creds_path, scopes=SCOPES)


def load_data():
    """Load and merge data from Google Sheets with caching."""
    global _data_cache, _cache_timestamp
    
    current_time = time.time()
    
    # Return cached data if available and not expired
    if _data_cache is not None and _cache_timestamp is not None:
        if current_time - _cache_timestamp < CACHE_DURATION:
            return _data_cache
    
    try:
        creds = get_credentials()
        client = gspread.authorize(creds)
        
        # Read Customer Orders
        spreadsheet = client.open_by_key(SPREADSHEET_ID)
        orders_sheet = spreadsheet.worksheet(CUSTOMER_ORDERS_SHEET_NAME)
        customer_orders_data = orders_sheet.get_all_records()
        customer_orders_df = pd.DataFrame(customer_orders_data)
        
        # Read Bakery Products
        products_sheet = spreadsheet.worksheet(BAKERY_PRODUCTS_SHEET_NAME)
        bakery_products_data = products_sheet.get_all_records()
        bakery_products_df = pd.DataFrame(bakery_products_data)
        
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
                how='inner',
                suffixes=('', '_product')
            )
        else:
            merged_df = customer_orders_df
        
        # Update cache
        _data_cache = merged_df
        _cache_timestamp = current_time
        
        return merged_df
    except Exception as e:
        if _data_cache is not None:
            return _data_cache
        raise Exception(f"Error loading data: {str(e)}")


def parse_dates(df):
    """Parse date columns from various formats."""
    df = df.copy()
    
    # Parse Order Date
    if 'Order Date' in df.columns:
        df['Order Date'] = df['Order Date'].astype(str).replace(['nan', 'None', ''], '')
        df['Order Date'] = pd.to_datetime(df['Order Date'], errors='coerce', format='%m-%d-%Y')
        mask_not_parsed = df['Order Date'].isna()
        if mask_not_parsed.any():
            df.loc[mask_not_parsed, 'Order Date'] = pd.to_datetime(
                df.loc[mask_not_parsed, 'Order Date'],
                errors='coerce',
                format='%m/%d/%Y'
            )
        mask_still_not_parsed = df['Order Date'].isna()
        if mask_still_not_parsed.any():
            df.loc[mask_still_not_parsed, 'Order Date'] = pd.to_datetime(
                df.loc[mask_still_not_parsed, 'Order Date'],
                errors='coerce',
                dayfirst=False,
                yearfirst=False
            )
    
    # Parse Due Pickup Date
    if 'Due Pickup Date' in df.columns:
        original_col = df['Due Pickup Date'].copy()
        df['Due Pickup Date'] = df['Due Pickup Date'].astype(str)
        df['Due Pickup Date'] = df['Due Pickup Date'].replace(['nan', 'None', 'NaT', 'NaN'], '')
        
        mask_not_empty = df['Due Pickup Date'].str.strip() != ''
        
        if mask_not_empty.any():
            original_strings = original_col.astype(str).replace(['nan', 'None', 'NaT', 'NaN'], '')
            
            parsed_dates = pd.to_datetime(
                original_strings.loc[mask_not_empty], 
                errors='coerce', 
                format='%m-%d-%Y'
            )
            df.loc[mask_not_empty, 'Due Pickup Date'] = parsed_dates
            
            mask_not_parsed = df['Due Pickup Date'].isna() & mask_not_empty
            if mask_not_parsed.any():
                df.loc[mask_not_parsed, 'Due Pickup Date'] = pd.to_datetime(
                    original_strings.loc[mask_not_parsed], 
                    errors='coerce', 
                    format='%m/%d/%Y'
                )
            
            mask_still_not_parsed = df['Due Pickup Date'].isna() & mask_not_empty
            if mask_still_not_parsed.any():
                df.loc[mask_still_not_parsed, 'Due Pickup Date'] = pd.to_datetime(
                    original_strings.loc[mask_still_not_parsed], 
                    errors='coerce', 
                    dayfirst=False, 
                    yearfirst=False
                )
    
    # Parse Pickup Timestamp
    if 'Pickup Timestamp' in df.columns:
        df['Pickup Timestamp'] = df['Pickup Timestamp'].astype(str).replace(['nan', 'None', ''], '')
        df['Pickup Timestamp'] = pd.to_datetime(df['Pickup Timestamp'], errors='coerce', dayfirst=False, yearfirst=False)
    
    # Parse Due Date
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
        start_date = pd.Timestamp(filters['date_start']).normalize()
        filtered_df = filtered_df[filtered_df['Order Date'].notna() & (filtered_df['Order Date'] >= start_date)]
    if filters.get('date_end'):
        end_date = pd.Timestamp(filters['date_end']).normalize() + pd.Timedelta(days=1) - pd.Timedelta(microseconds=1)
        filtered_df = filtered_df[filtered_df['Order Date'].notna() & (filtered_df['Order Date'] <= end_date)]
    
    # Filter by Order Type
    if filters.get('order_type') and filters['order_type']:
        if 'Order Type ' in filtered_df.columns:
            order_types = [ot.strip() for ot in filters['order_type'].split(',') if ot.strip()]
            if order_types:
                mask = pd.Series([False] * len(filtered_df), index=filtered_df.index)
                for order_type in order_types:
                    mask |= (filtered_df['Order Type '] == order_type)
                filtered_df = filtered_df[mask]
    
    # Filter by Product Description
    if filters.get('product') and filters['product']:
        if 'Product Description' in filtered_df.columns:
            products = [p.strip() for p in filters['product'].split(',') if p.strip()]
            if products:
                mask = pd.Series([False] * len(filtered_df), index=filtered_df.index)
                for product in products:
                    mask |= filtered_df['Product Description'].str.contains(
                        product, case=False, na=False
                    )
                filtered_df = filtered_df[mask]
    
    # Filter by Pickup Dates
    if filters.get('pickup_dates') and filters['pickup_dates']:
        if 'Due Pickup Date' in filtered_df.columns:
            pickup_dates = [d.strip() for d in filters['pickup_dates'].split(',') if d.strip()]
            if pickup_dates:
                pickup_date_objs = []
                for date_str in pickup_dates:
                    try:
                        date_obj = pd.to_datetime(date_str).normalize()
                        pickup_date_objs.append(date_obj)
                    except:
                        pass
                
                if pickup_date_objs:
                    mask = pd.Series([False] * len(filtered_df), index=filtered_df.index)
                    for date_obj in pickup_date_objs:
                        if pd.api.types.is_datetime64_any_dtype(filtered_df['Due Pickup Date']):
                            mask |= (
                                filtered_df['Due Pickup Date'].notna() & 
                                (filtered_df['Due Pickup Date'].dt.normalize() == date_obj)
                            )
                        else:
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


def handle_rate_limit_error(e):
    """Handle Google Sheets API rate limit errors."""
    error_str = str(e)
    if '429' in error_str or 'RESOURCE_EXHAUSTED' in error_str or 'quota' in error_str.lower():
        from flask import jsonify
        return jsonify({
            "success": False,
            "error": "Google Sheets API rate limit exceeded. Please wait a minute and try again.",
            "rate_limited": True
        }), 429
    return None

