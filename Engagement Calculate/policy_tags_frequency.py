#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Policy Tags Frequency Visualization Script for Trump Policy Analysis
Creates horizontal bar chart based on Engagement_data_processed.csv
Y-axis: Policy Tags (Tag_id)
X-axis: Frequency Percentage (Frequency %)

"""

import os
import sys
from pathlib import Path

# Import required libraries
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# Set chart style and font settings
plt.style.use('default')
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 16
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 9
plt.rcParams['legend.fontsize'] = 10
sns.set_palette("husl")

def find_data_file():
    """
    Automatically find the data file in current directory or parent directories
    """
    current_dir = Path.cwd()
    possible_paths = [
        current_dir / "Engagement_data_processed.csv",
        current_dir.parent / "Engagement_data_processed.csv",
        current_dir / "Engagement Calculate" / "Engagement_data_processed.csv",
        current_dir.parent / "Engagement Calculate" / "Engagement_data_processed.csv"
    ]
    
    for path in possible_paths:
        if path.exists():
            print(f"Found data file: {path}")
            return str(path)
    
    print("Could not find Engagement_data_processed.csv")
    print("Searched in:")
    for path in possible_paths:
        print(f"   - {path}")
    return None

def load_and_process_data(file_path=None):
    """
    Load and process data from CSV file with automatic file detection
    """
    try:
        # If no file path provided, try to find it automatically
        if file_path is None:
            file_path = find_data_file()
            if file_path is None:
                return None
        
        # Check if file exists
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return None
        
        # Read CSV file
        df = pd.read_csv(file_path)
        
        # Filter out rows with 0 frequency (policy tags with no data)
        df_filtered = df[df['Frequency (%)'] > 0].copy()
        
        # Sort by frequency percentage in ascending order for horizontal bar chart
        df_filtered = df_filtered.sort_values('Frequency (%)', ascending=True)
        
        print(f"Loaded data with {len(df_filtered)} active policy tags")
        print(f"Data range: {df_filtered['Frequency (%)'].min():.2f}% - {df_filtered['Frequency (%)'].max():.2f}%")
        
        return df_filtered
        
    except Exception as e:
        print(f"Data loading error: {e}")
        return None

def create_horizontal_bar_chart(df, save_path=None):
    """
    Create horizontal bar chart with improved label visibility
    """
    # Create figure with larger size to accommodate all labels
    fig, ax = plt.subplots(figsize=(14, 10))
    
    # Define category colors and labels
    category_info = {
        'A': {'color': '#2E86C1', 'label': 'Category A (Taming Bureaucracy)'},
        'B': {'color': '#E74C3C', 'label': 'Category B (Culture Wars)'},
        'C': {'color': '#28B463', 'label': 'Category C (Reshaping Power)'}
    }
    
    # Assign colors to each tag based on category
    bar_colors = [category_info[cat]['color'] for cat in df['Category_id']]
    
    # Create horizontal bar chart with adequate spacing
    y_positions = np.arange(len(df))
    bars = ax.barh(y_positions, df['Frequency (%)'], 
                   color=bar_colors, alpha=0.8, edgecolor='white', linewidth=1.5, height=0.7)
    
    # Set title and labels
    ax.set_title('Figure 1: Policy Tags Frequency in Trump\'s Social Media Content', 
                 fontsize=18, fontweight='bold', pad=25)
    ax.set_xlabel('Frequency Percentage (%)', fontsize=14, fontweight='bold')
    ax.set_ylabel('Policy Tag ID', fontsize=14, fontweight='bold')
    
    # Set y-axis labels with proper spacing
    ax.set_yticks(y_positions)
    ax.set_yticklabels(df['Tag_id'], fontsize=11)
    
    # Add value labels on bars with better positioning
    for i, (bar, freq) in enumerate(zip(bars, df['Frequency (%)'])):
        width = bar.get_width()
        # Position text based on bar width to avoid overlap
        if width > 10:  # For longer bars, put text inside
            ax.text(width - 1, bar.get_y() + bar.get_height()/2, 
                    f'{freq:.2f}%', ha='right', va='center', fontsize=10, 
                    fontweight='bold', color='white')
        else:  # For shorter bars, put text outside
            ax.text(width + 0.2, bar.get_y() + bar.get_height()/2, 
                    f'{freq:.2f}%', ha='left', va='center', fontsize=10, fontweight='bold')
    
    # Set grid for better readability
    ax.grid(True, axis='x', alpha=0.3, linestyle='--', linewidth=0.5)
    ax.set_axisbelow(True)
    
    # Set x-axis limits with some padding
    max_freq = df['Frequency (%)'].max()
    ax.set_xlim(0, max_freq * 1.15)
    
    # Create improved legend
    legend_elements = [plt.Rectangle((0,0),1,1, facecolor=category_info[cat]['color'], 
                                   alpha=0.8, label=category_info[cat]['label']) 
                      for cat in sorted(category_info.keys())]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=11, 
             frameon=True, fancybox=True, shadow=True)
    
    # Add statistics text box
    stats_text = f"Total Active Tags: {len(df)}\nFrequency Range: {df['Frequency (%)'].min():.2f}% - {df['Frequency (%)'].max():.2f}%\nAverage Frequency: {df['Frequency (%)'].mean():.2f}%"
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
            verticalalignment='top', horizontalalignment='left',
            bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8),
            fontsize=10)
    
    # Adjust layout with more padding
    plt.tight_layout(pad=2.0)
    
    # Save chart
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        print(f"Chart saved to: {save_path}")
    
    # Display chart
    plt.show()
    
    return fig, ax

def create_detailed_analysis(df):
    """
    Create detailed analysis report
    """
    print("\n" + "="*80)
    print("Detailed Policy Tags Frequency Analysis Report")
    print("="*80)
    
    # Basic statistics
    print(f"\nBasic Statistics:")
    print(f"   • Number of active policy tags: {len(df)}")
    print(f"   • Total mentions: {df['Frequency (Count)'].sum():,}")
    print(f"   • Average frequency percentage: {df['Frequency (%)'].mean():.2f}%")
    print(f"   • Frequency percentage std deviation: {df['Frequency (%)'].std():.2f}%")
    print(f"   • Frequency range: {df['Frequency (%)'].min():.2f}% - {df['Frequency (%)'].max():.2f}%")
    
    # Statistics by category
    print(f"\nStatistics by Category:")
    category_names = {
        'A': 'Taming Bureaucracy',
        'B': 'Culture Wars', 
        'C': 'Reshaping Power'
    }
    
    category_stats = df.groupby('Category_id').agg({
        'Frequency (Count)': 'sum',
        'Frequency (%)': 'sum',
        'Tag_id': 'count'
    }).round(2)
    category_stats.columns = ['Total Mentions', 'Total Frequency (%)', 'Number of Tags']
    
    for cat_id, row in category_stats.iterrows():
        print(f"   Category {cat_id} ({category_names[cat_id]}):")
        print(f"      - Tags: {int(row['Number of Tags'])}")
        print(f"      - Total Mentions: {int(row['Total Mentions']):,}")
        print(f"      - Total Frequency: {row['Total Frequency (%)']}%")
        print(f"      - Average per Tag: {row['Total Frequency (%)'] / row['Number of Tags']:.2f}%")
    
    # Top 5 policy tags
    print(f"\nTop 5 Policy Tags by Frequency:")
    top_5 = df.nlargest(5, 'Frequency (%)')
    for i, (idx, row) in enumerate(top_5.iterrows(), 1):
        print(f"   {i}. {row['Tag_id']}: {row['Frequency (%)']:.2f}% ({row['Frequency (Count)']} mentions) [Category {row['Category_id']}]")
    
    # Bottom 5 policy tags
    print(f"\nBottom 5 Policy Tags by Frequency:")
    bottom_5 = df.nsmallest(5, 'Frequency (%)')
    for i, (idx, row) in enumerate(bottom_5.iterrows(), 1):
        print(f"   {i}. {row['Tag_id']}: {row['Frequency (%)']:.2f}% ({row['Frequency (Count)']} mentions) [Category {row['Category_id']}]")
    
    print("\n" + "="*80)

def main():
    """
    Main function - IDE-friendly with automatic setup
    """
    print("=" * 80)
    print("Trump Policy Analysis - Policy Tags Frequency Visualization")
    print("=" * 80)
    print("Current working directory:", Path.cwd())
    
    # Automatically determine output file path
    current_dir = Path.cwd()
    output_file = current_dir / "policy_tags_frequency_chart.png"
    
    print(f"Chart will be saved to: {output_file}")
    print("\nStarting policy tags frequency visualization...")
    
    # Load data (automatic file detection)
    df = load_and_process_data()
    if df is None:
        print("\nCannot proceed without data file.")
        print("Make sure 'Engagement_data_processed.csv' exists in:")
        print("   - Current directory")
        print("   - Parent directory")
        print("   - Engagement Calculate folder")
        return
    
    # Verify we have all expected tags
    print(f"\nLoaded {len(df)} active policy tags (non-zero frequency)")
    print(f"Tags by category:")
    for cat in sorted(df['Category_id'].unique()):
        tags_in_cat = df[df['Category_id'] == cat]['Tag_id'].tolist()
        print(f"   Category {cat}: {len(tags_in_cat)} tags - {', '.join(tags_in_cat)}")
    
    # Create detailed analysis
    create_detailed_analysis(df)
    
    # Create chart
    print("\nGenerating horizontal bar chart with improved label visibility...")
    fig, ax = create_horizontal_bar_chart(df, str(output_file))
    
    print(f"\nPolicy tags frequency visualization completed.")
    print(f"Chart saved: {output_file}")
    print(f"All {len(df)} active policy tags are displayed in the chart")
    
    # Try to open the chart automatically (optional)
    try:
        if sys.platform == "darwin":  # macOS
            os.system(f"open '{output_file}'")
        elif sys.platform == "win32":  # Windows
            os.system(f"start '{output_file}'")
        elif sys.platform == "linux":  # Linux
            os.system(f"xdg-open '{output_file}'")
    except:
        pass  # Silently fail if can't open

if __name__ == "__main__":
    main()
