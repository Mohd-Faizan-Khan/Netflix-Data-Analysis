# Netflix Content Analysis Dashboard (Professional - Minimal & Interactive)

import streamlit as st
import pandas as pd
from pathlib import Path
import plotly.express as px

# ---------------------- Config ----------------------
st.set_page_config(page_title="Netflix Content Dashboard", layout="wide", initial_sidebar_state="expanded")

BASE = Path(__file__).parent
DATA_DIR = BASE / "data"
VIS_DIR = BASE / "visuals"

# Banner image you uploaded earlier (local path)
BANNER_PATH = "/mnt/data/057d91f9-1048-4463-b08e-20c4b0f6df12.png"

# ---------------------- Helpers & Caching ----------------------
@st.cache_data(show_spinner=False)
def load_cleaned_data(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    # Ensure expected columns exist and basic dtypes
    if 'duration_num' in df.columns:
        df['duration_num'] = pd.to_numeric(df['duration_num'], errors='coerce')
    if 'release_year' in df.columns:
        df['release_year'] = pd.to_numeric(df['release_year'], errors='coerce', downcast='integer')
    if 'year_added' in df.columns:
        df['year_added'] = pd.to_numeric(df['year_added'], errors='coerce', downcast='integer')
    return df

# Safe CSV loader for aggregated CSVs
@st.cache_data(show_spinner=False)
def load_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)

# ---------------------- Load Data ----------------------
df = load_cleaned_data(DATA_DIR / "netflix_cleaned.csv")

# Aggregates (used for default selections and some static KPIs)
agg_by_type = load_csv(DATA_DIR / "agg_by_type.csv") if (DATA_DIR / "agg_by_type.csv").exists() else df['type'].value_counts().reset_index().rename(columns={'index':'type', 'type':'count'})
agg_by_genre = load_csv(DATA_DIR / "agg_by_genre.csv") if (DATA_DIR / "agg_by_genre.csv").exists() else df.groupby(['primary_genre','type']).size().reset_index(name='count')
agg_by_country = load_csv(DATA_DIR / "agg_by_country.csv") if (DATA_DIR / "agg_by_country.csv").exists() else df.groupby(['primary_country','type']).size().reset_index(name='count')

# ---------------------- Sidebar (Filters & Page Select) ----------------------
st.sidebar.header("Filters")

# Type filter
type_options = sorted(df['type'].dropna().unique().tolist())
type_selected = st.sidebar.multiselect("Content type", options=type_options, default=type_options)

# Genre filter
genre_options = sorted(df['primary_genre'].dropna().unique().tolist())
genre_selected = st.sidebar.multiselect("Genres (multi)", options=genre_options, default=None)

# Country filter
country_options = sorted(df['primary_country'].dropna().unique().tolist())
country_selected = st.sidebar.multiselect("Countries (multi)", options=country_options, default=None)

# Year range filter (release year)
min_year = int(df['release_year'].dropna().min()) if not df['release_year'].dropna().empty else 1900
max_year = int(df['release_year'].dropna().max()) if not df['release_year'].dropna().empty else 2025
year_range = st.sidebar.slider("Release year range", min_value=min_year, max_value=max_year, value=(min_year, max_year))

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
        st.image(BANNER_PATH, use_column_width=True)
    except Exception:
        st.title("Netflix Content Dashboard")
st.markdown("###### Built with Python • Streamlit • Pandas • Plotly")
st.markdown("---")

# ---------------------- KPI Row ----------------------
total_titles = len(filtered)
total_movies = len(filtered[filtered['type'] == "Movie"])
total_tv = len(filtered[filtered['type'] == "TV Show"])

# Top items within filtered data (safe computations)
top_gen = filtered['primary_genre'].value_counts().idxmax() if not filtered['primary_genre'].dropna().empty else "Unknown"
top_country = filtered['primary_country'].value_counts().idxmax() if not filtered['primary_country'].dropna().empty else "Unknown"

k1, k2, k3, k4 = st.columns([1.3,1,1,1])
k1.metric("Total Titles (filtered)", f"{total_titles:,}")
k2.metric("Movies", f"{total_movies:,}")
k3.metric("TV Shows", f"{total_tv:,}")
k4.metric("Top Genre", top_gen)
st.markdown("---")

# ---------------------- Page: Overview ----------------------
if page == "Overview":
    st.header("Overview")

    # Two-column layout for interactive plots
    left, right = st.columns([2, 2])

    # Top Genres (interactive)
    with left:
        st.subheader("Top Genres (interactive)")
        top_gen_counts = filtered['primary_genre'].value_counts().nlargest(12).reset_index()
        top_gen_counts.columns = ['genre','count']
        if not top_gen_counts.empty:
            fig_gen = px.bar(top_gen_counts, x='count', y='genre', orientation='h',
                             title="Top Genres", text='count', height=420)
            fig_gen.update_layout(yaxis={'categoryorder':'total ascending'}, margin=dict(l=10,r=10,t=40,b=10))
            st.plotly_chart(fig_gen, use_container_width=True)
        else:
            st.info("No genre data available for current filters.")

    # Top Countries (interactive)
    with right:
        st.subheader("Top Countries (interactive)")
        top_country_counts = filtered['primary_country'].value_counts().nlargest(12).reset_index()
        top_country_counts.columns = ['country','count']
        if not top_country_counts.empty:
            fig_ctry = px.bar(top_country_counts, x='count', y='country', orientation='h',
                              title="Top Countries", text='count', height=420)
            fig_ctry.update_layout(yaxis={'categoryorder':'total ascending'}, margin=dict(l=10,r=10,t=40,b=10))
            st.plotly_chart(fig_ctry, use_container_width=True)
        else:
            st.info("No country data available for current filters.")

    st.markdown("---")

    # Row with static image heatmap + boxplot (keeps expensive plotting offline)
    s1, s2 = st.columns(2)
    with s1:
        st.subheader("Genre vs Type Heatmap (static)")
        img = VIS_DIR / "genre_vs_type_heatmap.png"
        if img.exists():
            st.image(str(img), use_column_width=True)
        else:
            st.info("genre_vs_type_heatmap.png missing in visuals/")

    with s2:
        st.subheader("Duration Comparison (Boxplot - static)")
        img2 = VIS_DIR / "duration_comparison_boxplot.png"
        if img2.exists():
            st.image(str(img2), use_column_width=True)
        else:
            st.info("duration_comparison_boxplot.png missing in visuals/")

    st.markdown("---")
    st.write("Tip: Use the sidebar filters to narrow the dataset; charts update automatically.")
    st.markdown("---")

# ---------------------- Page: Genres ----------------------
elif page == "Genres":
    st.header("Genres — deeper look")
    st.write("Interactive Top Genres with the current filters.")

    genre_table = filtered['primary_genre'].value_counts().reset_index()
    genre_table.columns = ['genre','count']
    st.dataframe(genre_table.head(200))

    st.download_button("Download genres (CSV)", data=genre_table.to_csv(index=False), file_name="genres_filtered.csv")

# ---------------------- Page: Countries ----------------------
elif page == "Countries":
    st.header("Countries — deeper look")
    country_table = filtered['primary_country'].value_counts().reset_index()
    country_table.columns = ['country','count']
    st.dataframe(country_table.head(200))
    st.download_button("Download countries (CSV)", data=country_table.to_csv(index=False), file_name="countries_filtered.csv")

# ---------------------- Page: Raw Data ----------------------
else:  # Raw Data
    st.header("Raw Data (filtered preview)")
    st.dataframe(filtered.head(200))
    csv = filtered.to_csv(index=False)
    st.download_button("Download filtered CSV", data=csv, file_name="netflix_filtered.csv")
    st.caption("You can apply sidebar filters and then download the filtered dataset.")

# ---------------------- Footer ----------------------
st.markdown("---")
st.caption("Project by Mohd Faizan Khan — Netflix Data Analysis (Day 1–7)")
