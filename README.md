# Netflix Content Analysis Dashboard  
**Interactive Data Insights on Movies & TV Shows**

This project analyzes the **Netflix Titles** dataset using Python. It includes data cleaning, exploratory analysis, visualization, and a production-ready Streamlit dashboard — a complete end-to-end data project suitable for a portfolio or interview demo.


## Project Overview

The goal of this project is to explore the Netflix catalogue, uncover content trends, and present the findings through a clean, interactive web dashboard.  
The dashboard lets users filter content by **type, genre, country, and release year**, making exploration intuitive and actionable.


## Key Features

- **Interactive Dashboard**
  - Filters: content type, genre, country, release year range  
  - KPI metrics: Total Titles, Movies, TV Shows, Top Genre  
  - Interactive Plotly charts and responsive layout  
  - CSV export of filtered data

- **Visual Insights**
  - Top genres and countries visualizations  
  - Genre vs Type heatmap  
  - Duration comparison (movies vs TV shows)  
  - Distribution and trend analysis

- **Data Processing**
  - Cleaned and standardized fields: `date_added`, `duration`, `listed_in`, `country`  
  - Extracted fields: `primary_genre`, `primary_country`, `duration_num`  
  - Missing values handled and common parsing issues corrected  
  - Aggregated CSVs for faster dashboard loading


## Project Structure

Netflix_Analysis/
├── .gitignore
├── .venv/ # local virtualenv (ignored)
├── app # Streamlit app
├── README # project README (this file)
├── Local_Notes/ # local notes (ignored)
├── data/
│ ├── agg_by_country.xlsx
│ ├── agg_by_genre.xlsx
│ ├── agg_by_type.xlsx
│ ├── duration_stats.xlsx
│ ├── netflix_cleaned.xlsx
│ └── netflix_titles.xlsx # original/raw dataset (keep outside repo if large)
│
├── notebooks/
│ ├── 01_Load_and_Inspect.ipynb
│ ├── 02_Data_Cleansing.ipynb
│ ├── 03_Exploratory_Data_Analysis.ipynb
│ └── 04_Advance_Visuals.ipynb
│
├── visuals/
│ ├── country_vs_type_stacked.png
│ ├── duration_comparison_boxplot.png
│ ├── genre_vs_type_heatmap.png
│ ├── movie_duration_distribution.png
│ ├── movies_vs_tvshows.png
│ ├── netflix_banner_2.png
│ ├── rating_distribution.png
│ ├── top_countries.png
│ └── top_genres.png
└── .ipynb_checkpoints/ # jupyter autosaves (ignored)


## Tech Stack

- Python (Pandas, NumPy)  
- Plotly, Matplotlib, Seaborn (visualization)  
- Streamlit (dashboard)  
- Jupyter Notebooks (analysis & exploration)


## Author

Mohd Faizan Khan
Netflix Data Analysis Project - 2025
Built with Python, Data Engineering, and Interactive Visualization