#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import pandas as pd
from datetime import datetime
import time
import os
import re
from dateutil import parser as date_parser
import pytz
import csv
import subprocess
import tempfile

def get_trump_truth_posts(start_date=None, end_date=None, max_pages=10):
    """
    Directly use the system's curl command to retrieve Trump's Truth Social posts from Roll Call API
    
    Parameters:
    - start_date: Start date (datetime object), if None, no start date restriction
    - end_date: End date (datetime object), if None, no end date restriction
    - max_pages: Maximum number of pages, default is 10 pages
    
    Returns:
    - List of Truth Social posts within the specified date range
    """
    all_truth_posts = []
    processed_ids = set()
    
    # Ensure start and end dates are datetime objects with timezone
    if start_date and start_date.tzinfo is None:
        start_date = pytz.UTC.localize(start_date)
    if end_date and end_date.tzinfo is None:
        end_date = pytz.UTC.localize(end_date)
    
    # API URL - Using known available API endpoint
    api_url_base = "https://rollcall.com/wp-json/factbase/v1/twitter"
    
    # Force fetching multiple pages of data
    for page in range(1, max_pages + 1):
        print(f"Fetching page {page} data...")
        
        # Build curl command
        api_url = f"{api_url_base}?platform=truth+social&sort=date&sort_order=desc&page={page}"
        print(f"Request URL: {api_url}")
        
        try:
            # Use system's curl command to get data
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
            temp_file.close()
            
            # Build curl command
            curl_cmd = [
                'curl',
                '-s',  # Silent mode
                '-o', temp_file.name,  # Output to temporary file
                api_url
            ]
            
            # Execute curl command
            print(f"Executing: {' '.join(curl_cmd)}")
            curl_process = subprocess.run(curl_cmd, check=True)
            
            # Read data from temporary file
            with open(temp_file.name, 'r', encoding='utf-8') as f:
                response_text = f.read()
            
            # Delete temporary file
            os.unlink(temp_file.name)
            
            # Parse JSON response
            data = json.loads(response_text)
            
            if page == 1:  # Only print data structure for the first page
                print("API response data structure:")
                print(f"Data type: {type(data)}")
                if isinstance(data, dict):
                    print(f"Top level keys: {list(data.keys())}")
                    if "meta" in data:
                        print(f"Total records: {data['meta'].get('total_hits', 0)}")
                        print(f"Total pages: {data['meta'].get('page_count', 0)}")
                    
                    if "meta" in data:
                        print(f"Metadata: {json.dumps(data['meta'], indent=2)}")
                        if "pagination" in data["meta"]:
                            print(f"Pagination info: {json.dumps(data['meta']['pagination'], indent=2)}")
            
            if not data or "data" not in data or not data["data"]:
                print(f"Page {page} has no data, ending retrieval")
                break  # Exit the loop if no data, don't continue to the next page
            
            items = data["data"]
            print(f"Found {len(items)} records")
            
            # Print current page's date range for debugging
            if items:
                first_date = date_parser.parse(items[0]["date"]) if "date" in items[0] else None
                last_date = date_parser.parse(items[-1]["date"]) if "date" in items[-1] else None
                if first_date and last_date:
                    print(f"Current page date range: {first_date.strftime('%Y-%m-%d')} to {last_date.strftime('%Y-%m-%d')}")
            
            total_posts_page = 0
            records_in_range = 0  # Count records within date range on current page
            
            # Process each post
            for post in items:
                # Check if already processed
                post_id = post.get("id")
                
                if post_id and post_id in processed_ids:
                    continue
                
                if post_id:
                    processed_ids.add(post_id)
                    total_posts_page += 1
                
                # Get date
                post_date = None
                if "date" in post:
                    try:
                        # Use dateutil to parse ISO format date (with timezone)
                        post_date = date_parser.parse(post["date"])
                    except Exception as e:
                        print(f"Error parsing date {post_id}: {e}")
                
                # Check date range
                in_range = True
                if post_date:
                    if start_date and post_date < start_date:
                        in_range = False
                        print(f"Post {post_id} date {post_date.strftime('%Y-%m-%d')} is earlier than start date {start_date.strftime('%Y-%m-%d')}")
                    if end_date and post_date > end_date:
                        in_range = False
                        print(f"Post {post_id} date {post_date.strftime('%Y-%m-%d')} is later than end date {end_date.strftime('%Y-%m-%d')}")
                else:
                    # If no date, consider not in range by default
                    in_range = False
                    print(f"Post {post_id} has no valid date, not included in results")
                
                # Extract required fields
                truth_post_data = {
                    "id": post_id,
                    "date": post_date.strftime("%Y-%m-%d %H:%M:%S") if post_date else None,
                    "text": post.get("text", ""),
                    "post_url": post.get("post_url", ""),
                    "image_url": post.get("image_url", ""),
                    "platform": post.get("platform", "Truth Social"),
                    "handle": post.get("handle", "realDonaldTrump"),
                    "speaker": post.get("speaker", "Donald Trump"),
                    "deleted_flag": post.get("deleted_flag", False),
                    "account_url": post.get("account_url", "")
                }
                
                # Extract post ID from URL
                if truth_post_data["post_url"] and not truth_post_data.get("post_id"):
                    match = re.search(r'posts/(\d+)', truth_post_data["post_url"])
                    if match:
                        truth_post_data["post_id"] = match.group(1)
                
                # If within date range, add to result list
                if in_range:
                    all_truth_posts.append(truth_post_data)
                    print(f"Found post within date range: {truth_post_data['date']}")
                    records_in_range += 1
            
            print(f"Page {page} processed {total_posts_page} posts, {records_in_range} within date range")
            
            # If no posts within range were found on this page and date is earlier than start date, exit the loop
            if records_in_range == 0 and items and "date" in items[-1]:
                last_date = date_parser.parse(items[-1]["date"])
                if start_date and last_date < start_date:
                    print(f"Current page's earliest date {last_date.strftime('%Y-%m-%d')} is earlier than start date {start_date.strftime('%Y-%m-%d')}, stopping retrieval")
                    break
            
            # Prevent too frequent requests
            time.sleep(1)
            
        except Exception as e:
            print(f"Error getting page {page} data: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"Retrieved a total of {len(all_truth_posts)} posts within the date range")
    return all_truth_posts

def clean_text(text):
    """Clean text content, handle special characters and formatting issues"""
    if not text:
        return ""
    
    # Replace line breaks
    text = text.replace('\n', ' ').replace('\r', ' ')
    
    # Handle URL links to ensure they are not split
    url_pattern = r'https?://\S+'
    urls = re.findall(url_pattern, text)
    for url in urls:
        # Replace URL with placeholder
        text = text.replace(url, "URL_PLACEHOLDER")
    
    # Handle other special characters
    text = text.replace('"', '""')  # Handle double quotes
    
    # Restore URLs
    for url in urls:
        text = text.replace("URL_PLACEHOLDER", url, 1)
    
    return text

def save_to_csv(posts, filename="trump_truth_social_content_raw.csv"):
    """Save Truth Social posts data to CSV file"""
    if not posts:
        print("No data to save")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(posts)
    
    # Sort by date (newest to oldest)
    if 'date' in df.columns and not df['date'].isna().all():
        df['date_obj'] = pd.to_datetime(df['date'])
        df = df.sort_values('date_obj', ascending=False)
        df = df.drop('date_obj', axis=1)
    
   
    # Only keep needed columns
    columns_to_keep = ['id', 'date', 'text', 'post_url', 'platform', 'speaker', 'deleted_flag', 'account_url']
    for col in columns_to_keep:
        if col not in df.columns:
            print(f"Warning: Column '{col}' not in data")
    
    # Only keep existing columns
    columns_to_keep = [col for col in columns_to_keep if col in df.columns]
    df = df[columns_to_keep]
    
    # Rename columns to English
    column_mapping = {
        "id": "ID",
        "date": "Date",
        "text": "Content",
        "post_url": "URL",
        "platform": "Platform",
        "speaker": "Speaker",
        "deleted_flag": "Deleted",
        "account_url": "AccountURL"
    }
    df = df.rename(columns=column_mapping)
     # Rename columns to English
    # Process text content to ensure quotes, commas and other special characters are handled correctly
    for idx, row in df.iterrows():
        if pd.notna(row['Content']):
            df.at[idx, 'Content'] = clean_text(row['Content'])
    
    # Directly use pandas to save, not using csv module
    try:
        print(f"Attempting to save {len(df)} records to {filename}...")
        df.to_csv(filename, index=False)
        print(f"Successfully saved {len(df)} records to {filename}")
        
        # Verify saved file
        try:
            saved_df = pd.read_csv(filename)
            print(f"Verification: File contains {len(saved_df)} rows of data")
        except Exception as e:
            print(f"Error verifying file: {e}")
    except Exception as e:
        print(f"Error saving CSV file: {e}")
        
        # Try using backup method to save
        try:
            print("Attempting to save using backup method...")
            # Save using simple text method
            with open(filename + ".backup", 'w', encoding='utf-8') as f:
                # Write header
                f.write(','.join(df.columns) + '\n')
                
                # Write data
                for _, row in df.iterrows():
                    row_values = []
                    for col in df.columns:
                        val = str(row[col]).replace(',', '，') if pd.notna(row[col]) else ""
                        row_values.append(val)
                    f.write(','.join(row_values) + '\n')
            
            print(f"Successfully saved using backup method to {filename}.backup")
        except Exception as e2:
            print(f"Backup method also failed: {e2}")
    
    # Print date range
    if 'Date' in df.columns and not df['Date'].isna().all():
        earliest_date = df['Date'].min()
        latest_date = df['Date'].max()
        print(f"Data date range: {earliest_date} to {latest_date}")


def main():
    """Main function"""
    # Set date range to January 20, 2025 to June 20, 2025
    start_date = datetime(2025, 1, 20)
    end_date = datetime(2025, 6, 20)
    
    print(f"Starting to fetch Trump's Truth Social posts from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}...")
    
    # Get data, set to fetch up to 100 pages to ensure finding posts within date range
    truth_posts = get_trump_truth_posts(start_date, end_date, max_pages=100)
    
    # If data found, save to CSV
    if truth_posts:
        save_to_csv(truth_posts, filename="trump_truth_social_content_raw.csv")
        
        # Output number of posts within date range
        print(f"\nFinal statistics:")
        print(f"Retrieved a total of {len(truth_posts)} posts within date range ({start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')})")
        
        # Count posts by month
        try:
            df = pd.DataFrame(truth_posts)
            df['date_obj'] = pd.to_datetime(df['date'])
            df['month'] = df['date_obj'].dt.strftime('%Y-%m')
            monthly_counts = df.groupby('month').size().reset_index(name='count')
            print("\nMonthly statistics:")
            for _, row in monthly_counts.iterrows():
                print(f"{row['month']}: {row['count']} posts")
        except Exception as e:
            print(f"Error during statistics: {e}")
    else:
        print("No posts found within date range")

if __name__ == "__main__":
    main() 