import pandas as pd
import geopandas as gpd
import folium
import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from folium.features import GeoJsonTooltip
import streamlit as st
from streamlit_folium import folium_static

# Load the CSV file
csv_file_path = 'Cleaned_Region_table.csv'
df = pd.read_csv(csv_file_path)

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
    year_df = df[df['Unnamed: 0'] == year].copy()
    
    # Strip trailing spaces from column names
    year_df.columns = year_df.columns.str.strip()
    
    if 'Region' not in year_df.columns:
        st.error(f"'Region' column not found in the sheet for year {year}. Please ensure the sheet has a 'Region' column.")
        return None
    
    # Ensure region names are consistent
    year_df['Region'] = year_df['Region'].str.strip().map(lambda x: region_mapping.get(x, x))
    
    # Rename columns to avoid duplicates, excluding 'Region'
    year_df = year_df.rename(columns={col: f"{col.strip()}_{year}" for col in year_df.columns if col != 'Region'})
    
    # Create a copy of the GeoDataFrame to avoid modifying the original
    merged_gdf = gdf.copy()
    
    # Merge the GeoDataFrame with the DataFrame
    merged_gdf = merged_gdf.merge(year_df, how='left', on='Region', suffixes=('', f'_{year}'))
    
    # Check for any unmatched regions
    unmatched = merged_gdf[merged_gdf[f'Male_{year}'].isna()]['Region']
    if not unmatched.empty:
        st.warning(f"Unmatched regions in year {year}: {unmatched.tolist()}")
    
    # Fill missing values for visualization
    merged_gdf[f'Male_{year}'] = merged_gdf[f'Male_{year}'].fillna(0)
    merged_gdf[f'Female_{year}'] = merged_gdf[f'Female_{year}'].fillna(0)
    
    # Create a Folium map
    m = folium.Map(location=[23.8859, 45.0792], zoom_start=6)
    
    # Define the style and highlight functions
    def style_function(feature):
        return {
            'fillColor': '#ffaf00' if feature['properties'].get(f'Male_{year}', 0) > 0 else 'lightgrey',
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
st.title("Cancer Statistics and Trends in Saudi Arabia")

st.markdown(
"""
Welcome to our website, showcasing cancer statistics in Saudi Arabia, based on data from the Saudi Health Council. Here, you'll find unique graphs that explore cancer cases by site, year, gender, and region. These visualizations reveal key trends and differences, offering valuable insights into cancer patterns over the past decade.
""")

# Create tabs
tab1, tab2 = st.tabs(["Map of Incidence", "Statistics"])

with tab1:
    st.write("Explore the cancer incidence across different regions of Saudi Arabia from 2012 to 2020. This interactive map provides a visual representation of cancer cases, allowing you to see how incidence rates vary by location and year.")
    # Your existing code for the Map of Incidence tab

    # Get available years from the CSV file
    years = df['Unnamed: 0'].unique()

    # Add a slider to select the year
    year = st.slider("Select Year", min_value=int(min(years)), max_value=int(max(years)), step=1, value=int(min(years)))

    # Create the map for the selected year
    map_ = create_map(year)
    if map_:
        folium_static(map_)

with tab2:
    st.write("Compare cancer incidence rates between males and females in Saudi Arabia. This section presents detailed statistics and graphs, highlighting gender-specific trends and differences in cancer cases over the years.")
    # Your existing code for the Statistics tab
    # Load the Excel file
    file_path = 'Cleaned_Master_table.xlsx'

    @st.cache_data
    def load_data(sheet_name):
        data = pd.read_excel(file_path, sheet_name=sheet_name)
        data.columns = data.columns.str.strip()
        return data

    def aggregate_data(data):
        aggregated_data = data.copy()
        years = range(2010, 2021)
        for year in years:
            saudi_col = f"{year}{data.columns[1][4:]}"
            nonsaudi_col = f"{year}{data.columns[2][4:]}"
            new_col = f"{year}total"
            aggregated_data[new_col] = aggregated_data[saudi_col] + aggregated_data[nonsaudi_col]
        return aggregated_data

    def create_heatmap(data, title):
        heatmap_data = data.drop(columns=['site'])
        plt.figure(figsize=(16, 10))
        sns.heatmap(heatmap_data, cmap='viridis', annot=True, fmt='d', xticklabels=heatmap_data.columns, yticklabels=data['site'], cbar_kws={'label': 'Count'})
        plt.title(f'{title} Cancer Statistics Heatmap', fontsize=16)
        plt.xlabel('Years and Categories', fontsize=14)
        plt.ylabel('Cancer Sites', fontsize=14)
        plt.xticks(rotation=45, ha='right', fontsize=12)
        plt.yticks(fontsize=12)
        plt.tight_layout()
        return plt

    def create_line_plot(data, gender):
        years = list(range(2010, 2021))
        total_cases = [data[f"{year}total"].sum() for year in years]
        plt.figure(figsize=(12, 6))
        plt.plot(years, total_cases, marker='o', label=f'{gender.capitalize()} Cases')
        plt.xlabel('Year')
        plt.ylabel('Total Cases')
        plt.title('Total Number of Cases Over the Years')
        plt.legend()
        plt.grid(True)
        plt.xticks(years, rotation=45)
        plt.tight_layout()
        return plt

    def create_box_plot(male_data, female_data, total_data):
        def transform_data(df, gender):
            year_columns = [col for col in df.columns if col.startswith('20') and col.endswith('total')]
            df_long = pd.melt(df, id_vars=['site'], value_vars=year_columns, var_name='Year', value_name='Cases')
            df_long['Year'] = df_long['Year'].str[:4]
            df_long['Gender'] = gender.capitalize()
            return df_long

        male_long = transform_data(male_data, 'male')
        female_long = transform_data(female_data, 'female')
        total_long = transform_data(total_data, 'total')

        combined_gender_data = pd.concat([male_long, female_long, total_long], ignore_index=True)

        top_sites = combined_gender_data.groupby('site')['Cases'].sum().nlargest(5).index
        top_sites_gender_data = combined_gender_data[combined_gender_data['site'].isin(top_sites)]

        plt.figure(figsize=(20, 12))
        sns.boxplot(data=top_sites_gender_data, x='site', y='Cases', hue='Gender', palette="Set1")
        plt.xticks(rotation=90)
        plt.title('Comparison of Cases per Site for Male, Female, and Total (Top 5 Cancer Sites)')
        plt.xlabel('Site')
        plt.ylabel('Number of Cases')
        plt.legend(title='Gender')
        plt.tight_layout()
        return plt


    # Load data
    male_data = load_data('Male')
    female_data = load_data('Female')
    total_data = load_data('Total')

    # Aggregate data
    male_data_aggregated = aggregate_data(male_data)
    female_data_aggregated = aggregate_data(female_data)
    total_data_aggregated = aggregate_data(total_data)

    # Dropdown menu for selecting data type
    data_type = st.selectbox('Select Data Type:', ['Total', 'Male', 'Female'])

    # Create and display visualizations based on selected data type
    if data_type == 'Total':
        st.subheader('Heatmap - Total')
        st.pyplot(create_heatmap(total_data_aggregated, 'Total'))
        
        st.subheader('Line Plot - Total')
        st.pyplot(create_line_plot(total_data_aggregated, 'total'))
    elif data_type == 'Male':
        st.subheader('Heatmap - Male')
        st.pyplot(create_heatmap(male_data_aggregated, 'Male'))
        
        st.subheader('Line Plot - Male')
        st.pyplot(create_line_plot(male_data_aggregated, 'male'))
    else:  # Female
        st.subheader('Heatmap - Female')
        st.pyplot(create_heatmap(female_data_aggregated, 'Female'))
        
        st.subheader('Line Plot - Female')
        st.pyplot(create_line_plot(female_data_aggregated, 'female'))

    # Box plot (always show all data)
    st.subheader('Box Plot - Comparison of Top 5 Cancer Sites')
    st.pyplot(create_box_plot(male_data_aggregated, female_data_aggregated, total_data_aggregated))



st.markdown(
    """
    <style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: white;
        color: black;
        text-align: center;
        padding: 10px;
        font-size: 14px;
    }
    </style>
    <div class="footer">
        <p>Created with Love ❤️ and passion 🔥 by <a href="https://www.linkedin.com/in/mohamedfadlalla-ai/" target="_blank">Mohamed Fadlalla</a></p>
    </div>
    """,
    unsafe_allow_html=True
)
