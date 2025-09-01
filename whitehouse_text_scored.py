import pandas as pd
import re

# Read the CSV file
df = pd.read_csv('Cleaned Data/whitehouse_original_text_cleaned.csv')
df['Content'] = df['Content'].astype(str)

# Customized keyword weight list
KEYWORDS_WEIGHTED = {
    'high': {
        'establish': 5, 'establishing': 5, 'establishment': 5, 'create': 5, 'creating': 5,
        'abolish': 5, 'abolishing': 5, 'terminate': 5, 'termination': 5, 'eliminate': 5,
        'rescind': 5, 'rescinding': 5, 'revoke': 5, 'revocation': 5, 'dissolve': 5, 'disband': 5,
        'consolidate': 5, 'consolidating': 5, 'consolidation': 5, 'merge': 5, 'merging': 5,
        'reorganize': 5, 'reorganization': 5, 'reconfigure': 5, 'reconfiguration': 5,
        'restructure': 5, 'restructuring': 5, 'disaggregate': 5, 'split': 5,
        'delegate authority': 5, 'transfer jurisdiction': 5, 'reallocate authority': 5
    },
    'medium': {
        'agency': 3, 'agencies': 3, 'department': 3, 'departments': 3, 'office': 3,
        'council': 3, 'commission': 3, 'board': 3, 'bureau': 3, 'administration': 3,
        'institute': 3, 'task force': 3, 'service': 3, 'component': 3, 'subcomponent': 3,
        'subdivision': 3, 'realign': 3, 'transfer': 3, 'reassign': 3, 'modify': 3,
        'revise': 3, 'amend': 3, 'streamline': 3, 'modernize': 3, 'reform': 3,
        'reduction in force': 3, 'rif': 3, 'attrition': 3, 'hiring freeze': 3,
        'workforce optimization': 3
    },
    'low': {
        'authority': 1, 'authorities': 1, 'responsibility': 1, 'responsibilities': 1,
        'function': 1, 'functions': 1, 'jurisdiction': 1, 'power': 1, 'process': 1,
        'procedure': 1, 'mechanism': 1, 'system': 1, 'framework': 1, 'architecture': 1,
        'personnel': 1, 'hiring': 1, 'appointment': 1, 'staffing': 1, 'performance': 1,
        'management': 1, 'oversight': 1, 'accountability': 1, 'procurement': 1,
        'contracting': 1, 'regulation': 1, 'guidance': 1, 'internal': 1, 'interagency': 1
    }
}

def calculate_score(text):
    score = 0
    text_lower = text.lower()
    found_words = set()  # Used for deduplication

    # Merge all keywords for one-time traversal
    all_keywords = {**KEYWORDS_WEIGHTED['high'], **KEYWORDS_WEIGHTED['medium'], **KEYWORDS_WEIGHTED['low']}

    # Sort by length in descending order to prioritize longer phrases (e.g., 'reduction in force' vs 'force')
    sorted_keywords = sorted(all_keywords.keys(), key=len, reverse=True)

    for keyword in sorted_keywords:
        # Use regex to ensure matching whole words/phrases
        if re.search(r'\b' + re.escape(keyword) + r'\b', text_lower):
            # Check if this word or its longer version has already been scored
            already_found = False
            for found in found_words:
                if keyword in found:
                    already_found = True
                    break
            if not already_found:
                score += all_keywords[keyword]
                found_words.add(keyword)
    
    return score

# Calculate score for each document
df['Reorg_Score'] = df['Content'].apply(calculate_score)

# Sort by score and filter those with score greater than 0
filtered_df = df[df['Reorg_Score'] > 0].sort_values(by='Reorg_Score', ascending=False)

# Display results
print("--- Initial Screening and Scoring Results (Top 20) ---")
print(filtered_df[['ID', 'Title', 'Reorg_Score']].head(20).to_string())

# Print column names for debugging
print("\nAvailable columns in the dataframe:")
print(df.columns.tolist())

# Check if 'Link' column exists instead of 'URL'
columns_to_save = ['ID', 'Title', 'Date', 'Category', 'Content', 'Reorg_Score']
if 'Link' in df.columns:
    columns_to_save.insert(4, 'Link')  # Add 'Link' before 'Content'
elif 'URL' in df.columns:
    columns_to_save.insert(4, 'URL')   # Add 'URL' before 'Content'

# Save only relevant columns to CSV for next step analysis
filtered_df_clean = filtered_df[columns_to_save]

# Fix ID and Title columns to ensure they are properly formatted
filtered_df_clean['ID'] = filtered_df_clean['ID'].astype(int)
filtered_df_clean['Title'] = filtered_df_clean['Title'].apply(lambda x: x.strip() if isinstance(x, str) else x)

# Save to CSV with proper encoding and formatting
filtered_df_clean.to_csv('whitehouse_text_scored.csv', index=False, encoding='utf-8')
print("\nScored candidate documents have been saved to 'whitehouse_text_scored.csv'")