import requests
from bs4 import BeautifulSoup
import csv
import time
import re
from datetime import datetime

def scrape_presidential_actions():
    base_url = "https://www.whitehouse.gov/presidential-actions/"
    all_actions = []
    page = 1
    
    while True:
        print(f"Scraping page {page}...")
        
        # Build URL (first page has no page parameter, subsequent pages do)
        if page == 1:
            url = base_url
        else:
            url = f"{base_url}page/{page}/"
        
        # Send request
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        
        # Check if request was successful
        if response.status_code != 200:
            print(f"Failed to scrape page {page}, status code: {response.status_code}")
            break
            
        # Parse page content
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Find all article items - use correct selector
        action_items = soup.select("ul.wp-block-post-template li.wp-block-post")
        
        # If no items found, may have reached the last page
        if not action_items:
            print(f"No article items found on page {page}, may have reached the last page")
            break
        
        print(f"Found {len(action_items)} article items")
        
        # Extract title, link and date for each article
        for item in action_items:
            try:
                # Find title and link - update selector
                title_element = item.select_one("h2.wp-block-post-title a")
                if title_element:
                    title = title_element.get_text(strip=True)
                    link = title_element.get("href")
                else:
                    continue
                
                # Find date - update selector
                date_element = item.select_one("div.wp-block-post-date time")
                date_text = date_element.get_text(strip=True) if date_element else "Date not found"
                
                # Find categories
                category_elements = item.select("div.taxonomy-category a")
                categories = [cat.get_text(strip=True) for cat in category_elements] if category_elements else []
                category_text = ", ".join(categories)
                
                # Ensure link is absolute URL
                if link and not link.startswith(('http://', 'https://')):
                    link = f"https://www.whitehouse.gov{link}" if not link.startswith('/') else f"https://www.whitehouse.gov{link}"
                
                # Add to result list
                all_actions.append({
                    "Title": title,
                    "Link": link,
                    "Date": date_text,
                    "Category": category_text
                })
                
                print(f"Successfully extracted: {title}")
                
            except Exception as e:
                print(f"Error processing item: {e}")
        
        print(f"Successfully scraped {len(action_items)} items from page {page}")
        
        # Check if there's a next page
        next_link = soup.select_one("a.wp-block-query-pagination-next")
        if not next_link:
            print("No next page link found, scraping completed")
            break
        
        # Increment page number and add delay to avoid too frequent requests
        page += 1
        time.sleep(1)  # 1 second delay
    
    print(f"Total scraped {len(all_actions)} presidential action items")
    return all_actions

def save_to_csv(actions, filename="whitehouse_link.csv"):
    """Save scraped data to CSV file"""
    with open(filename, mode='w', newline='', encoding='utf-8-sig') as file:
        writer = csv.DictWriter(file, fieldnames=["Title", "Link", "Date", "Category"])
        writer.writeheader()
        writer.writerows(actions)
    print(f"Data successfully saved to {filename}")

if __name__ == "__main__":
    actions = scrape_presidential_actions()
    save_to_csv(actions)
    print("Scraper execution completed!")
