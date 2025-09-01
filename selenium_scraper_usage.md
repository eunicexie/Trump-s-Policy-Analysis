# Twitter/X Selenium Scraper Usage Guide

## Overview

This script uses Selenium and ChromeDriver to automatically open tweet pages and extract complete tweet content and engagement data from Twitter/X.

## Extracted Data Fields

- **text**: Complete tweet text content
- **author**: Author display name
- **author_handle**: Author username (@username)
- **date_published**: Publication timestamp
- **likes**: Number of likes
- **replies**: Number of replies
- **retweets**: Number of retweets/reposts
- **bookmarks**: Number of bookmarks
- **views**: Number of views
- **url**: Tweet URL
- **extraction_status**: Extraction status (success/failed)
- **error_message**: Error message (if any)

## Usage

### 1. Basic CSV Processing

```bash
# Basic batch processing with auto file detection
python trump_x_content_selenium_scraper.py

# Specify input file
python trump_x_content_selenium_scraper.py trump_x_content_raw.csv

# Custom output file
python trump_x_content_selenium_scraper.py trump_x_content_raw.csv -o twitter_complete_data.csv
```

### 2. Batch Processing with Range Control

```bash
# Process specific range (start from index 0, process 10 items)
python trump_x_content_selenium_scraper.py trump_x_content_raw.csv -o output.csv --start-index 0 --batch-size 10

# Headless mode batch processing
python trump_x_content_selenium_scraper.py trump_x_content_raw.csv -o output.csv --headless --batch-size 20
```

### 3. Processing Large Files in Batches

For large datasets, it's recommended to process in batches:

```bash
# Process first 10 items
python trump_x_content_selenium_scraper.py trump_x_content_raw.csv -o batch_1.csv --start-index 0 --batch-size 10

# Process items 11-20
python trump_x_content_selenium_scraper.py trump_x_content_raw.csv -o batch_2.csv --start-index 10 --batch-size 10

# Process items 21-30
python trump_x_content_selenium_scraper.py trump_x_content_raw.csv -o batch_3.csv --start-index 20 --batch-size 10
```

## Command Line Arguments

- `input_file`: Input CSV file path (optional - auto-detects if not specified)
- `--output` / `-o`: Output file path (default: `trump_x_content_fixed_engagenment.csv`)
- `--start-index`: Starting row index (default: 0)
- `--batch-size`: Number of items to process per batch (optional - processes all if not specified)
- `--headless`: Use headless mode (no browser window)
- `--wait-time`: Page loading wait time in seconds (default: 10)

## File Auto-Detection

The script automatically looks for input files in the following order:

1. `Cleaned Data/trump_x_content_cleaned.csv`
2. `trump_x_content_cleaned.csv`
3. `Cleaned Data/trump_x_content.csv`
4. `trump_x_content.csv`

## Recommended Usage Strategies

### 1. First-Time Usage
1. Start with a small batch to ensure the script works properly
2. Test with 5-10 items first
3. Gradually increase batch size

### 2. Large-Scale Processing
1. Use headless mode for better efficiency
2. Process in batches of 20-50 items
3. Automatic rest intervals between items
4. Save multiple small files, then merge if needed

### 3. Error Handling
- Script automatically retries failed requests
- 3-second rest every 5 tweets
- Error messages are recorded in results
- Partial results are saved every 5 processed items

## Example Commands

### Quick Start (Recommended)
```bash
# Test with first 5 tweets
python trump_x_content_selenium_scraper.py -o test_output.csv --batch-size 5 --wait-time 15

# If test successful, process more data
python trump_x_content_selenium_scraper.py -o complete_data.csv --batch-size 20 --headless
```

### Processing with Custom Input
```bash
# Process specific file with custom settings
python trump_x_content_selenium_scraper.py my_tweets.csv -o results.csv --headless --batch-size 25

# Debug mode (visible browser)
python trump_x_content_selenium_scraper.py my_tweets.csv -o results.csv --wait-time 15
```

## Important Notes

1. **Speed**: Each tweet takes approximately 15-30 seconds to process
2. **Stability**: Using smaller batches helps avoid long-running session issues
3. **Anti-Detection**: Script includes anti-detection measures, but use responsibly
4. **Resource Usage**: Visible browser mode uses more resources; headless mode is more efficient
5. **Auto-Save**: Results are automatically saved every 5 processed items to prevent data loss

## Troubleshooting

### Common Issues
1. **ChromeDriver Version**: Script automatically downloads matching ChromeDriver
2. **Network Timeout**: Increase `--wait-time` parameter
3. **Tweet Loading Failed**: Some tweets may require login or have been deleted
4. **File Not Found**: Script auto-detects common file locations

### Debugging Tips
1. Don't use `--headless` to see browser operations during debugging
2. Check log output for processing progress and error information
3. Use smaller batch sizes for testing
4. Verify input CSV file has 'URL' column with valid Twitter/X URLs

## Advanced Features

### Multiple Extraction Methods
The script uses 5 different methods to extract engagement data:
1. **aria-label** attributes parsing
2. **data-testid** attributes
3. **role** patterns with text matching
4. **SVG icon** recognition
5. **Large number** detection for views (e.g., "76.7M")

### Robust Text Extraction
- Handles various tweet formats (text, media-only, etc.)
- Filters out timestamp text automatically
- Marks media-only tweets as "no text"
- Supports multiple CSS selector strategies

### Error Recovery
- Automatic retry mechanisms
- Graceful degradation when elements aren't found
- Comprehensive logging for debugging
- Partial result preservation
