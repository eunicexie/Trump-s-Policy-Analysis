#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Strategic Signal Matrix Visualization Script for Trump Policy Analysis - X Platform Only
Creates a scatter plot showing the relationship between signal frequency and average engagement
for Trump's Government Reorganization Agenda on X Platform

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
    """Find the data file in current directory or parent directories"""
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

def calculate_x_frequency_percentage(df):
    """Calculate X platform specific frequency percentages"""
    # Get total X posts by counting non-zero X_Average_Engagement entries
    total_x_posts = 0
    
    # For frequency calculation, we need to consider how many times each tag appears on X platform
    # This requires calculating from the X engagement data
    for idx, row in df.iterrows():
        if row['X_Average_Engagement'] > 0:
            # Calculate frequency count for X platform specifically
            # X_Total_Engagement / X_Average_Engagement = X frequency count
            x_freq_count = row['X_Total_Engagement'] / row['X_Average_Engagement'] if row['X_Average_Engagement'] > 0 else 0
            df.at[idx, 'X_Frequency_Count'] = round(x_freq_count)
            total_x_posts += x_freq_count
        else:
            df.at[idx, 'X_Frequency_Count'] = 0
    
    # Calculate X platform frequency percentages
    for idx, row in df.iterrows():
        if total_x_posts > 0:
            x_freq_pct = (row['X_Frequency_Count'] / total_x_posts) * 100
            df.at[idx, 'X_Frequency_Percent'] = x_freq_pct
        else:
            df.at[idx, 'X_Frequency_Percent'] = 0
    
    return df, total_x_posts

def load_and_process_data(file_path=None):
    """Load and process X platform data from CSV file"""
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
        
        # Filter out rows with 0 X platform engagement (no X data)
        df_x_filtered = df[df['X_Average_Engagement'] > 0].copy()
        
        # Calculate X platform specific frequency percentages
        df_x_filtered, total_x_posts = calculate_x_frequency_percentage(df_x_filtered)
        
        print(f"Loaded X platform data with {len(df_x_filtered)} active policy tags")
        print(f"Total posts: {total_x_posts:.0f}, Range: {df_x_filtered['X_Frequency_Percent'].min():.2f}-{df_x_filtered['X_Frequency_Percent'].max():.2f}%, Engagement: {df_x_filtered['X_Average_Engagement'].min():.0f}-{df_x_filtered['X_Average_Engagement'].max():.0f}")
        
        return df_x_filtered
        
    except Exception as e:
        print(f"Data loading error: {e}")
        return None

def calculate_baselines(df):
    """Calculate baseline values for X platform frequency and average engagement"""
    avg_frequency = df['X_Frequency_Percent'].mean()
    median_engagement = df['X_Average_Engagement'].median()
    
    print(f"\nBaselines - Frequency: {avg_frequency:.2f}%, Engagement: {median_engagement:.0f}")
    
    return avg_frequency, median_engagement

def adjust_label_positions_simple(df, ax):
    """Position labels without connecting lines"""
    # Extended offset patterns to handle all tags with better distribution
    offset_patterns = [
        (10, 10), (-10, 10), (10, -10), (-10, -10),  # Diagonal corners
        (15, 0), (-15, 0), (0, 15), (0, -15),        # Cardinal directions
        (12, 6), (-12, 6), (12, -6), (-12, -6),      # Diagonal offsets
        (6, 12), (-6, 12), (6, -12), (-6, -12),      # More diagonal offsets
        (8, 8), (-8, -8), (14, 4), (-14, -4),        # Additional patterns
        (4, 14), (-4, -14), (18, 2), (-18, -2)       # Extra patterns for safety
    ]
    
    # Position labels with varied offsets
    
    for i, (idx, row) in enumerate(df.iterrows()):
        offset = offset_patterns[i % len(offset_patterns)]
        # Position label for {row['Tag_id']}
        
        ax.annotate(
            row['Tag_id'],
            (row['X_Frequency_Percent'], row['X_Average_Engagement']),
            xytext=offset,
            textcoords='offset points',
            fontsize=10,
            fontweight='bold',
            ha='center',
            va='center',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.95, edgecolor='gray', linewidth=0.8),
            zorder=10  # Ensure labels appear on top
            # No arrowprops - cleaner look without connecting lines
        )

def create_strategic_signal_matrix(df, save_path=None):
    """Create the strategic signal matrix scatter plot for X platform"""
    # Calculate baselines (using median for engagement)
    avg_frequency, median_engagement = calculate_baselines(df)
    
    # Create figure and axis with larger size for better label visibility
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    
    # Define colors and markers for each category (same as original)
    category_styles = {
        'A': {'color': '#2E86C1', 'marker': 'o', 'label': 'Category A (Taming Bureaucracy)', 'size': 120},
        'B': {'color': '#E74C3C', 'marker': 's', 'label': 'Category B (Culture Wars)', 'size': 120},
        'C': {'color': '#28B463', 'marker': '^', 'label': 'Category C (Reshaping Power)', 'size': 140}
    }
    
    # Plot data points for each category
    for category, style in category_styles.items():
        category_data = df[df['Category_id'] == category]
        
        if len(category_data) > 0:  # Only plot if category has data on X platform
            scatter = ax.scatter(
                category_data['X_Frequency_Percent'], 
                category_data['X_Average_Engagement'],
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
    
    # Add data point labels with simple clean positioning (no connecting lines)
    adjust_label_positions_simple(df, ax)
    
    # Get data ranges for axis limits
    max_freq = df['X_Frequency_Percent'].max()
    min_freq = df['X_Frequency_Percent'].min()
    max_engage = df['X_Average_Engagement'].max()
    min_engage = df['X_Average_Engagement'].min()
    
    # Customize the plot (X platform version)
    ax.set_xlabel('Signal Frequency on X Platform (%)', fontsize=14, fontweight='bold')
    ax.set_ylabel('Average Engagement on X Platform', fontsize=14, fontweight='bold')
    ax.set_title('Policy Tags Frequency of Trump X Contents', 
                 fontsize=18, fontweight='bold', pad=25)
    
    # Set axis limits with generous padding
    x_margin = (max_freq - min_freq) * 0.15 if max_freq > min_freq else 1
    y_margin = (max_engage - min_engage) * 0.15 if max_engage > min_engage else 1000
    
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
    
    # Add statistics text box (X platform version)
    total_x_posts = df['X_Frequency_Count'].sum()
    stats_text = f"""X Platform Data Statistics:
• Active Policy Tags: {len(df)}
• Total X Platform Posts: {total_x_posts:.0f}
• Average Frequency: {avg_frequency:.2f}%
• Median Engagement: {median_engagement:.0f}
• Frequency Range: {min_freq:.2f}% - {max_freq:.2f}%
• Engagement Range: {min_engage:.0f} - {max_engage:.0f}"""
    
    # Place statistics text box below the legend with larger size (moved left and down)
    ax.text(0.70, 0.72, stats_text, transform=ax.transAxes, 
            verticalalignment='top', horizontalalignment='left',
            bbox=dict(boxstyle='round,pad=0.8', facecolor='lightblue', alpha=0.8, linewidth=1.5),
            fontsize=12, fontfamily='monospace')
    
    # Adjust layout with more padding
    plt.tight_layout(pad=2.0)
    
    # Save the plot
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"Chart saved to: {save_path}")
    
    return fig, ax

def create_detailed_analysis(df):
    """Create detailed analysis of the strategic signal matrix for X platform"""
    avg_frequency, median_engagement = calculate_baselines(df)
    
    print("\n" + "="*80)
    print("Strategic Signal Matrix Analysis Report - X Platform Only")
    print("="*80)
    
    # Classify data points into quadrants (using median for engagement baseline)
    quadrants = {
        'core_strategic': df[(df['X_Frequency_Percent'] >= avg_frequency) & (df['X_Average_Engagement'] >= median_engagement)],
        'high_efficiency': df[(df['X_Frequency_Percent'] < avg_frequency) & (df['X_Average_Engagement'] >= median_engagement)],
        'strong_push': df[(df['X_Frequency_Percent'] >= avg_frequency) & (df['X_Average_Engagement'] < median_engagement)],
        'marginal': df[(df['X_Frequency_Percent'] < avg_frequency) & (df['X_Average_Engagement'] < median_engagement)]
    }
    
    quadrant_names = {
        'core_strategic': 'Core Strategic Signals on X (High Frequency + High Engagement)',
        'high_efficiency': 'High Efficiency Opportunity Signals on X (Low Frequency + High Engagement)', 
        'strong_push': 'Strong Push Agenda Signals on X (High Frequency + Low Engagement)',
        'marginal': 'Marginal Signals on X (Low Frequency + Low Engagement)'
    }
    
    for quad_key, quad_data in quadrants.items():
        print(f"\n{quadrant_names[quad_key]}:")
        if len(quad_data) > 0:
            for idx, row in quad_data.iterrows():
                print(f"   • {row['Tag_id']}: {row['X_Frequency_Percent']:.2f}% frequency, {row['X_Average_Engagement']:.0f} avg engagement [Category {row['Category_id']}]")
        else:
            print("   • No data points")
    
    # Category analysis (X platform version)
    print(f"\nAnalysis by Category (X Platform Only):")
    category_names = {'A': 'Taming Bureaucracy', 'B': 'Culture Wars', 'C': 'Reshaping Power'}
    
    for category in ['A', 'B', 'C']:
        cat_data = df[df['Category_id'] == category]
        
        if len(cat_data) > 0:
            print(f"\nCategory {category} ({category_names[category]}):")
            print(f"   • Number of Active Tags on X: {len(cat_data)}")
            print(f"   • Average Frequency on X: {cat_data['X_Frequency_Percent'].mean():.2f}%")
            print(f"   • Average Engagement on X: {cat_data['X_Average_Engagement'].mean():.0f}")
            print(f"   • Frequency Range on X: {cat_data['X_Frequency_Percent'].min():.2f}% - {cat_data['X_Frequency_Percent'].max():.2f}%")
            print(f"   • Engagement Range on X: {cat_data['X_Average_Engagement'].min():.0f} - {cat_data['X_Average_Engagement'].max():.0f}")
            print(f"   • Active Tags on X: {', '.join(cat_data['Tag_id'].tolist())}")
        else:
            print(f"\nCategory {category} ({category_names[category]}):")
            print("   • No active tags on X platform")
    
    # Additional insights for X platform
    print(f"\nKey Insights (X Platform Only):")
    
    # Most frequent tag on X
    top_freq_tag = df.loc[df['X_Frequency_Percent'].idxmax()]
    print(f"   • Highest Frequency on X: {top_freq_tag['Tag_id']} ({top_freq_tag['X_Frequency_Percent']:.2f}%)")
    
    # Most engaging tag on X
    top_engage_tag = df.loc[df['X_Average_Engagement'].idxmax()]
    print(f"   • Highest Engagement on X: {top_engage_tag['Tag_id']} ({top_engage_tag['X_Average_Engagement']:.0f} avg engagement)")
    
    # Category dominance on X
    category_totals = df.groupby('Category_id')['X_Frequency_Percent'].sum().sort_values(ascending=False)
    print(f"   • Category by Total Frequency on X: {', '.join([f'{cat} ({freq:.1f}%)' for cat, freq in category_totals.items()])}")
    
    print("\n" + "="*80)

def main():
    """Main function for X platform analysis"""
    print("=" * 80)
    print("Trump Policy Analysis - Strategic Signal Matrix Visualization (X Platform Only)")
    print("=" * 80)
    print("Current working directory:", Path.cwd())
    
    # Automatically determine output file path
    script_dir = Path(__file__).parent.absolute()
    output_file = script_dir / "strategic_signal_matrix_X.png"
    
    print(f"Chart will be saved to: {output_file}")
    print("\nStarting X platform strategic signal matrix processing...")
    
    # Load data (automatic file detection)
    df = load_and_process_data()
    if df is None:
        print("\nCannot proceed without data file.")
        print("Make sure 'Engagement_data_processed.csv' exists in:")
        print("   - Current directory")
        print("   - Parent directory")
        print("   - Engagement Calculate folder")
        return
    
    # Verify we have X platform data
    print(f"\nLoaded {len(df)} active policy tags with X platform data")
    print(f"X Platform tags by category:")
    for cat in sorted(df['Category_id'].unique()):
        tags_in_cat = df[df['Category_id'] == cat]['Tag_id'].tolist()
        category_names = {'A': 'Taming Bureaucracy', 'B': 'Culture Wars', 'C': 'Reshaping Power'}
        print(f"   Category {cat} ({category_names[cat]}): {len(tags_in_cat)} tags - {', '.join(tags_in_cat)}")
    
    # Create detailed analysis
    create_detailed_analysis(df)
    
    # Create strategic signal matrix
    print("\nGenerating X platform strategic signal matrix with improved label positioning...")
    fig, ax = create_strategic_signal_matrix(df, str(output_file))
    
    print(f"\nX Platform strategic signal matrix visualization completed.")
    print(f"Chart saved: {output_file}")
    print(f"All {len(df)} active X platform policy tags are displayed in the scatter plot")
    
    # Try to open the chart
    try:
        if sys.platform == "darwin":
            os.system(f"open '{output_file}'")
        elif sys.platform == "win32":
            os.system(f"start '{output_file}'")
    except:
        pass

if __name__ == "__main__":
    main()
