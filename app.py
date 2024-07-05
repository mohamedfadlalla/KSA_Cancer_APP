import pandas as pd
import geopandas as gpd
import folium
from folium.features import GeoJsonTooltip
import streamlit as st
from streamlit_folium import folium_static

# Load the Excel file
file_path = 'Reqion_table.xlsx'
xls = pd.ExcelFile(file_path)

# Load the GeoPackage file
gpkg_path = 'saudi_arabia.gpkg'
gdf = gpd.read_file(gpkg_path, layer='regions')

# Manually map region names if necessary
region_mapping = {
    "Ar Riyad": "Riyadh",
    "Makkah": "Makkah",
    "Ash Sharqiyah": "Eastern",
    "Asir": "Asir",
    "Al Madinah": "Madinah",
    "Al Qasim": "Qassim",
    "Tabuk": "Tabuk",
    "Jazan": "Jazan",
    "Hail": "Hail",
    "Najran": "Najran",
    "Al Jawf": "Jouf",
    "Al Baha": "Baha",
    "Northern Borders": "Northern"
}

gdf['Region'] = gdf['NAME_1'].map(region_mapping)

# Function to create the map for a given year
def create_map(year):
    df = xls.parse(str(year))
    
    # Strip trailing spaces from column names
    df.columns = df.columns.str.strip()
    
    if 'Region' not in df.columns:
        st.error(f"'Region' column not found in the sheet for year {year}. Please ensure the sheet has a 'Region' column.")
        return None
    
    # Ensure region names are consistent
    df['Region'] = df['Region'].str.strip().map(lambda x: region_mapping.get(x, x))
    
    # Rename columns to avoid duplicates
    df = df.rename(columns=lambda x: x.strip() + f"_{year}" if x != 'Region' else x)

    # Merge the GeoDataFrame with the DataFrame
    merged_gdf = gdf.merge(df, how='left', on='Region')

    # Check for any unmatched regions
    unmatched = gdf[~gdf['Region'].isin(df['Region'])]
    if not unmatched.empty:
        st.warning(f"Unmatched regions in year {year}: {unmatched['Region'].tolist()}")

    # Fill missing values for visualization
    merged_gdf[f'Male_{year}'] = merged_gdf[f'Male_{year}'].fillna(0)
    merged_gdf[f'Female_{year}'] = merged_gdf[f'Female_{year}'].fillna(0)

    # Create a Folium map
    m = folium.Map(location=[23.8859, 45.0792], zoom_start=6)

    # Define the style and highlight functions
    def style_function(feature):
        return {
            'fillColor': '#ffaf00' if feature['properties'][f'Male_{year}'] > 0 else 'lightgrey',
            'color': 'black',
            'weight': 1,
            'fillOpacity': 0.6,
        }

    def highlight_function(feature):
        return {
            'fillColor': '#ffff00',
            'color': 'black',
            'weight': 3,
            'fillOpacity': 0.9,
        }

    # Add a GeoJson layer with tooltips and highlight functionality
    folium.GeoJson(
        merged_gdf,
        style_function=style_function,
        highlight_function=highlight_function,
        tooltip=GeoJsonTooltip(
            fields=['Region', f'Male_{year}', f'Female_{year}'],
            aliases=['Region', 'Male Cases', 'Female Cases'],
            localize=True
        )
    ).add_to(m)

    return m

# Streamlit app
st.title("Cancer Incidence Map in Saudi Arabia")

# Get available years from the Excel file
years = [int(sheet) for sheet in xls.sheet_names]

# Add a slider to select the year
year = st.slider("Select Year", min_value=min(years), max_value=max(years), step=1, value=min(years))

# Create the map for the selected year
map_ = create_map(year)
if map_:
    folium_static(map_)
