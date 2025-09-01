#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Trump Policy Analysis - Macro Engagement Data Processing Script
================================================================

This script aggregates micro-level tag data into macro-level category data
Outputs results according to the format of Engagement_overall_format.csv

Input file: Engagement_data_processed.csv (micro data)
Output file: Engagement_overall_result.csv (macro data)

"""

import pandas as pd
import numpy as np
import os
from pathlib import Path

def load_processed_data():
    """Load processed micro-level data"""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, 'Engagement_data_processed.csv')
        df = pd.read_csv(file_path)
        print(f"Loaded {len(df)} tags from processed data")
        return df
    except FileNotFoundError:
        print("Error: Engagement_data_processed.csv file not found")
        return None
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

def load_raw_data():
    """Load raw data to get platform distribution information"""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, 'Engagement_data_raw.csv')
        df_raw = pd.read_csv(file_path)
        # Calculate number of posts per category on each platform
        platform_stats = df_raw.groupby(['Category_id', 'Platform']).size().unstack(fill_value=0)
        return platform_stats
    except FileNotFoundError:
        print("Warning: Raw data file not found, will use estimated values")
        return None

def calculate_category_stats(df):
    """Calculate statistics for each category"""
    
    # Category name mapping
    category_names = {
        'A': 'Subjugating the Bureaucracy',
        'B': 'Waging Culture Wars', 
        'C': 'Remaking Power Structures'
    }
    
    # Load raw data to get platform distribution
    platform_stats = load_raw_data()
    
    results = []
    total_posts = df['Frequency (Count)'].sum()
    
    print(f"Total posts: {total_posts}")
    if platform_stats is not None:
        print("\nDistribution of categories across platforms:")
        print(platform_stats)
    print("\nStarting category data calculation...")
    
    for category in ['A', 'B', 'C']:
        category_data = df[df['Category_id'] == category]
        print(f"\nProcessing category {category} ({category_names[category]}):")
        print(f"  Number of tags: {len(category_data)}")
        
        # Combined (total) data
        combined_frequency = category_data['Frequency (Count)'].sum()
        combined_total_engagement = category_data['Total_Engagement'].sum()
        combined_avg_engagement = combined_total_engagement / combined_frequency if combined_frequency > 0 else 0
        combined_frequency_pct = (combined_frequency / total_posts) * 100 if total_posts > 0 else 0
        
        print(f"  Combined - Frequency: {combined_frequency}, Total engagement: {combined_total_engagement:,}")
        
        # X platform data - using actual post count from raw data
        if platform_stats is not None and 'X' in platform_stats.columns:
            x_frequency = platform_stats.loc[category, 'X'] if category in platform_stats.index else 0
        else:
            x_frequency = len(category_data[category_data['X_Total_Engagement'] > 0])
            
        x_total_engagement = category_data['X_Total_Engagement'].sum()
        x_avg_engagement = x_total_engagement / x_frequency if x_frequency > 0 else 0
        x_frequency_pct = (x_frequency / total_posts) * 100 if total_posts > 0 else 0
        
        print(f"  X platform - Frequency: {x_frequency}, Total engagement: {x_total_engagement:,}")
        
        # Truth Social platform data - using actual post count from raw data
        if platform_stats is not None and 'Truth Social' in platform_stats.columns:
            truth_frequency = platform_stats.loc[category, 'Truth Social'] if category in platform_stats.index else 0
        else:
            truth_frequency = len(category_data[category_data['Truth_Total_Engagement'] > 0])
            
        truth_total_engagement = category_data['Truth_Total_Engagement'].sum()
        truth_avg_engagement = truth_total_engagement / truth_frequency if truth_frequency > 0 else 0
        truth_frequency_pct = (truth_frequency / total_posts) * 100 if total_posts > 0 else 0
        
        print(f"  Truth Social - Frequency: {truth_frequency}, Total engagement: {truth_total_engagement:,}")
        
        # Add results
        # Combined row
        results.append({
            'Category ID': category,
            'Category Name': category_names[category],
            'Platform': 'Combined',
            'Frequency (Count)': combined_frequency,
            'Frequency (%)': f"{combined_frequency_pct:.2f}%",
            'Total Engagement': f"{combined_total_engagement:,}",
            'Average Engagement': f"{combined_avg_engagement:,.0f}"
        })
        
        # X platform row
        results.append({
            'Category ID': category,
            'Category Name': category_names[category],
            'Platform': 'X',
            'Frequency (Count)': x_frequency if x_frequency > 0 else '',
            'Frequency (%)': f"{x_frequency_pct:.2f}%" if x_frequency > 0 else "",
            'Total Engagement': f"{x_total_engagement:,}" if x_total_engagement > 0 else "",
            'Average Engagement': f"{x_avg_engagement:,.0f}" if x_avg_engagement > 0 else ""
        })
        
        # Truth Social row
        results.append({
            'Category ID': category,
            'Category Name': category_names[category],
            'Platform': 'Truth Social',
            'Frequency (Count)': truth_frequency if truth_frequency > 0 else '',
            'Frequency (%)': f"{truth_frequency_pct:.2f}%" if truth_frequency > 0 else "",
            'Total Engagement': f"{truth_total_engagement:,}" if truth_total_engagement > 0 else "",
            'Average Engagement': f"{truth_avg_engagement:,.0f}" if truth_avg_engagement > 0 else ""
        })
    
    # Add total row
    total_engagement = df['Total_Engagement'].sum()
    total_avg_engagement = total_engagement / total_posts if total_posts > 0 else 0
    
    results.append({
        'Category ID': 'TOTAL',
        'Category Name': 'All Categories',
        'Platform': 'Combined',
        'Frequency (Count)': total_posts,
        'Frequency (%)': '100%',
        'Total Engagement': f"{total_engagement:,}",
        'Average Engagement': f"{total_avg_engagement:,.0f}"
    })
    
    return results

def save_results(results, output_file='Engagement_overall_result.csv'):
    """Save results to CSV file"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if output_file == 'Engagement_overall_result.csv':
        output_file = os.path.join(script_dir, output_file)
    df_result = pd.DataFrame(results)
    df_result.to_csv(output_file, index=False)
    print(f"Results saved to: {output_file}")
    return df_result

def main():
    """Main function"""
    print("Trump Policy Analysis - Macro Engagement Data Processing Script")
    print("=" * 60)
    
    # Load data
    df = load_processed_data()
    if df is None:
        return
    
    print(f"\nData overview:")
    print(f"- Total tags: {len(df)}")
    print(f"- Categories covered: {sorted(df['Category_id'].unique())}")
    print(f"- Total mentions: {df['Frequency (Count)'].sum()}")
    print(f"- Total engagement: {df['Total_Engagement'].sum():,}")
    
    # Calculate statistics
    results = calculate_category_stats(df)
    
    # Save results
    df_result = save_results(results)
    
    # Display results preview
    print(f"\nResults preview:")
    print(df_result.to_string(index=False))
    
    print(f"\nMacro data processing completed.")
    print(f"Output file: Engagement_overall_result.csv")

if __name__ == "__main__":
    main()
