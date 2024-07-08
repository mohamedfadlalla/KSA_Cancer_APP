# KSA_Cancer_APP

KSA_Cancer_APP is a web application designed to visualize cancer statistics in Saudi Arabia. It provides interactive visualizations, including maps and charts, to help users understand regional cancer data.

## Features

- **Interactive Maps**: Visualize cancer statistics across different regions in Saudi Arabia.
- **Charts and Graphs**: Display various cancer-related metrics.
- **Data Filters**: Filter data by gender, type of cancer, and other parameters.

## Requirements

- Python 3.x
- Streamlit
- Pandas
- Geopandas
- Fulium

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/mohamedfadlalla/KSA_Cancer_APP.git
   cd KSA_Cancer_APP
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```

2. Access the application in your web browser at `http://localhost:8501`.

## Files

- `app.py`: Main application script.
- `requirements.txt`: List of required Python packages.
- `Cleaned_Master_table.xlsx`, `Cleaned_Region_table.csv`: Data files used for visualizations.
- `map_shp`: Directory containing shape files for map visualizations.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

## License

This project is licensed under the MIT License.
