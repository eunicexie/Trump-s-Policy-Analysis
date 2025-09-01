#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Strategic Signal Matrix Visualization Script for Trump Policy Analysis - Truth Media Platform Only
Creates a scatter plot showing the relationship between signal frequency and average engagement
for Trump's Government Reorganization Agenda on Truth Media Platform

"""

import os
import sys
from pathlib import Path

# Import required libraries
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# Set matplotlib backend and style
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 16
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['legend.fontsize'] = 11
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False  # Fix minus sign display
plt.style.use('default')

def find_data_file():
    """
    Automatically find the data file in current directory or parent directories
    """
    script_dir = Path(__file__).parent.absolute()
    current_dir = Path.cwd()
    
    possible_paths = [
        script_dir / "Engagement_data_processed.csv",  # Script directory first
        current_dir / "Engagement_data_processed.csv",  # Current working directory
        current_dir / "Engagement Calculate" / "Engagement_data_processed.csv",  # From root
        script_dir.parent / "Engagement_data_processed.csv",  # Parent of script
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

def calculate_truth_frequency_percentage(df):
    """
    Calculate Truth Media platform specific frequency percentages
    For Truth Media platform, we need to calculate frequency based on total Truth Media posts, not all posts
    """
    # Get total Truth Media posts by counting non-zero Truth_Average_Engagement entries
    total_truth_posts = 0
    
    # For frequency calculation, we need to consider how many times each tag appears on Truth Media platform
    # This requires calculating from the Truth Media engagement data
    for idx, row in df.iterrows():
        if row['Truth_Average_Engagement'] > 0:
            # Calculate frequency count for Truth Media platform specifically
            # Truth_Total_Engagement / Truth_Average_Engagement = Truth frequency count
            truth_freq_count = row['Truth_Total_Engagement'] / row['Truth_Average_Engagement'] if row['Truth_Average_Engagement'] > 0 else 0
            df.at[idx, 'Truth_Frequency_Count'] = round(truth_freq_count)
            total_truth_posts += truth_freq_count
        else:
            df.at[idx, 'Truth_Frequency_Count'] = 0
    
    # Calculate Truth Media platform frequency percentages
    for idx, row in df.iterrows():
        if total_truth_posts > 0:
            truth_freq_pct = (row['Truth_Frequency_Count'] / total_truth_posts) * 100
            df.at[idx, 'Truth_Frequency_Percent'] = truth_freq_pct
        else:
            df.at[idx, 'Truth_Frequency_Percent'] = 0
    
    return df, total_truth_posts

def load_and_process_data(file_path=None):
    """
    Load and process data from CSV file with automatic file detection
    Filter for Truth Media platform data only
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
        
        # Filter out rows with 0 Truth Media platform engagement (no Truth Media data)
        df_truth_filtered = df[df['Truth_Average_Engagement'] > 0].copy()
        
        # Calculate Truth Media platform specific frequency percentages
        df_truth_filtered, total_truth_posts = calculate_truth_frequency_percentage(df_truth_filtered)
        
        print(f"Loaded Truth Media platform data with {len(df_truth_filtered)} active policy tags")
        print(f"Total Truth Media platform posts: {total_truth_posts:.0f}")
        print(f"Truth Frequency range: {df_truth_filtered['Truth_Frequency_Percent'].min():.2f}% - {df_truth_filtered['Truth_Frequency_Percent'].max():.2f}%")
        print(f"Truth Engagement range: {df_truth_filtered['Truth_Average_Engagement'].min():.0f} - {df_truth_filtered['Truth_Average_Engagement'].max():.0f}")
        
        return df_truth_filtered
        
    except Exception as e:
        print(f"Data loading error: {e}")
        return None

def calculate_baselines(df):
    """
    Calculate baseline values for Truth Media platform frequency and average engagement
    Uses median for engagement to avoid outlier influence
    """
    avg_frequency = df['Truth_Frequency_Percent'].mean()
    median_engagement = df['Truth_Average_Engagement'].median()
    
    print(f"\nCalculated Truth Media Platform Baselines:")
    print(f"   Average Frequency: {avg_frequency:.2f}%")
    print(f"   Median Engagement: {median_engagement:.0f}")
    print(f"   (Note: Using median instead of mean to avoid outlier influence)")
    
    return avg_frequency, median_engagement

def adjust_label_positions_hybrid(df, ax):
    """
    Hybrid label positioning approach:
    - Only B3, A4, C1 use arrow connections (due to overlapping at 6.38%)
    - All other labels use simple close positioning without arrows
    """
    # Tags that need arrow connections due to overlapping positions
    arrow_tags = {'B3', 'A4', 'C1'}
    
    # Large offsets for arrow tags to completely avoid overlaps
    arrow_offsets = {
        'B3': (70, 40),   # Far right-up
        'A4': (-80, 35),  # Far left-up  
        'C1': (-45, 70),  # Left-up high
    }
    
    # Simple close offsets for non-overlapping tags (no arrows)
    simple_offsets = [
        (12, 8), (-12, 8), (12, -8), (-12, -8),       # Small diagonal
        (15, 0), (-15, 0), (0, 15), (0, -15),         # Small cardinal
        (10, 12), (-10, 12), (10, -12), (-10, -12),   # Small diagonal alt
        (18, 6), (-18, 6), (18, -6), (-18, -6),       # Medium diagonal
        (8, 18), (-8, 18), (8, -18), (-8, -18),       # Medium vertical
    ]
    
    print(f"Positioning {len(df)} labels with hybrid approach (arrows only for overlapping tags)...")
    
    simple_offset_index = 0
    
    for i, (idx, row) in enumerate(df.iterrows()):
        tag_id = row['Tag_id']
        
        if tag_id in arrow_tags:
            # Use arrow connection for overlapping tags
            offset = arrow_offsets[tag_id]
            print(f"   Label {i+1}: {tag_id} at ({row['Truth_Frequency_Percent']:.2f}%, {row['Truth_Average_Engagement']:.0f}) with ARROW offset {offset}")
            
            ax.annotate(
                tag_id,
                (row['Truth_Frequency_Percent'], row['Truth_Average_Engagement']),
                xytext=offset,
                textcoords='offset points',
                fontsize=10,
                fontweight='bold',
                ha='center',
                va='center',
                bbox=dict(boxstyle='round,pad=0.4', facecolor='lightyellow', alpha=0.95, 
                         edgecolor='orange', linewidth=1.2),
                arrowprops=dict(
                    arrowstyle='->', 
                    connectionstyle='arc3,rad=0.1',
                    color='orange', 
                    alpha=0.8,
                    linewidth=1.5
                ),
                zorder=10
            )
        else:
            # Use simple close positioning for other tags (no arrows)
            offset = simple_offsets[simple_offset_index % len(simple_offsets)]
            simple_offset_index += 1
            print(f"   Label {i+1}: {tag_id} at ({row['Truth_Frequency_Percent']:.2f}%, {row['Truth_Average_Engagement']:.0f}) with SIMPLE offset {offset}")
            
            ax.annotate(
                tag_id,
                (row['Truth_Frequency_Percent'], row['Truth_Average_Engagement']),
                xytext=offset,
                textcoords='offset points',
                fontsize=10,
                fontweight='bold',
                ha='center',
                va='center',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.95, 
                         edgecolor='gray', linewidth=0.8),
                zorder=10
                # No arrowprops - clean close positioning
            )

def create_strategic_signal_matrix(df, save_path=None):
    """
    Create the strategic signal matrix scatter plot for Truth Media platform with improved English labels
    """
    # Calculate baselines (using median for engagement)
    avg_frequency, median_engagement = calculate_baselines(df)
    
    # Create figure and axis with larger size for better label visibility and spacing
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    
    # Define colors and markers for each category (same as original)
    category_styles = {
        'A': {'color': '#2E86C1', 'marker': 'o', 'label': 'Category A (Taming Bureaucracy)', 'size': 120},
        'B': {'color': '#E74C3C', 'marker': 's', 'label': 'Category B (Culture Wars)', 'size': 120},
        'C': {'color': '#28B463', 'marker': '^', 'label': 'Category C (Reshaping Power)', 'size': 140}
    }
    
    # Plot data points for each category
    for category, style in category_styles.items():
        category_data = df[df['Category_id'] == category]
        
        if len(category_data) > 0:  # Only plot if category has data on Truth Media platform
            scatter = ax.scatter(
                category_data['Truth_Frequency_Percent'], 
                category_data['Truth_Average_Engagement'],
                c=style['color'],
                marker=style['marker'],
                s=style['size'],
                alpha=0.8,
                label=style['label'],
                edgecolors='white',
                linewidth=2
            )
    
    # Add baseline lines (blue frequency line, red engagement line)
    ax.axvline(x=avg_frequency, color='blue', linestyle='--', alpha=0.7, linewidth=2, label='Average Frequency Baseline')
    ax.axhline(y=median_engagement, color='red', linestyle='--', alpha=0.7, linewidth=2, label='Median Engagement Baseline')
    
    # Add data point labels with hybrid approach (arrows only for overlapping tags)
    adjust_label_positions_hybrid(df, ax)
    
    # Get data ranges for axis limits
    max_freq = df['Truth_Frequency_Percent'].max()
    min_freq = df['Truth_Frequency_Percent'].min()
    max_engage = df['Truth_Average_Engagement'].max()
    min_engage = df['Truth_Average_Engagement'].min()
    
    # Customize the plot (Truth Media platform version)
    ax.set_xlabel('Signal Frequency on Truth Media Platform (%)', fontsize=14, fontweight='bold')
    ax.set_ylabel('Average Engagement on Truth Media Platform', fontsize=14, fontweight='bold')
    ax.set_title('Policy Tags Frequency of Trump Truth Media Contents', 
                 fontsize=18, fontweight='bold', pad=25)
    
    # Set axis limits with extra generous padding for labels
    x_margin = (max_freq - min_freq) * 0.25 if max_freq > min_freq else 1
    y_margin = (max_engage - min_engage) * 0.25 if max_engage > min_engage else 1000
    
    ax.set_xlim(min_freq - x_margin, max_freq + x_margin)
    ax.set_ylim(min_engage - y_margin, max_engage + y_margin)
    
    # Add improved grid
    ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
    ax.set_axisbelow(True)
    
    # Create improved legend with larger font
    legend = ax.legend(loc='upper right', frameon=True, fancybox=True, shadow=True, fontsize=13)
    legend.get_frame().set_facecolor('white')
    legend.get_frame().set_alpha(0.95)
    legend.get_frame().set_linewidth(1.5)
    
    # Add statistics text box (Truth Media platform version)
    total_truth_posts = df['Truth_Frequency_Count'].sum()
    stats_text = f"""Truth Media Platform Data Statistics:
• Active Policy Tags: {len(df)}
• Total Truth Media Posts: {total_truth_posts:.0f}
• Average Frequency: {avg_frequency:.2f}%
• Median Engagement: {median_engagement:.0f}
• Frequency Range: {min_freq:.2f}% - {max_freq:.2f}%
• Engagement Range: {min_engage:.0f} - {max_engage:.0f}"""
    
    # Place statistics text box below the legend with larger size
    ax.text(0.47, 0.98, stats_text, transform=ax.transAxes, 
            verticalalignment='top', horizontalalignment='left',
            bbox=dict(boxstyle='round,pad=0.8', facecolor='lightgreen', alpha=0.8, linewidth=1.5),
            fontsize=12, fontfamily='monospace')
    
    # Adjust layout with more padding
    plt.tight_layout(pad=2.0)
    
    # Save the plot
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"Chart saved to: {save_path}")
    
    return fig, ax

def create_detailed_analysis(df):
    """
    Create detailed analysis of the strategic signal matrix for Truth Media platform
    """
    avg_frequency, median_engagement = calculate_baselines(df)
    
    print("\n" + "="*80)
    print("Strategic Signal Matrix Analysis Report - Truth Media Platform Only")
    print("="*80)
    
    # Classify data points into quadrants (using median for engagement baseline)
    quadrants = {
        'core_strategic': df[(df['Truth_Frequency_Percent'] >= avg_frequency) & (df['Truth_Average_Engagement'] >= median_engagement)],
        'high_efficiency': df[(df['Truth_Frequency_Percent'] < avg_frequency) & (df['Truth_Average_Engagement'] >= median_engagement)],
        'strong_push': df[(df['Truth_Frequency_Percent'] >= avg_frequency) & (df['Truth_Average_Engagement'] < median_engagement)],
        'marginal': df[(df['Truth_Frequency_Percent'] < avg_frequency) & (df['Truth_Average_Engagement'] < median_engagement)]
    }
    
    quadrant_names = {
        'core_strategic': 'Core Strategic Signals on Truth Media (High Frequency + High Engagement)',
        'high_efficiency': 'High Efficiency Opportunity Signals on Truth Media (Low Frequency + High Engagement)', 
        'strong_push': 'Strong Push Agenda Signals on Truth Media (High Frequency + Low Engagement)',
        'marginal': 'Marginal Signals on Truth Media (Low Frequency + Low Engagement)'
    }
    
    for quad_key, quad_data in quadrants.items():
        print(f"\n{quadrant_names[quad_key]}:")
        if len(quad_data) > 0:
            for idx, row in quad_data.iterrows():
                print(f"   • {row['Tag_id']}: {row['Truth_Frequency_Percent']:.2f}% frequency, {row['Truth_Average_Engagement']:.0f} avg engagement [Category {row['Category_id']}]")
        else:
            print("   • No data points")
    
    # Category analysis (Truth Media platform version)
    print(f"\nAnalysis by Category (Truth Media Platform Only):")
    category_names = {'A': 'Taming Bureaucracy', 'B': 'Culture Wars', 'C': 'Reshaping Power'}
    
    for category in ['A', 'B', 'C']:
        cat_data = df[df['Category_id'] == category]
        
        if len(cat_data) > 0:
            print(f"\nCategory {category} ({category_names[category]}):")
            print(f"   • Number of Active Tags on Truth Media: {len(cat_data)}")
            print(f"   • Average Frequency on Truth Media: {cat_data['Truth_Frequency_Percent'].mean():.2f}%")
            print(f"   • Average Engagement on Truth Media: {cat_data['Truth_Average_Engagement'].mean():.0f}")
            print(f"   • Frequency Range on Truth Media: {cat_data['Truth_Frequency_Percent'].min():.2f}% - {cat_data['Truth_Frequency_Percent'].max():.2f}%")
            print(f"   • Engagement Range on Truth Media: {cat_data['Truth_Average_Engagement'].min():.0f} - {cat_data['Truth_Average_Engagement'].max():.0f}")
            print(f"   • Active Tags on Truth Media: {', '.join(cat_data['Tag_id'].tolist())}")
        else:
            print(f"\nCategory {category} ({category_names[category]}):")
            print("   • No active tags on Truth Media platform")
    
    # Additional insights for Truth Media platform
    print(f"\nKey Insights (Truth Media Platform Only):")
    
    # Most frequent tag on Truth Media
    top_freq_tag = df.loc[df['Truth_Frequency_Percent'].idxmax()]
    print(f"   • Highest Frequency on Truth Media: {top_freq_tag['Tag_id']} ({top_freq_tag['Truth_Frequency_Percent']:.2f}%)")
    
    # Most engaging tag on Truth Media
    top_engage_tag = df.loc[df['Truth_Average_Engagement'].idxmax()]
    print(f"   • Highest Engagement on Truth Media: {top_engage_tag['Tag_id']} ({top_engage_tag['Truth_Average_Engagement']:.0f} avg engagement)")
    
    # Category dominance on Truth Media
    category_totals = df.groupby('Category_id')['Truth_Frequency_Percent'].sum().sort_values(ascending=False)
    print(f"   • Category by Total Frequency on Truth Media: {', '.join([f'{cat} ({freq:.1f}%)' for cat, freq in category_totals.items()])}")
    
    print("\n" + "="*80)

def main():
    """
    Main function - IDE-friendly with automatic setup (Truth Media platform version)
    """
    print("=" * 80)
    print("Trump Policy Analysis - Strategic Signal Matrix Visualization (Truth Media Platform Only)")
    print("=" * 80)
    print("Current working directory:", Path.cwd())
    
    # Automatically determine output file path
    script_dir = Path(__file__).parent.absolute()
    output_file = script_dir / "strategic_signal_matrix_truth_media.png"
    
    print(f"Chart will be saved to: {output_file}")
    print("\nStarting Truth Media platform strategic signal matrix processing...")
    
    # Load data (automatic file detection)
    df = load_and_process_data()
    if df is None:
        print("\nCannot proceed without data file.")
        print("Make sure 'Engagement_data_processed.csv' exists in:")
        print("   - Current directory")
        print("   - Parent directory")
        print("   - Engagement Calculate folder")
        return
    
    # Verify we have Truth Media platform data
    print(f"\nLoaded {len(df)} active policy tags with Truth Media platform data")
    print(f"Truth Media Platform tags by category:")
    for cat in sorted(df['Category_id'].unique()):
        tags_in_cat = df[df['Category_id'] == cat]['Tag_id'].tolist()
        category_names = {'A': 'Taming Bureaucracy', 'B': 'Culture Wars', 'C': 'Reshaping Power'}
        print(f"   Category {cat} ({category_names[cat]}): {len(tags_in_cat)} tags - {', '.join(tags_in_cat)}")
    
    # Create detailed analysis
    create_detailed_analysis(df)
    
    # Create strategic signal matrix
    print("\nGenerating Truth Media platform strategic signal matrix with improved label positioning...")
    fig, ax = create_strategic_signal_matrix(df, str(output_file))
    
    print(f"\nTruth Media Platform strategic signal matrix visualization completed.")
    print(f"Chart saved: {output_file}")
    print(f"All {len(df)} active Truth Media platform policy tags are displayed in the scatter plot")
    
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
