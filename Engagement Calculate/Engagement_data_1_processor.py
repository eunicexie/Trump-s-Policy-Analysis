#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data Processing Script - Process engagement data for Trump policy analysis
Create proper headers based on definitions in Header_explaination.csv and calculate corresponding metrics
"""

import pandas as pd
import numpy as np
from collections import defaultdict
import os

def load_and_process_data():
    """
    Load raw data and process it according to header explanation file
    """
    # File paths - using relative paths from project root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    raw_data_path = os.path.join(script_dir, "Engagement_data_raw.csv")
    header_explanation_path = os.path.join(script_dir, "Header_explaination.csv")
    output_path = os.path.join(script_dir, "Engagement_data_processed.csv")
    
    print("Loading raw data...")
    # Load raw data
    df_raw = pd.read_csv(raw_data_path)
    
    print(f"Raw data contains {len(df_raw)} records")
    print(f"Platforms covered: {df_raw['Platform'].unique()}")
    print(f"Categories covered: {df_raw['Category_id'].unique()}")
    
    # Group by Tag_id and calculate various metrics
    print("\nCalculating various metrics...")
    
    # Create results dictionary
    results = []
    
    # Define all expected tags (based on source file structure)
    all_expected_tags = [
        'A1', 'A2', 'A3', 'A4', 'A5', 'A6',
        'B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 
        'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8'
    ]
    
    # Get actually existing tags in raw data
    actual_tags_in_data = df_raw['Tag_id'].unique()
    total_records = len(df_raw)  # Total records for calculating frequency percentage
    
    print(f"Total expected tags: {len(all_expected_tags)}")
    print(f"Tags in actual data: {len(actual_tags_in_data)}")
    
    # Iterate through all expected tags to ensure each tag has a record
    for tag_id in all_expected_tags:
        # Determine category ID
        category_id = tag_id[0]  # A1 -> A, B2 -> B, C3 -> C
        
        # Check if this tag exists in raw data
        tag_data = df_raw[df_raw['Tag_id'].str.contains(tag_id, na=False)]
        
        if len(tag_data) > 0:
            # Tags with data - calculate actual values
            # 1. Frequency (Count) - mention count (raw count)
            frequency_count = len(tag_data)
            
            # 2. Frequency (%) - frequency percentage
            frequency_percent = (frequency_count / total_records) * 100
            
            # 3. Total_Likes - total likes count
            total_likes = tag_data['Likes'].sum()
            
            # 4. Total_Reposts - total reposts count
            total_reposts = tag_data['Repost'].sum()
            
            # 5. Total_Comments - total comments count (using Replies column here)
            total_comments = tag_data['Replies'].sum()
            
            # 6. Total_Engagement - total engagement
            total_engagement = total_likes + total_reposts + total_comments
            
            # 7. X_Total_Engagement - total engagement on X platform
            x_data = tag_data[tag_data['Platform'] == 'X']
            x_total_engagement = (x_data['Likes'].sum() + 
                                 x_data['Repost'].sum() + 
                                 x_data['Replies'].sum()) if len(x_data) > 0 else 0
            
            # 8. Truth_Total_Engagement - total engagement on Truth Social platform
            truth_data = tag_data[tag_data['Platform'] == 'Truth Social']
            truth_total_engagement = (truth_data['Likes'].sum() + 
                                     truth_data['Repost'].sum() + 
                                     truth_data['Replies'].sum()) if len(truth_data) > 0 else 0
            
            # 9. Average_Engagement - average engagement
            average_engagement = total_engagement / frequency_count if frequency_count > 0 else 0
            
            # 10. X_Average_Engagement - average engagement on X platform
            x_frequency_count = len(x_data) if len(x_data) > 0 else 0
            x_average_engagement = x_total_engagement / x_frequency_count if x_frequency_count > 0 else 0
            
            # 11. Truth_Average_Engagement - average engagement on Truth Social platform
            truth_frequency_count = len(truth_data) if len(truth_data) > 0 else 0
            truth_average_engagement = truth_total_engagement / truth_frequency_count if truth_frequency_count > 0 else 0
            
        else:
            # Tags with no data - set all to 0
            frequency_count = 0
            frequency_percent = 0.0
            total_likes = 0
            total_reposts = 0
            total_comments = 0
            total_engagement = 0
            x_total_engagement = 0
            truth_total_engagement = 0
            average_engagement = 0.0
            x_average_engagement = 0.0
            truth_average_engagement = 0.0
        
        # Add to results list
        results.append({
            'Tag_id': tag_id,
            'Category_id': category_id,
            'Frequency (Count)': frequency_count,
            'Frequency (%)': round(frequency_percent, 2),
            'Total_Likes': total_likes,
            'Total_Reposts': total_reposts,
            'Total_Comments': total_comments,
            'Total_Engagement': total_engagement,
            'X_Total_Engagement': x_total_engagement,
            'Truth_Total_Engagement': truth_total_engagement,
            'Average_Engagement': round(average_engagement, 2),
            'X_Average_Engagement': round(x_average_engagement, 2),
            'Truth_Average_Engagement': round(truth_average_engagement, 2)
        })
    
    # Create DataFrame
    df_processed = pd.DataFrame(results)
    
    # Sort by Category_id and Tag_id
    df_processed = df_processed.sort_values(['Category_id', 'Tag_id'])
    
    # Save processed data
    df_processed.to_csv(output_path, index=False, encoding='utf-8')
    
    print(f"\nData processing completed!")
    print(f"Processed data saved to: {output_path}")
    print(f"Processed {len(df_processed)} different policy tags")
    
    # Display statistics
    print(f"\nData statistics:")
    print(f"- Total mentions: {df_processed['Frequency (Count)'].sum()}")
    print(f"- Total engagement: {df_processed['Total_Engagement'].sum():,}")
    print(f"- Average engagement per tag: {df_processed['Average_Engagement'].mean():.2f}")
    
    # Display preview of first few rows
    print(f"\nProcessed data preview:")
    print(df_processed.head())
    
    return df_processed

def display_header_explanations():
    """
    Display header explanation information
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    header_explanation_path = os.path.join(script_dir, "Header_explaination.csv")
    
    if os.path.exists(header_explanation_path):
        print("=" * 80)
        print("Header Explanations (based on Header_explaination.csv):")
        print("=" * 80)
        
        df_headers = pd.read_csv(header_explanation_path)
        for _, row in df_headers.iterrows():
            if pd.notna(row['Header']) and row['Header'] != '':
                print(f"\n【{row['Header']}】")
                print(f"Chinese Name: {row['中文解释']}")
                print(f"Description: {row['在研究中的作用和意义']}")
        print("=" * 80)

if __name__ == "__main__":
    print("Trump Policy Analysis - Engagement Data Processing Script")
    print("=" * 50)
    
    # Display header explanations
    display_header_explanations()
    
    # Process data
    try:
        processed_data = load_and_process_data()
        print("\nData processing completed successfully.")
        
        # Provide some additional analysis information
        print(f"\nQuick analysis:")
        top_engagement = processed_data.nlargest(5, 'Average_Engagement')[['Tag_id', 'Average_Engagement']]
        print(f"\nTop 5 policy tags with highest average engagement:")
        for _, row in top_engagement.iterrows():
            print(f"  {row['Tag_id']}: {row['Average_Engagement']:.2f}")
            
        most_frequent = processed_data.nlargest(5, 'Frequency (Count)')[['Tag_id', 'Frequency (Count)']]
        print(f"\nTop 5 most frequently mentioned policy tags:")
        for _, row in most_frequent.iterrows():
            print(f"  {row['Tag_id']}: {row['Frequency (Count)']} times")
            
    except Exception as e:
        print(f"Error occurred during processing: {e}")
        print("Please check if file paths and data formats are correct.")
