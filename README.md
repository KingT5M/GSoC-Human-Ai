# Crisis Data Analysis Project

This project is designed to analyze crisis-related data, visualize trends, and generate insights. It processes data from various sources, performs risk analysis, and creates visualizations to aid in understanding crisis dynamics.

## Project Structure

credentials.env # Environment variables for accessing APIs or services
data_pipeline.py # Script for processing and cleaning data
geo_mapping.py # Script for geolocation mapping of crisis data
requirements.txt # Python dependencies for the project
risk_analysis.py # Script for analyzing crisis risk

## Setup Instructions

1. Clone the repository to your local machine.
2. Install the required dependencies using `pip`:
   pip install -r requirements.txt

## Usage

Data Processing
Run the data_pipeline.py script to process and clean the raw data:
python data_pipeline.py

Geolocation Mapping
Use the geo_mapping.py script to map crisis data to geographical locations:
python geo_mapping.py

Risk Analysis
Analyze crisis risks using the risk_analysis.py script:
python risk_analysis.py

## Visualizations

Generated visualizations include:
Bar Chart: bar_chart_risk_vs_sentiment.png
Heatmap: crisis_heatmap.html
heatmap_crisis_risk_vs_sentiment.png
Top Locations: top_5_crisis_locations.png

## Data Files

Input Data:
classified_posts.csv: Contains classified crisis-related posts.
crisis_posts_with_comments.csv: Includes posts and their associated comments.

Output Data:
geolocated_crisis_posts.csv: Processed data with geolocation information.

## Dependencies

The project requires the following Python libraries:Listed in requirements.txt.
Install them using:
pip install -r requirements.txt
