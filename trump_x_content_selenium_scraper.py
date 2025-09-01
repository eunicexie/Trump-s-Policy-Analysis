#!/usr/bin/env python3
"""
Twitter/X Tweet Content Extractor (using Selenium)
Improved version - Optimized engagement data extraction
"""

import os
import sys
import csv
import time
import random
import argparse
import logging
from datetime import datetime
from typing import Dict, List, Optional
import re

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('twitter_scraper.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TwitterSeleniumScraper:
    def __init__(self, headless=True, wait_time=10):
        """
        Initialize Twitter scraper
        
        Args:
            headless: Whether to use headless mode
            wait_time: Page loading wait time
        """
        self.wait_time = wait_time
        self.driver = None
        self.wait = None
        self._setup_driver(headless)
    
    def _setup_driver(self, headless):
        """Setup Chrome WebDriver"""
        try:
            chrome_options = Options()
            
            if headless:
                chrome_options.add_argument('--headless')
            
            # General settings
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # Disable images and CSS to improve speed
            prefs = {
                "profile.managed_default_content_settings.images": 2,
                "profile.default_content_setting_values.notifications": 2
            }
            chrome_options.add_experimental_option("prefs", prefs)
            
            # Auto-find ChromeDriver
            service = Service()
            
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.wait = WebDriverWait(self.driver, self.wait_time)
            
            logger.info("Chrome WebDriver initialized successfully")
            
        except Exception as e:
            logger.error(f"WebDriver initialization failed: {e}")
            logger.error("Please ensure Chrome browser and ChromeDriver are installed")
            sys.exit(1)
    
    def extract_tweet_data(self, url: str) -> Dict:
        """
        Extract complete data from a single tweet
        
        Args:
            url: Tweet URL
            
        Returns:
            Dictionary containing tweet data
        """
        result = {
            'author': '',
            'author_handle': '',
            'text': '',
            'date_published': '',
            'likes': 0,
            'replies': 0,
            'retweets': 0,
            'bookmarks': 0,
            'views': 0,
            'url': url,
            'extraction_status': 'failed',
            'error_message': ''
        }
        
        try:
            logger.info(f"Extracting: {url}")
            
            # Load page
            self.driver.get(url)
            
            # Wait for page to load
            time.sleep(3)
            
            # Wait for tweet content to load
            try:
                self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="tweetText"], [data-testid="tweet"]')))
            except TimeoutException:
                logger.warning(f"Tweet content loading timeout: {url}")
            
            # Extract author information
            author_info = self._extract_author_info()
            result.update(author_info)
            
            # Extract tweet text
            tweet_text = self._extract_tweet_text()
            
            # If no valid text found, mark as "no text"
            if not tweet_text or len(tweet_text.strip()) == 0:
                result['text'] = 'no text'
                logger.info(f"No text content found, possibly video/image tweet: {url}")
            else:
                result['text'] = tweet_text
            
            # Extract publication time
            result['date_published'] = self._extract_publish_date()
            
            # Extract engagement data (key improvement)
            engagement_data = self._extract_engagement_data_improved()
            result.update(engagement_data)
            
            result['extraction_status'] = 'success'
            logger.info(f"Successfully extracted: {url}")
            
        except Exception as e:
            error_msg = str(e)
            result['error_message'] = error_msg
            logger.error(f"Extraction failed {url}: {error_msg}")
        
        return result
    
    def _extract_author_info(self) -> Dict:
        """Extract author information"""
        author_info = {'author': '', 'author_handle': ''}
        
        try:
            # Method 1: Through data-testid
            try:
                author_element = self.driver.find_element(By.CSS_SELECTOR, '[data-testid="User-Name"]')
                # Usually contains display name and @username
                author_text = author_element.text.strip()
                lines = author_text.split('\n')
                if lines:
                    author_info['author'] = lines[0].strip()
                    for line in lines:
                        if line.startswith('@'):
                            author_info['author_handle'] = line.strip()
                            break
            except NoSuchElementException:
                pass
            
            # Method 2: If not found above, try other selectors
            if not author_info['author']:
                try:
                    # Find elements containing author information
                    selectors = [
                        '[data-testid="User-Names"]',
                        '.css-901oao.css-16my406.r-poiln3.r-bcqeeo.r-qvutc0',
                        'span[dir="ltr"]'
                    ]
                    
                    for selector in selectors:
                        try:
                            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                            for element in elements:
                                text = element.text.strip()
                                if text and not author_info['author']:
                                    author_info['author'] = text
                                    break
                            if author_info['author']:
                                break
                        except:
                            continue
                            
                except Exception:
                    pass
            
            # Method 3: Extract username from URL
            if not author_info['author_handle']:
                try:
                    url = self.driver.current_url
                    match = re.search(r'twitter\.com/([^/]+)', url) or re.search(r'x\.com/([^/]+)', url)
                    if match:
                        username = match.group(1)
                        if username not in ['status', 'i', 'home']:
                            author_info['author_handle'] = f'@{username}'
                except:
                    pass
                    
        except Exception as e:
            logger.debug(f"Author information extraction failed: {e}")
        
        return author_info
    
    def _extract_tweet_text(self) -> str:
        """Extract tweet text"""
        try:
            # Try multiple selectors
            selectors = [
                '[data-testid="tweetText"]',
                '.tweet-text',
                '.js-tweet-text',
                '.css-901oao.css-16my406.r-poiln3.r-bcqeeo.r-qvutc0'
            ]
            
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        text = element.text.strip()
                        if text and len(text) > 10:  # Ensure not empty content
                            # Check if it's timestamp format
                            if self._is_timestamp_format(text):
                                continue
                            return text
                except:
                    continue
            
            # If none found, try to get main page text
            try:
                article = self.driver.find_element(By.CSS_SELECTOR, 'article')
                text = article.text.strip()
                # Simple processing, take the longest paragraph
                lines = text.split('\n')
                for line in sorted(lines, key=len, reverse=True):
                    if len(line) > 20 and not self._is_timestamp_format(line):
                        return line
            except:
                pass
                
        except Exception as e:
            logger.debug(f"Tweet text extraction failed: {e}")
        
        return ''
    
    def _is_timestamp_format(self, text: str) -> bool:
        """Check if text is in timestamp format"""
        import re
        # Match timestamp formats like "3:44 pm · 16 Apr 2025"
        timestamp_patterns = [
            r'\d{1,2}:\d{2}\s*(am|pm)\s*·\s*\d{1,2}\s*\w+\s*\d{4}',  # 3:44 pm · 16 Apr 2025
            r'\d{1,2}:\d{2}\s*(AM|PM)\s*·\s*\d{1,2}\s*\w+\s*\d{4}',  # 3:44 PM · 16 Apr 2025
            r'^\d{1,2}:\d{2}\s*(am|pm|AM|PM)$',  # Time only
            r'^\w+\s*\d{1,2},?\s*\d{4}$',  # Apr 16, 2025
        ]
        
        for pattern in timestamp_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def _extract_publish_date(self) -> str:
        """Extract publication time"""
        try:
            # Find time elements
            time_selectors = [
                'time',
                '[datetime]',
                '[data-testid="Time"]'
            ]
            
            for selector in time_selectors:
                try:
                    time_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    datetime_attr = time_element.get_attribute('datetime')
                    if datetime_attr:
                        return datetime_attr
                    
                    # If no datetime attribute, try to parse text
                    time_text = time_element.text.strip()
                    if time_text:
                        # Time text parsing logic can be added here
                        return time_text
                except:
                    continue
                    
        except Exception as e:
            logger.debug(f"Publication time extraction failed: {e}")
        
        return ''
    
    def _extract_engagement_data_improved(self) -> Dict:
        """
        Improved engagement data extraction method
        Optimized for Twitter/X's new interface structure
        """
        engagement = {'likes': 0, 'replies': 0, 'retweets': 0, 'bookmarks': 0, 'views': 0}
        
        try:
            # Wait for engagement buttons to load
            time.sleep(2)
            
            # Method 1: Find engagement buttons through aria-label
            self._extract_by_aria_labels(engagement)
            
            # Method 2: Find through data-testid
            if all(v == 0 for v in engagement.values()):
                self._extract_by_test_ids(engagement)
            
            # Method 3: Match through role and text patterns
            if all(v == 0 for v in engagement.values()):
                self._extract_by_role_pattern(engagement)
            
            # Method 4: Identify through paths and SVG icons
            if all(v == 0 for v in engagement.values()):
                self._extract_by_svg_icons(engagement)
            
            # Method 5: Specifically find large numbers for views (like 76.7M)
            if engagement['views'] == 0:
                self._extract_views_by_large_numbers(engagement)
                
            logger.debug(f"Extracted engagement data: {engagement}")
            
        except Exception as e:
            logger.debug(f"Engagement data extraction failed: {e}")
        
        return engagement
    
    def _extract_by_aria_labels(self, engagement: Dict):
        """Extract engagement data through aria-label attributes"""
        try:
            # Find all elements that may contain engagement data
            clickable_elements = self.driver.find_elements(By.CSS_SELECTOR, '[role="button"], [role="link"], button, a')
            
            for element in clickable_elements:
                try:
                    aria_label = element.get_attribute('aria-label') or ''
                    aria_label_lower = aria_label.lower()
                    
                    # Check if it's complete engagement data aria-label (contains multiple stats)
                    if self._extract_from_complete_aria_label(aria_label_lower, engagement):
                        continue
                    
                    # Process each engagement button's aria-label individually
                    numbers = re.findall(r'[\d,]+', aria_label)
                    if numbers:
                        count = self._parse_number(numbers[0])
                        
                        # Determine type based on keywords
                        if any(keyword in aria_label_lower for keyword in ['reply', 'comment']):
                            engagement['replies'] = max(engagement['replies'], count)
                        elif any(keyword in aria_label_lower for keyword in ['retweet', 'repost']):
                            engagement['retweets'] = max(engagement['retweets'], count)
                        elif any(keyword in aria_label_lower for keyword in ['like', 'favorite']):
                            engagement['likes'] = max(engagement['likes'], count)
                        elif any(keyword in aria_label_lower for keyword in ['bookmark', 'save']):
                            engagement['bookmarks'] = max(engagement['bookmarks'], count)
                        elif any(keyword in aria_label_lower for keyword in ['view']):
                            engagement['views'] = max(engagement['views'], count)
                            
                except Exception:
                    continue
                    
        except Exception as e:
            logger.debug(f"aria-label extraction failed: {e}")
    
    def _extract_from_complete_aria_label(self, aria_label_lower: str, engagement: Dict) -> bool:
        """Extract all engagement data from complete aria-label
        Format like: '59334 replies, 60690 reposts, 384624 likes, 11384 bookmarks, 76743504 views'
        """
        try:
            # Check if contains complete aria-label with multiple stats
            if ('replies' in aria_label_lower and 'reposts' in aria_label_lower and 
                'likes' in aria_label_lower and 'views' in aria_label_lower):
                
                # Use regex to extract each data item
                patterns = {
                    'replies': r'(\d+(?:,\d+)*)\s+replies',
                    'retweets': r'(\d+(?:,\d+)*)\s+reposts',
                    'likes': r'(\d+(?:,\d+)*)\s+likes',
                    'bookmarks': r'(\d+(?:,\d+)*)\s+bookmarks',
                    'views': r'(\d+(?:,\d+)*)\s+views'
                }
                
                for key, pattern in patterns.items():
                    match = re.search(pattern, aria_label_lower)
                    if match:
                        count = self._parse_number(match.group(1))
                        if key == 'retweets':
                            engagement['retweets'] = max(engagement['retweets'], count)
                        else:
                            engagement[key] = max(engagement[key], count)
                
                logger.debug(f"Extracted from complete aria-label: {engagement}")
                return True
                
        except Exception as e:
            logger.debug(f"Complete aria-label parsing failed: {e}")
        
        return False
    
    def _extract_by_test_ids(self, engagement: Dict):
        """Extract engagement data through data-testid attributes"""
        try:
            test_id_mappings = {
                'reply': 'replies',
                'retweet': 'retweets', 
                'like': 'likes',
                'bookmark': 'bookmarks'
            }
            
            for test_id, key in test_id_mappings.items():
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, f'[data-testid*="{test_id}"]')
                    for element in elements:
                        text = element.text.strip()
                        if text and re.search(r'\d', text):
                            count = self._parse_number(text)
                            engagement[key] = max(engagement[key], count)
                except Exception:
                    continue
                    
        except Exception as e:
            logger.debug(f"test-id extraction failed: {e}")
    
    def _extract_by_role_pattern(self, engagement: Dict):
        """Extract engagement data through role attributes and text patterns"""
        try:
            # Find all buttons and links
            interactive_elements = self.driver.find_elements(By.CSS_SELECTOR, '[role="button"], [role="link"]')
            
            for element in interactive_elements:
                try:
                    # Get element text and all child element text
                    element_text = element.text.strip()
                    
                    # Find numbers
                    numbers = re.findall(r'[\d,]+', element_text)
                    if numbers:
                        count = self._parse_number(numbers[0])
                        
                        # Check element's HTML content to identify type
                        html_content = element.get_attribute('innerHTML') or ''
                        html_lower = html_content.lower()
                        
                        # Identify icon type through SVG paths or class names
                        if 'reply' in html_lower or 'comment' in html_lower:
                            engagement['replies'] = max(engagement['replies'], count)
                        elif 'retweet' in html_lower or 'share' in html_lower:
                            engagement['retweets'] = max(engagement['retweets'], count)
                        elif 'heart' in html_lower or 'like' in html_lower or 'favorite' in html_lower:
                            engagement['likes'] = max(engagement['likes'], count)
                        elif 'bookmark' in html_lower:
                            engagement['bookmarks'] = max(engagement['bookmarks'], count)
                            
                except Exception:
                    continue
                    
        except Exception as e:
            logger.debug(f"role pattern extraction failed: {e}")
    
    def _extract_by_svg_icons(self, engagement: Dict):
        """Extract engagement data through SVG icon features"""
        try:
            # Find buttons containing SVG
            svg_buttons = self.driver.find_elements(By.CSS_SELECTOR, 'button svg, [role="button"] svg')
            
            for svg in svg_buttons:
                try:
                    # Get parent button element
                    parent_button = svg.find_element(By.XPATH, './..')
                    while parent_button and parent_button.tag_name not in ['button', 'a'] and 'button' not in parent_button.get_attribute('role'):
                        parent_button = parent_button.find_element(By.XPATH, './..')
                    
                    if parent_button:
                        button_text = parent_button.text.strip()
                        numbers = re.findall(r'[\d,]+', button_text)
                        
                        if numbers:
                            count = self._parse_number(numbers[0])
                            
                            # Identify icon type through SVG paths or attributes
                            svg_html = svg.get_attribute('innerHTML') or ''
                            viewbox = svg.get_attribute('viewBox') or ''
                            
                            # More SVG feature recognition logic can be added here
                            # Currently using simple text matching
                            aria_label = parent_button.get_attribute('aria-label') or ''
                            
                            if 'reply' in aria_label.lower():
                                engagement['replies'] = max(engagement['replies'], count)
                            elif 'retweet' in aria_label.lower():
                                engagement['retweets'] = max(engagement['retweets'], count)
                            elif 'like' in aria_label.lower():
                                engagement['likes'] = max(engagement['likes'], count)
                            elif 'bookmark' in aria_label.lower():
                                engagement['bookmarks'] = max(engagement['bookmarks'], count)
                                
                except Exception:
                    continue
                    
        except Exception as e:
            logger.debug(f"SVG icon extraction failed: {e}")
    
    def _extract_views_by_large_numbers(self, engagement: Dict):
        """Specifically find large numbers for views (like 76.7M)"""
        try:
            # Find large numbers containing M or K, these might be views
            large_number_elements = self.driver.find_elements(By.XPATH, "//span[contains(text(), 'M') or contains(text(), 'K')]")
            
            views_candidates = []
            for element in large_number_elements:
                try:
                    text = element.text.strip()
                    # Only process pure number+unit format (like 76.7M)
                    if re.match(r'^\d+(\.\d+)?[KM]$', text):
                        number = self._parse_number(text)
                        # Views are usually the largest number
                        if number > 1000000:  # Greater than 1 million is usually views
                            views_candidates.append((number, text, element))
                except Exception:
                    continue
            
            # Choose the largest number as views
            if views_candidates:
                views_candidates.sort(key=lambda x: x[0], reverse=True)
                max_views = views_candidates[0][0]
                engagement['views'] = max(engagement['views'], max_views)
                logger.debug(f"Found views through large numbers: {max_views:,}")
                
        except Exception as e:
            logger.debug(f"Large number views extraction failed: {e}")
    
    def _parse_number(self, text: str) -> int:
        """Parse number text, support K, M units"""
        try:
            # Remove commas and spaces
            text = re.sub(r'[,\s]', '', text.strip())
            
            # Extract number part
            number_match = re.search(r'([\d.]+)([KMkm]?)', text)
            if not number_match:
                return 0
            
            number_str = number_match.group(1)
            unit = number_match.group(2).upper() if number_match.group(2) else ''
            
            number = float(number_str)
            
            # Handle units
            if unit in ['K', 'k']:
                number *= 1000
            elif unit in ['M', 'm']:
                number *= 1000000
            
            return int(number)
            
        except Exception:
            return 0
    
    def _is_valid_twitter_url(self, url: str) -> bool:
        """Validate if URL is a valid Twitter/X URL"""
        try:
            # Check if URL contains Twitter or X domain and status
            twitter_pattern = r'https?://(www\.)?(twitter\.com|x\.com)/.+/status/\d+'
            return bool(re.match(twitter_pattern, url, re.IGNORECASE))
        except Exception:
            return False
    
    def _extract_with_retry(self, url: str, max_retries: int = 2) -> Dict:
        """Extract tweet data with retry mechanism"""
        last_error = None
        
        for attempt in range(max_retries + 1):
            try:
                result = self.extract_tweet_data(url)
                
                # If successful or has some data, return immediately
                if result['extraction_status'] == 'success' or result['text']:
                    return result
                    
                # If failed and not last attempt, wait and retry
                if attempt < max_retries:
                    logger.info(f"Attempt {attempt + 1} failed for {url}, retrying...")
                    time.sleep(5)
                    continue
                    
                return result
                
            except Exception as e:
                last_error = str(e)
                logger.warning(f"Attempt {attempt + 1} error for {url}: {e}")
                
                if attempt < max_retries:
                    time.sleep(5)
                    continue
        
        # All attempts failed
        return {
            'author': '',
            'author_handle': '',
            'text': '',
            'date_published': '',
            'likes': 0,
            'replies': 0,
            'retweets': 0,
            'bookmarks': 0,
            'views': 0,
            'url': url,
            'extraction_status': 'failed',
            'error_message': f'All {max_retries + 1} attempts failed. Last error: {last_error}'
        }
    
    def process_csv_file(self, input_file: str, output_file: str, start_index: int = 0, batch_size: Optional[int] = None):
        """
        Batch process tweet URLs in CSV file
        
        Args:
            input_file: Input CSV file path
            output_file: Output CSV file path
            start_index: Starting row index
            batch_size: Batch size
        """
        try:
            # Read input file
            with open(input_file, 'r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                rows = []
                for row in reader:
                    # Clean empty field names
                    cleaned_row = {k: v for k, v in row.items() if k and k.strip()}
                    rows.append(cleaned_row)
            
            logger.info(f"Read {len(rows)} records")
            
            # Check available column names for URL
            if rows:
                available_columns = list(rows[0].keys())
                logger.info(f"Available columns: {available_columns}")
                
                # Try different possible URL column names
                url_column = None
                for col in ['URL', 'url', 'link', 'Link', 'tweet_url', 'post_url']:
                    if col in available_columns:
                        url_column = col
                        logger.info(f"Using '{col}' column for URLs")
                        break
                
                if not url_column:
                    logger.error(f"No URL column found. Available columns: {available_columns}")
                    return
            else:
                logger.error("No data rows found in input file")
                return
            
            # Determine processing range
            end_index = len(rows)
            if batch_size:
                end_index = min(start_index + batch_size, len(rows))
            
            process_rows = rows[start_index:end_index]
            logger.info(f"Processing range: {start_index} - {end_index-1} (total {len(process_rows)} items)")
            
            results = []
            processed_count = 0
            error_count = 0
            
            for i, row in enumerate(process_rows):
                try:
                    # Get URL using detected column name
                    url = row.get(url_column, '').strip()
                    if not url:
                        logger.warning(f"Row {start_index + i + 1} missing URL in column '{url_column}'")
                        continue
                    
                    # Validate URL format
                    if not self._is_valid_twitter_url(url):
                        logger.warning(f"Row {start_index + i + 1} invalid Twitter/X URL: {url}")
                        continue
                    
                    # Extract tweet data with retry mechanism
                    tweet_data = self._extract_with_retry(url, max_retries=2)
                    
                    # Only use extracted Twitter API data, don't merge input old fields
                    result = tweet_data
                    results.append(result)
                    processed_count += 1
                    
                    if tweet_data['extraction_status'] == 'failed':
                        error_count += 1
                        logger.warning(f"Failed to extract data from: {url} - {tweet_data.get('error_message', 'Unknown error')}")
                    
                    # Add random delay to prevent blocking
                    time.sleep(random.uniform(8, 15))
                    
                    # Save every 5 records
                    if processed_count % 5 == 0:
                        self._save_results(results, output_file)
                        logger.info(f"Processed {processed_count}/{len(process_rows)} records")
                
                except Exception as e:
                    logger.error(f"Error processing row {start_index + i + 1}: {e}")
                    error_count += 1
                    continue
            
            # Final save
            self._save_results(results, output_file)
            logger.info(f"Processing complete! Total: {processed_count}, Success: {processed_count - error_count}, Failed: {error_count}")
            
        except Exception as e:
            logger.error(f"Error processing file: {e}")
            if 'results' in locals() and results:
                self._save_results(results, output_file)
                logger.info(f"Saved partial results to {output_file}")
    
    def _save_results(self, results: List[Dict], output_file: str):
        """Save results to CSV file"""
        if not results:
            return
        
        # Define standardized field order (Twitter API fields only)
        standard_fieldnames = [
            'author', 'author_handle', 'text', 'date_published', 
            'likes', 'replies', 'retweets', 'bookmarks', 'views', 'url',
            'extraction_status', 'error_message'
        ]
        
        # Determine actual field names (including empty fields)
        actual_fieldnames = []
        sample_keys = set(results[0].keys())
        
        for field in standard_fieldnames:
            if field in sample_keys:
                actual_fieldnames.append(field)
        
        # Add any extra fields (if any)
        for key in sample_keys:
            if key not in actual_fieldnames:
                actual_fieldnames.append(key)
        
        with open(output_file, 'w', newline='', encoding='utf-8-sig') as file:
            writer = csv.DictWriter(file, fieldnames=actual_fieldnames)
            writer.writeheader()
            writer.writerows(results)
    
    def close(self):
        """Close browser"""
        if self.driver:
            self.driver.quit()
            logger.info("Browser closed")

def find_input_file(specified_file=None):
    """
    Find input file, support multiple path formats
    
    Args:
        specified_file: User specified file path
        
    Returns:
        Found file path
    """
    # Default file list to search (by priority)
    default_files = [
        'Cleaned Data/trump_x_content_cleaned.csv',
        'trump_x_content_cleaned.csv',
        'Cleaned Data/trump_x_content.csv',
        'trump_x_content.csv'
    ]
    
    # If user specified a file
    if specified_file:
        # Direct path check
        if os.path.exists(specified_file):
            return specified_file
        
        # Search in current directory
        if os.path.exists(os.path.join('.', specified_file)):
            return os.path.join('.', specified_file)
        
        # Search in Cleaned Data directory
        cleaned_data_path = os.path.join('Cleaned Data', specified_file)
        if os.path.exists(cleaned_data_path):
            return cleaned_data_path
        
        # If not found anywhere, return original path (let subsequent error handling deal with it)
        return specified_file
    
    # If user didn't specify, search by default list
    for file_path in default_files:
        if os.path.exists(file_path):
            logger.info(f"Auto-found input file: {file_path}")
            return file_path
    
    # If none found, return first default file (let subsequent error handling deal with it)
    return default_files[0]

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Twitter Tweet Data Extractor (Improved Version)')
    parser.add_argument('input_file', nargs='?', help='Input CSV file path (optional, auto-detects by default)')
    parser.add_argument('-o', '--output', help='Output file path', default='trump_x_content_fixed_engagenment.csv')
    parser.add_argument('--start-index', type=int, default=0, help='Starting row index')
    parser.add_argument('--batch-size', type=int, help='Batch size')
    parser.add_argument('--wait-time', type=int, default=10, help='Page loading wait time')
    parser.add_argument('--headless', action='store_true', help='Use headless mode')
    
    args = parser.parse_args()
    
    # Find input file
    input_file = find_input_file(args.input_file)
    
    # Check input file
    if not os.path.exists(input_file):
        logger.error(f"Input file does not exist: {input_file}")
        logger.error("Please ensure one of the following files exists:")
        logger.error("  - Cleaned Data/trump_x_content_cleaned.csv")
        logger.error("  - trump_x_content_cleaned.csv")
        logger.error("  - Or manually specify file path")
        sys.exit(1)
    
    logger.info(f"Using input file: {input_file}")
    
    scraper = None
    try:
        # Create scraper instance
        scraper = TwitterSeleniumScraper(
            headless=args.headless,
            wait_time=args.wait_time
        )
        
        # Process file
        scraper.process_csv_file(
            input_file=input_file,
            output_file=args.output,
            start_index=args.start_index,
            batch_size=args.batch_size
        )
        
    except KeyboardInterrupt:
        logger.info("User interrupted program")
    except Exception as e:
        logger.error(f"Program execution error: {e}")
    finally:
        if scraper:
            scraper.close()

if __name__ == "__main__":
    main()
