import requests
from bs4 import BeautifulSoup
import csv
import time
import os
from urllib.parse import urlparse

def read_csv_links(csv_file):
    """Reads links from a CSV file"""
    print(f"Reading links from {csv_file}...")
    links = []
    titles = []
    dates = []
    categories = []
    
    with open(csv_file, mode='r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        for row in reader:
            links.append(row['Link'])
            titles.append(row['Title'])
            dates.append(row['Date'])
            categories.append(row['Category'])
    
    print(f"Found {len(links)} links")
    return links, titles, dates, categories

def extract_content(url, original_title, original_date, category):
    """Extracts title, publication date, and content from a webpage"""
    print(f"Extracting content from: {url}")
    
    # Send the request
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=20)
        if response.status_code != 200:
            print(f"Extraction failed, status code: {response.status_code}")
            return {
                "Title": original_title,
                "Date": original_date,
                "Category": category,
                "Link": url,
                "Content": "Extraction failed",
                "Status": "Failed"
            }
        
        # Parse the HTML
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Extract content - try several possible selectors
        content_selectors = [
            "div.wp-block-post-content", 
            "article.post",
            "div.entry-content",
            "main.site-main"
        ]
        
        content_text = ""
        for selector in content_selectors:
            content = soup.select_one(selector)
            if content:
                # Remove all script and style elements
                for script in content.find_all(["script", "style"]):
                    script.decompose()
                
                # Extract paragraph text
                paragraphs = content.find_all(["p", "h1", "h2", "h3", "h4", "h5", "h6", "li"])
                if paragraphs:
                    content_text = "\n\n".join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
                    break
        
        # If no content was found, try extracting directly from the body
        if not content_text:
            body = soup.find("body")
            if body:
                # Remove navigation, menu, etc.
                for nav in body.find_all(["nav", "header", "footer", "aside"]):
                    nav.decompose()
                
                paragraphs = body.find_all(["p", "h1", "h2", "h3", "h4", "h5", "h6", "li"])
                if paragraphs:
                    content_text = "\n\n".join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
        
        # If still no content, return an error message
        if not content_text:
            content_text = "Content parsing failed, unable to find main text"
            print(f"Warning: Unable to extract content")
            status = "Failed"
        else:
            status = "Success"
        
        # Get the title and date from the page, fallback to CSV data if not found
        title = original_title
        date = original_date
        
        # Try to extract page title
        page_title = soup.find("h1")
        if page_title:
            title_text = page_title.get_text(strip=True)
            if title_text:
                title = title_text
        
        return {
            "Title": title,
            "Date": date,
            "Category": category,
            "Link": url,
            "Content": content_text,
            "Status": status
        }
        
    except requests.exceptions.RequestException as e:
        print(f"Request exception: {e}")
        return {
            "Title": original_title,
            "Date": original_date,
            "Category": category,
            "Link": url,
            "Content": f"Request exception: {e}",
            "Status": "Exception"
        }
    except Exception as e:
        print(f"Error during extraction: {e}")
        return {
            "Title": original_title,
            "Date": original_date,
            "Category": category,
            "Link": url,
            "Content": f"Processing error: {e}",
            "Status": "Exception"
        }

def save_content_to_csv(contents, output_file):
    """Saves the extracted content to a CSV file"""
    print(f"Saving content to {output_file}...")
    
    fieldnames = ["ID", "Title", "Date", "Category", "Link", "Content", "Status"]
    
    with open(output_file, 'w', encoding='utf-8-sig', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        
        for idx, content in enumerate(contents, 1):
            # Copy content and add ID
            row = content.copy()
            row["ID"] = idx
            
            # Clean content text - replace newlines with space to keep CSV format intact
            if "Content" in row and row["Content"]:
                # Replace multiple newlines with a single space
                row["Content"] = row["Content"].replace("\n", " ").replace("\r", " ")
                # Replace multiple spaces with single space
                while "  " in row["Content"]:
                    row["Content"] = row["Content"].replace("  ", " ")
            
            writer.writerow(row)
    
    print(f"Content successfully saved to {output_file}")

def main():
    csv_file = "whitehouse_link.csv"
    output_file = "whitehouse_original_text.csv"
    
    links, titles, dates, categories = read_csv_links(csv_file)
    
    contents = []
    success_count = 0
    fail_count = 0
    
    print(f"Starting extraction of content from {len(links)} links...")
    
    for i, (url, title, date, category) in enumerate(zip(links, titles, dates, categories), 1):
        print(f"Processing link {i}/{len(links)}: {title}")
        content = extract_content(url, title, date, category)
        contents.append(content)
        
        if content['Status'] == 'Success':
            success_count += 1
        else:
            fail_count += 1
        
        # Save every 10 links to prevent data loss
        if i % 10 == 0:
            save_content_to_csv(contents, output_file)
        
        # Add delay to avoid making requests too frequently
        time.sleep(1)
    
    # Final save
    save_content_to_csv(contents, output_file)
    
    print(f"Extraction complete! Success: {success_count}, Failed: {fail_count}")

if __name__ == "__main__":
    main()
