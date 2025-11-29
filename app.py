# Netflix Content Analysis Dashboard

import streamlit as st
import pandas as pd
from pathlib import Path
import plotly.express as px
import datetime

# ---------------------- Config ----------------------
st.set_page_config(page_title="Netflix Content Dashboard", layout="wide", initial_sidebar_state="expanded")

BASE = Path(__file__).parent
DATA_DIR = BASE / "data"
VIS_DIR = BASE / "visuals"

# Banner image
BANNER_PATH = "visuals/netflix_banner_2.png"

# ---------------------- Helpers & Caching ----------------------
@st.cache_data(show_spinner=False)
def load_cleaned_data(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    if 'duration_num' in df.columns:
        df['duration_num'] = pd.to_numeric(df['duration_num'], errors='coerce')
    if 'release_year' in df.columns:
        df['release_year'] = pd.to_numeric(df['release_year'], errors='coerce', downcast='integer')
    if 'year_added' in df.columns:
        df['year_added'] = pd.to_numeric(df['year_added'], errors='coerce', downcast='integer')
    return df

@st.cache_data(show_spinner=False)
def load_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)

# ---------------------- New helper: UI-only 1-based index ----------------------
def st_display_one_based(df: pd.DataFrame, height: int | None = None):
    display_df = df.copy()
    display_df.index = range(1, len(display_df) + 1)
    if height:
        st.dataframe(display_df, height=height)
    else:
        st.dataframe(display_df)

# ---------------------- Load Data ----------------------
df = load_cleaned_data(DATA_DIR / "netflix_cleaned.csv")

# Aggregates
agg_by_type = load_csv(DATA_DIR / "agg_by_type.csv") if (DATA_DIR / "agg_by_type.csv").exists() else df['type'].value_counts().reset_index().rename(columns={'index':'Type', 'type':'Count'})
agg_by_genre = load_csv(DATA_DIR / "agg_by_genre.csv") if (DATA_DIR / "agg_by_genre.csv").exists() else df.groupby(['primary_genre','type']).size().reset_index(name='Count')
agg_by_country = load_csv(DATA_DIR / "agg_by_country.csv") if (DATA_DIR / "agg_by_country.csv").exists() else df.groupby(['primary_country','type']).size().reset_index(name='Count')

# ---------------------- Sidebar ----------------------
st.sidebar.header("Filters")

type_options = sorted(df['type'].dropna().unique().tolist())
type_selected = st.sidebar.multiselect("Content Type", options=type_options, default=type_options)

genre_options = sorted(df['primary_genre'].dropna().unique().tolist())
genre_selected = st.sidebar.multiselect("Genres", options=genre_options)

country_options = sorted(df['primary_country'].dropna().unique().tolist())
country_selected = st.sidebar.multiselect("Countries", options=country_options)

current_year = datetime.datetime.now().year
release_years = df['release_year'].dropna()

min_year = int(release_years.min()) if not release_years.empty else 1900
max_year = int(release_years.max()) if not release_years.empty else current_year

year_range = st.sidebar.slider("Release Year Range", min_value=min_year, max_value=max_year, value=(min_year, max_year))

st.sidebar.markdown("---")
page = st.sidebar.selectbox("Page", ["Overview", "Genres", "Countries", "Raw Data"])

# ---------------------- Apply Filters ----------------------
filtered = df[df['type'].isin(type_selected)].copy()

if genre_selected:
    filtered = filtered[filtered['primary_genre'].isin(genre_selected)]

if country_selected:
    filtered = filtered[filtered['primary_country'].isin(country_selected)]

if 'release_year' in filtered.columns:
    filtered = filtered[(filtered['release_year'] >= year_range[0]) & (filtered['release_year'] <= year_range[1])]

# ---------------------- Header / Banner ----------------------
with st.container():
    try:
        st.image(BANNER_PATH, use_container_width=True)
    except Exception:
        st.title("Netflix Content Dashboard")

st.markdown("###### Built With Python • Streamlit • Pandas • Plotly")
st.divider()

# ---------------------- KPI Row ----------------------
total_titles = len(filtered)
total_movies = len(filtered[filtered['type'] == "Movie"])
total_tv = len(filtered[filtered['type'] == "TV Show"])

top_gen = filtered['primary_genre'].value_counts().idxmax() if not filtered['primary_genre'].dropna().empty else "Unknown"
top_country = filtered['primary_country'].value_counts().idxmax() if not filtered['primary_country'].dropna().empty else "Unknown"

k1, k2, k3, k4 = st.columns([1.3,1,1,1])
k1.metric("Total Titles", f"{total_titles:,}")
k2.metric("Movies", f"{total_movies:,}")
k3.metric("TV Shows", f"{total_tv:,}")
k4.metric("Top Genre", top_gen)
st.markdown("---")

# ---------------------- Page: Overview ----------------------
if page == "Overview":
    st.header("Overview")

    left, right = st.columns([2, 2])

    with left:
        st.subheader("Top Genres")
        top_gen_counts = filtered['primary_genre'].value_counts().nlargest(12).reset_index()
        top_gen_counts.columns = ['Genre','Count']
        
        if not top_gen_counts.empty:
            fig_gen = px.bar(top_gen_counts, x='Count', y='Genre', orientation='h',
                             title="Top Genres", text='Count', height=420)
            fig_gen.update_layout(yaxis={'categoryorder':'total ascending'}, margin=dict(l=10,r=10,t=40,b=10))
            st.plotly_chart(fig_gen, use_container_width=True)
        else:
            st.info("No Genre Data Available For Current Filters.")

    with right:
        st.subheader("Top Countries")
        top_country_counts = filtered['primary_country'].value_counts().nlargest(12).reset_index()
        top_country_counts.columns = ['Country','Count']

        if not top_country_counts.empty:
            fig_ctry = px.bar(top_country_counts, x='Count', y='Country', orientation='h',
                              title="Top Countries", text='Count', height=420)
            fig_ctry.update_layout(yaxis={'categoryorder':'total ascending'}, margin=dict(l=10,r=10,t=40,b=10))
            st.plotly_chart(fig_ctry, use_container_width=True)
        else:
            st.info("No Country Data Available For Current Filters.")

    st.markdown("---")

    s1, s2 = st.columns(2)
    with s1:
        st.subheader("Genre vs Type Heatmap (Static)")
        img = VIS_DIR / "genre_vs_type_heatmap.png"
        if img.exists():
            st.image(str(img), use_container_width=True)
        else:
            st.info("Heatmap Visual Not Found.")

    with s2:
        st.subheader("Duration Comparison (Boxplot - Static)")
        img2 = VIS_DIR / "duration_comparison_boxplot.png"
        if img2.exists():
            st.image(str(img2), use_container_width=True)
        else:
            st.info("Duration Boxplot Visual Not Found.")

    st.divider()
    st.write("Tip: Use the Sidebar Filters To Narrow Results.")

# ---------------------- Page: Genres ----------------------
elif page == "Genres":
    st.header("Genres")
    st.write("Top Genres Based On Current Filters")

    genre_table = filtered['primary_genre'].value_counts().reset_index()
    genre_table.columns = ['Genre', 'Count']

    st_display_one_based(genre_table)

    st.download_button("Download Genres (CSV)", data=genre_table.to_csv(index=False), file_name="genres_filtered.csv")

# ---------------------- Page: Countries ----------------------
elif page == "Countries":
    st.header("Countries")
    st.write("Top Countries Based On Current Filters")

    country_table = filtered['primary_country'].value_counts().reset_index()
    country_table.columns = ['Country', 'Count']

    st_display_one_based(country_table)

    st.download_button("Download Countries (CSV)", data=country_table.to_csv(index=False), file_name="countries_filtered.csv")

# ---------------------- Page: Raw Data ----------------------
else:
    st.header("Raw Data")
    st.write("Filtered Dataset Preview")

    st_display_one_based(filtered.head(200), height=600)

    csv = filtered.to_csv(index=False)
    st.download_button("Download Filtered CSV", data=csv, file_name="netflix_filtered.csv")

st.divider()
st.caption("Project By Mohd Faizan Khan — Netflix Data Analysis")
