#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import pandas as pd
from datetime import datetime
import time
import os
import re
from dateutil import parser as date_parser
import pytz
import csv

def get_trump_tweets(start_date=None, end_date=None, max_pages=2):
    """
    Directly fetch Trump's Twitter posts from Roll Call API
    
    Parameters:
    - start_date: Start date (datetime object), if None, no start date restriction
    - end_date: End date (datetime object), if None, no end date restriction
    - max_pages: Maximum number of pages, default is 2 pages
    
    Returns:
    - List of tweets that match the date range
    """
    all_tweets = []
    processed_ids = set()
    
    # Ensure start and end dates are datetime objects with timezone
    if start_date and start_date.tzinfo is None:
        start_date = pytz.UTC.localize(start_date)
    if end_date and end_date.tzinfo is None:
        end_date = pytz.UTC.localize(end_date)
    
    # API URL - Using known available API endpoint
    api_url = "https://rollcall.com/wp-json/factbase/v1/twitter"
    
    # Request headers
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Content-Type": "application/json",
        "Referer": "https://rollcall.com/factbase-twitter/?platform=twitter&sort=date&sort_order=desc&page=1",
        "X-Requested-With": "XMLHttpRequest"
    }
    
    # Force fetching multiple pages of data
    for page in range(1, max_pages + 1):
        print(f"Fetching page {page} data...")
        
        # Request parameters
        params = {
            "platform": "twitter",
            "sort": "date",
            "sort_order": "desc",
            "page": page,
            "per_page": 100  # 100 records per page
        }
        
        try:
            # Send request
            response = requests.get(api_url, headers=headers, params=params)
            
            # Check response status
            if response.status_code != 200:
                print(f"Request failed, status code: {response.status_code}")
                print(f"Response content: {response.text[:500]}...")
                break
            
            # Parse JSON response
            data = response.json()
            
            if page == 1:  # Only print data structure for the first page
                print("API response data structure:")
                print(f"Data type: {type(data)}")
                if isinstance(data, dict):
                    print(f"Top level keys: {list(data.keys())}")
                    if "data" in data and len(data["data"]) > 0:
                        first_item = data["data"][0]
                        print(f"First data item keys: {list(first_item.keys())}")
                        print(f"First data item content: {json.dumps(first_item, indent=2)[:500]}...")
                    
                        # Specifically check date field
                        if "date" in first_item:
                            print(f"Date field type: {type(first_item['date'])}")
                            print(f"Date field value: {first_item['date']}")
                            
                            # Try to parse the date
                            try:
                                date_obj = date_parser.parse(first_item['date'])
                                print(f"Parsed date: {date_obj.strftime('%Y-%m-%d %H:%M:%S %Z%z')}")
                                print(f"Has timezone info: {date_obj.tzinfo is not None}")
                            except Exception as e:
                                print(f"Error parsing date: {e}")
                    
                    # Check pagination info
                    if "meta" in data:
                        print(f"Metadata: {json.dumps(data['meta'], indent=2)}")
                        if "pagination" in data["meta"]:
                            print(f"Pagination info: {json.dumps(data['meta']['pagination'], indent=2)}")
            
            if not data or "data" not in data or not data["data"]:
                print(f"Page {page} has no data, ending retrieval")
                continue  # Try next page
            
            items = data["data"]
            print(f"Found {len(items)} records")
            total_tweets_page = 0
            
            # Process each tweet
            for tweet in items:
                # Check if already processed
                tweet_id = tweet.get("id")
                
                if tweet_id and tweet_id in processed_ids:
                    continue
                
                if tweet_id:
                    processed_ids.add(tweet_id)
                    total_tweets_page += 1
                
                # Get date
                tweet_date = None
                if "date" in tweet:
                    try:
                        # Use dateutil to parse ISO format date (with timezone)
                        tweet_date = date_parser.parse(tweet["date"])
                    except Exception as e:
                        print(f"Error parsing date {tweet_id}: {e}")
                
                # Check date range
                in_range = True
                if tweet_date:
                    if start_date and tweet_date < start_date:
                        in_range = False
                        print(f"Tweet {tweet_id} date {tweet_date.strftime('%Y-%m-%d')} is earlier than start date {start_date.strftime('%Y-%m-%d')}")
                    if end_date and tweet_date > end_date:
                        in_range = False
                        print(f"Tweet {tweet_id} date {tweet_date.strftime('%Y-%m-%d')} is later than end date {end_date.strftime('%Y-%m-%d')}")
                else:
                    # If no date, consider not in range by default
                    in_range = False
                    print(f"Tweet {tweet_id} has no valid date, not included in results")
                
                # Extract required fields
                tweet_data = {
                    "id": tweet_id,
                    "date": tweet_date.strftime("%Y-%m-%d %H:%M:%S") if tweet_date else None,
                    "text": tweet.get("text", ""),
                    "post_url": tweet.get("post_url", ""),
                    "image_url": tweet.get("image_url", ""),
                    "platform": tweet.get("platform", "Twitter"),
                    "handle": tweet.get("handle", "realDonaldTrump"),
                    "speaker": tweet.get("speaker", "Donald Trump"),
                    "deleted_flag": tweet.get("deleted_flag", False)
                }
                
                # Extract tweet ID from URL
                if tweet_data["post_url"] and not tweet_data.get("tweet_id"):
                    match = re.search(r'status/(\d+)', tweet_data["post_url"])
                    if match:
                        tweet_data["tweet_id"] = match.group(1)
                
                # If within date range, add to result list
                if in_range:
                    all_tweets.append(tweet_data)
                    print(f"Found tweet within date range: {tweet_data['date']}")
            
            print(f"Page {page} processed {total_tweets_page} tweets")
            
            # Prevent too frequent requests
            time.sleep(1)
            
        except Exception as e:
            print(f"Error getting page {page} data: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"Retrieved a total of {len(all_tweets)} tweets within the date range")
    return all_tweets

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

def save_to_csv(tweets, filename="trump_x_content_raw.csv"):
    """Save tweet data to CSV file"""
    if not tweets:
        print("No data to save")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(tweets)
    
    # Sort by date (newest to oldest)
    if 'date' in df.columns and not df['date'].isna().all():
        df['date_obj'] = pd.to_datetime(df['date'])
        df = df.sort_values('date_obj', ascending=False)
        df = df.drop('date_obj', axis=1)
    
   
    # Only keep needed columns
    columns_to_keep = ['id', 'date', 'text', 'post_url', 'platform', 'speaker', 'deleted_flag']
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
        "deleted_flag": "Deleted"
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
    # Set date range: January 20, 2025 to April 20, 2025 (expand start date)
    start_date = datetime(2025, 1, 20)
    end_date = datetime(2025, 6, 20)
    
    print(f"Starting to fetch Trump's Twitter posts from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}...")
    
    # Get tweet data, set to fetch first 3 pages
    tweets = get_trump_tweets(start_date, end_date, max_pages=3)
    
    # If data found, save to CSV
    if tweets:
        save_to_csv(tweets, filename="trump_x_content_raw.csv")
        
        # Output number of tweets within date range
        print(f"\nFinal statistics:")
        print(f"Retrieved a total of {len(tweets)} tweets within date range (Jan 20, 2025 to June 20, 2025)")
        
        # Count tweets by month
        try:
            df = pd.DataFrame(tweets)
            df['date_obj'] = pd.to_datetime(df['date'])
            df['month'] = df['date_obj'].dt.strftime('%Y-%m')
            monthly_counts = df.groupby('month').size().reset_index(name='count')
            print("\nMonthly statistics:")
            for _, row in monthly_counts.iterrows():
                print(f"{row['month']}: {row['count']} tweets")
        except Exception as e:
            print(f"Error during statistics: {e}")
    else:
        print("No tweets found within date range")

if __name__ == "__main__":
    main() 