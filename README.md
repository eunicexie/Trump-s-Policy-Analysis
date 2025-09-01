# Trump Policy Analysis Project

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)

##  Project Overview

This is an academic research-based data collection and analysis platform designed to analyze how Donald Trump transforms government reorganization policies into strategic communication tools. The project implements the complete research methodology described in the thesis **"The Weaponization of Governance: Donald Trump's Dual-Track Strategy for Communicating Administrative Reform on Social Media"**.

###  Core Research Questions
This project explores how Trump, as a populist leader, constructs functional communication strategies to disseminate his ideologically-driven government reorganization policies across X and Truth Social platforms:

1. **Which specific policy issues constitute the core signals for public agenda-setting and political confrontation?**
2. **Do these platforms exhibit quantifiable, systematic differences in their communication patterns?**
3. **How do these core policy signals achieve their communicative functions through specific narrative frameworks and strategic framing?**

###  Key Findings
The research reveals a carefully designed "dual-track" communication system:
- **Truth Social** functions as an "ideological forge" for internal cultivation, using high-frequency culture-war narratives to solidify the base
- **X Platform** serves as a "public amphitheater" for external confrontation, employing low-frequency, high-impact signals to challenge institutions and disrupt public agenda

###  Research Scope
- **Time Frame**: January 20 - June 20, 2025 (first 5 months post-inauguration)
- **Policy Documents**: 298 White House official documents → 91 government reorganization policies → 24 ideologically-driven policies
- **Social Media**: 2,717 social media posts across 22 policy tags
- **Analysis Dimensions**: Signal Frequency × Signal Resonance strategic matrix analysis

##  Project Structure

```
Trump-s-Policy-Analysis/
├──  Core Scripts
│   ├── trump_x_content_scraper.py          # X/Twitter Content Scraper (API method)
│   ├── trump_x_content_selenium_scraper.py # X/Twitter Content Scraper (Selenium method)
│   ├── trump_truth_social_scraper.py       # Truth Social Content Scraper
│   ├── whitehouse_link_scraper.py          # White House Policy Link Scraper
│   ├── whitehouse_original_text_scraper.py # White House Policy Text Scraper
│   └── whitehouse_text_scored.py           # White House Document Policy Scoring
│
├──  Data Analysis
│   └── Engagement Calculate/
│       ├── Engagement_data_1_processor.py       # Engagement Data Processor
│       ├── Engagement_overall_processor.py      # Overall Engagement Analysis
│       ├── strategic_signal_matrix_overall.py   # Strategic Signal Matrix (Overall)
│       ├── strategic_signal_matrix_X.py         # Strategic Signal Matrix (X Platform)
│       ├── strategic_signal_matrix_truth_media.py # Strategic Signal Matrix (Truth Social)
│       └── policy_tags_frequency.py             # Policy Tag Frequency Analysis
│
├──  Data Files
│   ├── Cleaned Data/                       # Cleaned Datasets
│   ├── whitehouse_link.csv                # White House Policy Links
│   ├── whitehouse_original_text.csv       # White House Policy Original Text
│   ├── trump_x_content_raw.csv            # X Platform Raw Data
│   └── trump_truth_social_content_raw.csv # Truth Social Raw Data
│
├──  Configuration Files
│   ├── requirements.txt                   # Python Dependencies
│   ├── setup_dependencies.py             # Automated Setup Script
│   └── selenium_scraper_usage.md         # Selenium Usage Guide
│
└──  Documentation
    └── README.md                          # This File
```

##  Quick Start

### 1. Environment Setup

#### Automated Dependency Installation
```bash
python setup_dependencies.py
```

#### Manual Dependency Installation
```bash
pip install -r requirements.txt
```

#### Main Dependencies
- `pandas` - Data processing
- `numpy` - Numerical computation
- `matplotlib` - Plotting
- `seaborn` - Statistical visualization
- `selenium` - Web automation
- `beautifulsoup4` - HTML parsing
- `requests` - HTTP requests

### 2. ChromeDriver Setup (For Selenium Usage)

The project includes ChromeDriver, no additional download needed. For updates:
- macOS/Linux: Ensure `chromedriver` is executable
- Windows: Download the corresponding version of `chromedriver.exe`

##  Core Functional Modules

###  Social Media Data Collection

#### X (Twitter) Content Scraper
```bash
# Basic API scraper (Recommended)
python trump_x_content_scraper.py

# Selenium scraper (Get engagement data)
python trump_x_content_selenium_scraper.py

# Batch processing example
python trump_x_content_selenium_scraper.py trump_x_content_raw.csv -o output.csv --batch-size 20 --headless
```

**Output Data Fields:**
- `text` - Complete tweet content
- `author` - Author display name
- `date_published` - Publication timestamp
- `likes` - Number of likes
- `replies` - Number of replies
- `retweets` - Number of retweets
- `views` - Number of views

#### Truth Social Content Scraper
```bash
python trump_truth_social_scraper.py
```

###  White House Policy Document Analysis

#### Collect White House Policy Links
```bash
python whitehouse_link_scraper.py
```

#### Extract Policy Document Content
```bash
python whitehouse_original_text_scraper.py
```

#### Policy Reorganization Scoring
```bash
python whitehouse_text_scored.py
```

**Scoring Keyword Weights:**
- **High Weight** (5 points): establish, create, abolish, reorganize, merge, etc.
- **Medium Weight** (3 points): agency, department, transfer, reform, etc.
- **Low Weight** (1 point): authority, function, management, etc.

###  Data Analysis and Visualization

#### Engagement Data Processing
```bash
cd "Engagement Calculate"
python Engagement_data_1_processor.py
```

#### Strategic Signal Matrix Generation
```bash
# Overall analysis
python strategic_signal_matrix_overall.py

# X platform specific analysis
python strategic_signal_matrix_X.py

# Truth Social specific analysis
python strategic_signal_matrix_truth_media.py
```

#### Policy Tag Frequency Analysis
```bash
python policy_tags_frequency.py
```

##  Research Methodology & Data Analysis Pipeline

###  Theoretical Framework
This research adopts three core theoretical perspectives:
1. **Policy as Strategic Signaling** - Analyzing how agenda-setting is achieved through policy choices and priority setting
2. **Policy as Narrative Construction** - Using Narrative Policy Framework (NPF) to deconstruct story structures, character roles, and moral implications
3. **Policy as Framing Strategy** - Analyzing how strategic information selection, emphasis, and elaboration influence public understanding

###  Digital Humanities Methodology
Combining "Distant Reading" and "Close Reading" dual approaches:

#### Phase I: Distant Reading - From Raw Data to Core Communication Signals
**Four-Stage Exclusionary Funnel Model**
1. **Initial Policy Identification** (298 → 91 documents)
   - Weighted keyword filtering
   - LLM-assisted text classification (Google Gemini 1.5 Pro)
   - Manual expert verification

2. **Ideologically-Driven Policy Filtering** (91 → 24 documents)
   - Exclude foreign-facing policies
   - Exclude temporary agencies
   - Exclude routine technical reforms
   - Exclude industry-oriented economic interventions

3. **Policy Tag Coding** (24 → 22 tags)
   - Category A: Taming Bureaucracy (6 tags)
   - Category B: Culture Wars (8 tags)  
   - Category C: Reshaping Power Structures (8 tags)

#### Phase II: Close Reading - Deconstructing Narrative and Framing
**Qualitative Discourse Analysis**
- Using Narrative Policy Framework (NPF) to deconstruct story elements
- Applying framing theory to analyze rhetorical strategies
- Revealing deep ideological structures

###  Strategic Signal Matrix Analysis
**Dual-Dimension Measurement Framework**
- **Signal Frequency** - Quantifying communicator's strategic effort (Agenda-setting theory)
- **Signal Resonance** - Measuring audience impact (Average engagement: likes + replies + retweets)
- **Platform Differentiation** - Strategic deployment comparison between Truth Social vs X

###  Data Processing Workflow

#### Stage 1: Data Collection (2025.1.20-6.20)
1. **Policy Corpus**: Systematic collection of White House official documents
2. **Social Media Corpus**: Dual-platform data from X and Truth Social
3. **Engagement Data**: Selenium automation-enhanced collection

#### Stage 2: Computational-Assisted Filtering
1. **Weighted Keyword Scoring**: Government reorganization relevance scoring
2. **LLM Classification**: Intelligent classification based on CRS framework
3. **Expert Verification**: Manual quality control and accuracy assurance

#### Stage 3: Coding & Quantitative Analysis
1. **Content Analysis Coding**: 22-tag policy classification system
2. **Engagement Calculation**: Standardized cross-platform comparison metrics
3. **Strategic Matrix Construction**: Two-dimensional analysis of frequency × resonance

#### Stage 4: Qualitative Deep Reading
1. **Narrative Deconstruction**: Story analysis under NPF framework
2. **Frame Identification**: Revealing deep cognitive structures
3. **Strategic Function Explanation**: Communication effect mechanism analysis

##  Strategic Signal Matrix Explanation

The Strategic Signal Matrix categorizes policy tags into four functional quadrants, representing different strategic roles:

###  Quadrant Classification & Strategic Functions
- **Core Strategic Drivers** (High Frequency + High Engagement) - Primary strategic driving forces, such as A1 (Reinstate Schedule F) and A2 (Increase SES Accountability)
- **Confrontational Spearheads** (Low Frequency + High Engagement) - High-efficiency tactical weapons, such as C4 (Require Independent Agencies to Undergo OIRA Review) and C2 (Abolish More Agencies)
- **Narrative Cornerstones** (High Frequency + Low Engagement) - Sustained narrative construction, such as B1 (Abolish DEI, Woke, and Affirmative Action)
- **Marginal Signals** (Low Frequency + Low Engagement) - Secondary policy issues

###  Policy Classification System (22 Tags)

#### Category A: Taming Bureaucracy (Blue Dots)
- A1: Reinstate Schedule F - Core anti-"deep state" weapon
- A2: Increase SES Accountability - Primary tool for personnel purges
- A3-A6: Other federal personnel reform measures

#### Category B: Culture Wars (Red Squares)
- B1: Abolish DEI, Woke, and Affirmative Action - Ideological framework construction
- B2: Gender - Societal & Legal - Super-narrative with extremely high narrative flexibility
- B3: Gender - Child Medical - Emotional spearhead, moral shock tool
- B4-B8: Other cultural issues

#### Category C: Reshaping Power Structures (Green Triangles)
- C4: Require Independent Agencies to Undergo OIRA Review - Constitutional challenge based on "Unitary Executive Theory"
- C7: Rescind Unlawful Federal Regulations - Populist battering ram
- C1-C8: Other institutional reforms and power redistribution

###  Dual-Track Strategic Model
**Truth Social (Ideological Forge)**
- Function: Internal cultivation, base consolidation
- Dominant Category: Category B Culture Wars (51.1%)
- Key Signals: B2 (Gender issues) as narrative foundation, B1 (Anti-DEI) providing theoretical framework

**X Platform (Public Amphitheater)**
- Function: External confrontation, institutional challenge
- Dominant Category: Category C Power Reshaping (50%)
- Key Signals: Multi-front attack - Personnel (A2), Culture (B2), Procedures (C4, C7)

##  Common Usage Scenarios

### Batch Processing Tweet Data
```bash
# Process first 5 tweets for testing
python trump_x_content_selenium_scraper.py -o test_output.csv --batch-size 5 --wait-time 15

# Large batch processing
python trump_x_content_selenium_scraper.py -o complete_data.csv --batch-size 20 --headless
```

### Scheduled Data Updates
```bash
# Recommend setting up cron job or scheduled task
# Daily execution of data collection and analysis pipeline
```

### Custom Analysis Range
```python
# Modify date range (in corresponding scripts)
start_date = datetime(2025, 1, 20)
end_date = datetime(2025, 6, 20)
```

##  Output Files Description

### Raw Data Files
- `trump_x_content_raw.csv` - X platform raw tweets
- `trump_truth_social_content_raw.csv` - Truth Social raw posts
- `whitehouse_original_text.csv` - White House policy document original text

### Processed Data Files
- `Cleaned Data/` - Cleaned data files
- `whitehouse_text_scored.csv` - Scored White House documents
- `Engagement_data_processed.csv` - Processed engagement data

### Visualization Outputs
- `strategic_signal_matrix_overall.png` - Overall Strategic Signal Matrix
- `strategic_signal_matrix_X.png` - X Platform Strategic Signal Matrix
- `strategic_signal_matrix_truth_media.png` - Truth Social Strategic Signal Matrix
- `policy_tags_frequency_chart.png` - Policy Tag Frequency Chart

##  Usage Considerations

### Scraper Usage Limitations
1. **Request Frequency Control** - Scripts include built-in delay mechanisms to avoid overly frequent requests
2. **Anti-Detection Measures** - Multiple techniques used to avoid platform blocking
3. **Data Integrity** - Auto-save every 5 items to prevent data loss

### System Requirements
- **Python 3.7+**
- **Chrome Browser** (for Selenium usage)
- **Sufficient Storage Space** (Large datasets may require several GB)

### Error Handling
- Scripts include comprehensive error handling and retry mechanisms
- Partial results are automatically saved to avoid complete failure
- Detailed log output for problem diagnosis

##  Academic Contributions

### Theoretical Innovation
1. **Dual-Track Communication Model** - First to propose a systematic framework explaining modern populist digital communication strategies
2. **Methodological Breakthrough** - Combines distant/close reading digital humanities analysis, integrating quantitative and qualitative research
3. **Empirical Findings** - Large-scale analysis based on 2,700+ social media posts, revealing policy weaponization mechanisms

### Theoretical Foundations
- **Populist Communication Theory** (Mudde, 2004; Moffitt, 2016)
- **Narrative Policy Framework** (Jones & McBeth, 2010; Shanahan et al., 2013)
- **Framing Theory** (Entman, 1993; Lakoff, 2002)
- **Agenda-Setting Theory** (McCombs & Shaw, 1972)

##  Support and Contact

### Academic Usage
For academic research purposes, please:
1. Cite relevant papers
2. Review methodology documentation
3. Reference theoretical framework documentation

### Technical Support
For technical issues, please:
1. Open a GitHub Issue
2. Review existing documentation
3. Check script output error messages

##  Version Updates

### Latest Features (Based on Thesis Methodology Implementation)
-  Four-stage exclusionary funnel model (298→91→24→22 tags)
-  LLM-assisted policy classification (Google Gemini 1.5 Pro)
-  Dual-dimension strategic signal matrix (frequency × resonance)
-  Cross-platform differentiation analysis
-  NPF narrative framework deconstruction

### Research Extension Directions
-  Cross-national populism comparative studies
-  Other policy domain applications (economics, foreign policy, etc.)
-  Real-time monitoring and early warning systems
-  Deep learning sentiment analysis integration

### Methodological Improvements
-  Multi-coder reliability testing
-  Sentiment analysis-enhanced engagement measurement
-  More fine-grained platform ecosystem analysis

---

##  Citation

If you use this project in your research, please cite:

```bibtex
@mastersthesis{xie2025weaponization,
  title={The Weaponization of Governance: Donald Trump's Dual-Track Strategy for Communicating Administrative Reform on Social Media},
  author={Xie, Yuning},
  year={2025},
  school={University of Groningen},
  type={Master's thesis},
  program={MA Digital Humanities}
}
```

---

**Academic Statement**: This project is based on rigorous academic research methodology and is intended solely for academic research and policy analysis. All analysis results are based on publicly available data. Please comply with relevant platform terms of service and data usage policies. 
