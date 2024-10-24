from flask import Flask, render_template, jsonify, make_response
import requests
import os
import csv
from io import StringIO
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

API_URL = 'https://api.electricitymap.org/v3/carbon-intensity/history?zone=GB'
API_TOKEN = os.getenv("ELECTRICITY_MAPS_API_TOKEN")


def get_carbon_intensity_data():
    """Function to fetch carbon intensity data from the API"""
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    response = requests.get(API_URL, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return data['history']  # Return full data from the API
    else:
        return None


def calculate_average_intensity(data):
    """Calculate average carbon intensity"""
    carbon_intensities = [entry['carbonIntensity'] for entry in data]
    if len(carbon_intensities) == 0:
        return None
    return sum(carbon_intensities) / len(carbon_intensities)


@app.route('/')
def index():
    data = get_carbon_intensity_data()
    if data is None:
        return "Failed to retrieve data", 500
    
    # Calculate average carbon intensity
    average_intensity = calculate_average_intensity(data)
    return render_template('index.html', carbon_intensity=average_intensity)


@app.route('/view_data')
def view_data():
    """Returns the raw carbon intensity data from the Electricity Maps API in JSON format."""
    data = get_carbon_intensity_data()
    if data is None:
        return jsonify({"error": "Failed to retrieve data"}), 500

    return jsonify(data)  # Return the raw data from the Electricity Maps API

@app.route('/download_csv')
def download_csv():
    """
    Generates and downloads a CSV file containing 
    the hourly carbon intensity values along with the average carbon intensity.
    """
    data = get_carbon_intensity_data()
    if data is None:
        return "Failed to retrieve data", 500
    
    # Create CSV in memory
    output = StringIO()
    writer = csv.writer(output)
    
    # Write the header
    writer.writerow(["Hour", "Carbon Intensity (gCO2eq/kWh)"])

    # Write the data rows (with datetime and carbon intensity)
    for entry in data:
        hour = datetime.strptime(entry['datetime'], "%Y-%m-%dT%H:%M:%S.%fZ")  # Convert datetime string to datetime object
        carbon_intensity = entry['carbonIntensity']
        writer.writerow([hour.strftime("%Y-%m-%d %H:%M:%S"), carbon_intensity])

    # Calculate and write the average carbon intensity
    average_intensity = calculate_average_intensity(data)
    writer.writerow(["Average", average_intensity])

    # Return CSV as a downloadable response
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=carbon_intensity.csv"
    response.headers["Content-type"] = "text/csv"
    return response

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
