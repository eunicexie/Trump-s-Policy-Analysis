#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Strategic Signal Matrix Visualization Script for Trump Policy Analysis
Creates a scatter plot showing the relationship between signal frequency and average engagement
for Trump's Government Reorganization Agenda

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
        
        print(f"Loaded data with {len(df_filtered)} active policy tags")
        print(f"Frequency range: {df_filtered['Frequency (%)'].min():.2f}% - {df_filtered['Frequency (%)'].max():.2f}%")
        print(f"Engagement range: {df_filtered['Average_Engagement'].min():.0f} - {df_filtered['Average_Engagement'].max():.0f}")
        
        return df_filtered
        
    except Exception as e:
        print(f"Data loading error: {e}")
        return None

def calculate_baselines(df):
    """
    Calculate baseline values for frequency and average engagement
    """
    avg_frequency = df['Frequency (%)'].mean()
    avg_engagement = df['Average_Engagement'].mean()
    
    print(f"\nCalculated Baselines:")
    print(f"   Average Frequency: {avg_frequency:.2f}%")
    print(f"   Average Engagement: {avg_engagement:.0f}")
    
    return avg_frequency, avg_engagement

def adjust_label_positions_simple(df, ax):
    """
    Simple label positioning without connecting lines - cleaner look
    Ensures all 15 labels are visible with varied offsets
    """
    # Extended offset patterns to handle all 15 tags with better distribution
    offset_patterns = [
        (10, 10), (-10, 10), (10, -10), (-10, -10),  # Diagonal corners
        (15, 0), (-15, 0), (0, 15), (0, -15),        # Cardinal directions
        (12, 6), (-12, 6), (12, -6), (-12, -6),      # Diagonal offsets
        (6, 12), (-6, 12), (6, -12), (-6, -12),      # More diagonal offsets
        (8, 8), (-8, -8), (14, 4), (-14, -4),        # Additional patterns
        (4, 14), (-4, -14), (18, 2), (-18, -2)       # Extra patterns for safety
    ]
    
    print(f"Positioning {len(df)} labels...")
    
    for i, (idx, row) in enumerate(df.iterrows()):
        offset = offset_patterns[i % len(offset_patterns)]
        print(f"   Label {i+1}: {row['Tag_id']} at ({row['Frequency (%)']:.2f}%, {row['Average_Engagement']:.0f}) with offset {offset}")
        
        ax.annotate(
            row['Tag_id'],
            (row['Frequency (%)'], row['Average_Engagement']),
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
    """
    Create the strategic signal matrix scatter plot with improved English labels
    """
    # Calculate baselines
    avg_frequency, avg_engagement = calculate_baselines(df)
    
    # Create figure and axis with larger size for better label visibility
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    
    # Define colors and markers for each category
    category_styles = {
        'A': {'color': '#2E86C1', 'marker': 'o', 'label': 'Category A (Taming Bureaucracy)', 'size': 120},
        'B': {'color': '#E74C3C', 'marker': 's', 'label': 'Category B (Culture Wars)', 'size': 120},
        'C': {'color': '#28B463', 'marker': '^', 'label': 'Category C (Reshaping Power)', 'size': 140}
    }
    
    # Plot data points for each category
    for category, style in category_styles.items():
        category_data = df[df['Category_id'] == category]
        
        scatter = ax.scatter(
            category_data['Frequency (%)'], 
            category_data['Average_Engagement'],
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
    ax.axhline(y=avg_engagement, color='red', linestyle='--', alpha=0.7, linewidth=2, label='Average Engagement Baseline')
    
    # Add data point labels with simple clean positioning (no connecting lines)
    adjust_label_positions_simple(df, ax)
    
    # Get data ranges for axis limits
    max_freq = df['Frequency (%)'].max()
    min_freq = df['Frequency (%)'].min()
    max_engage = df['Average_Engagement'].max()
    min_engage = df['Average_Engagement'].min()
    
    # Customize the plot
    ax.set_xlabel('Signal Frequency (%)', fontsize=14, fontweight='bold')
    ax.set_ylabel('Average Engagement', fontsize=14, fontweight='bold')
    ax.set_title('Policy Tags Frequency of Trump Social Media Contents', 
                 fontsize=18, fontweight='bold', pad=25)
    
    # Set axis limits with generous padding
    x_margin = (max_freq - min_freq) * 0.15
    y_margin = (max_engage - min_engage) * 0.15
    
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
    
    # Add statistics text box
    stats_text = f"""Data Statistics:
• Active Policy Tags: {len(df)}
• Average Frequency: {avg_frequency:.2f}%
• Average Engagement: {avg_engagement:.0f}
• Frequency Range: {min_freq:.2f}% - {max_freq:.2f}%
• Engagement Range: {min_engage:.0f} - {max_engage:.0f}"""
    
    # Place statistics text box below the legend with larger size
    ax.text(0.707, 0.80, stats_text, transform=ax.transAxes, 
            verticalalignment='top', horizontalalignment='left',
            bbox=dict(boxstyle='round,pad=0.8', facecolor='lightblue', alpha=0.8, linewidth=1.5),
            fontsize=12, fontfamily='monospace')
    
    # Adjust layout with more padding
    plt.tight_layout(pad=2.0)
    
    # Save the plot
    if save_path:
        try:
            print(f"Attempting to save chart to: {save_path}")
            plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
            print(f"Chart successfully saved to: {save_path}")
            
            # Verify file was created
            if Path(save_path).exists():
                file_size = Path(save_path).stat().st_size
                print(f"File verification: {save_path} exists, size: {file_size:,} bytes")
            else:
                print(f"Warning: File was not created at {save_path}")
        except Exception as e:
            print(f"Error saving chart: {e}")
            print(f"Trying to save to current directory instead...")
            try:
                fallback_path = Path.cwd() / "strategic_signal_matrix_overall.png"
                plt.savefig(fallback_path, dpi=300, bbox_inches='tight', facecolor='white')
                print(f"Chart saved to fallback location: {fallback_path}")
            except Exception as e2:
                print(f"Failed to save to fallback location: {e2}")
    
    return fig, ax

def create_detailed_analysis(df):
    """Create detailed analysis of the strategic signal matrix"""
    avg_frequency, avg_engagement = calculate_baselines(df)
    
    print("\n" + "="*80)
    print("Strategic Signal Matrix Analysis Report")
    print("="*80)
    
    # Classify data points into quadrants
    quadrants = {
        'core_strategic': df[(df['Frequency (%)'] >= avg_frequency) & (df['Average_Engagement'] >= avg_engagement)],
        'high_efficiency': df[(df['Frequency (%)'] < avg_frequency) & (df['Average_Engagement'] >= avg_engagement)],
        'strong_push': df[(df['Frequency (%)'] >= avg_frequency) & (df['Average_Engagement'] < avg_engagement)],
        'marginal': df[(df['Frequency (%)'] < avg_frequency) & (df['Average_Engagement'] < avg_engagement)]
    }
    
    quadrant_names = {
        'core_strategic': 'Core Strategic Signals (High Frequency + High Engagement)',
        'high_efficiency': 'High Efficiency Opportunity Signals (Low Frequency + High Engagement)', 
        'strong_push': 'Strong Push Agenda Signals (High Frequency + Low Engagement)',
        'marginal': 'Marginal Signals (Low Frequency + Low Engagement)'
    }
    
    for quad_key, quad_data in quadrants.items():
        print(f"\n{quadrant_names[quad_key]}:")
        if len(quad_data) > 0:
            for idx, row in quad_data.iterrows():
                print(f"   • {row['Tag_id']}: {row['Frequency (%)']:.2f}% frequency, {row['Average_Engagement']:.0f} avg engagement [Category {row['Category_id']}]")
        else:
            print("   • No data points")
    
    # Category analysis
    print(f"\nAnalysis by Category:")
    category_names = {'A': 'Taming Bureaucracy', 'B': 'Culture Wars', 'C': 'Reshaping Power'}
    
    for category in ['A', 'B', 'C']:
        cat_data = df[df['Category_id'] == category]
        
        print(f"\nCategory {category} ({category_names[category]}):")
        print(f"   • Number of Tags: {len(cat_data)}")
        print(f"   • Average Frequency: {cat_data['Frequency (%)'].mean():.2f}%")
        print(f"   • Average Engagement: {cat_data['Average_Engagement'].mean():.0f}")
        print(f"   • Frequency Range: {cat_data['Frequency (%)'].min():.2f}% - {cat_data['Frequency (%)'].max():.2f}%")
        print(f"   • Engagement Range: {cat_data['Average_Engagement'].min():.0f} - {cat_data['Average_Engagement'].max():.0f}")
        print(f"   • Tags: {', '.join(cat_data['Tag_id'].tolist())}")
    
    # Additional insights
    print(f"\nKey Insights:")
    
    # Most frequent tag
    top_freq_tag = df.loc[df['Frequency (%)'].idxmax()]
    print(f"   • Highest Frequency: {top_freq_tag['Tag_id']} ({top_freq_tag['Frequency (%)']:.2f}%)")
    
    # Most engaging tag
    top_engage_tag = df.loc[df['Average_Engagement'].idxmax()]
    print(f"   • Highest Engagement: {top_engage_tag['Tag_id']} ({top_engage_tag['Average_Engagement']:.0f} avg engagement)")
    
    # Category dominance
    category_totals = df.groupby('Category_id')['Frequency (%)'].sum().sort_values(ascending=False)
    print(f"   • Category by Total Frequency: {', '.join([f'{cat} ({freq:.1f}%)' for cat, freq in category_totals.items()])}")
    
    print("\n" + "="*80)

def main():
    """Main function"""
    print("=" * 80)
    print("Trump Policy Analysis - Strategic Signal Matrix Visualization")
    print("=" * 80)
    
    # Get script directory for consistent file paths
    script_dir = Path(__file__).parent.absolute()
    print("Script directory:", script_dir)
    print("Current working directory:", Path.cwd())
    
    # Save chart in script directory for consistent access
    output_file = script_dir / "strategic_signal_matrix_overall.png"
    
    print(f"Chart will be saved to: {output_file}")
    print("\nStarting strategic signal matrix processing...")
    
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
        category_names = {'A': 'Taming Bureaucracy', 'B': 'Culture Wars', 'C': 'Reshaping Power'}
        print(f"   Category {cat} ({category_names[cat]}): {len(tags_in_cat)} tags - {', '.join(tags_in_cat)}")
    
    # Create detailed analysis
    create_detailed_analysis(df)
    
    # Create strategic signal matrix
    print("\nGenerating strategic signal matrix...")
    fig, ax = create_strategic_signal_matrix(df, str(output_file))
    
    print(f"\nStrategic signal matrix visualization completed.")
    print(f"Chart saved: {output_file}")
    print(f"All {len(df)} active policy tags are displayed in the scatter plot")
    
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
