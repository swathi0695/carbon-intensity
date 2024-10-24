# Carbon Intensity in UK (Flask App)

This is a simple Python Flask web application that calculates the average carbon intensity of electricity consumed in the UK over the last 24 hours using the Electricity Maps API.

## Features

- Fetches carbon intensity data from the Electricity Maps API.
- Displays the average carbon intensity on a web page.
- Provides a RESTful API endpoint to return the carbon intensity in JSON format.
- Unit tests using `pytest`.

# Running the Flask App with Docker

## Prerequisites
- [Docker](https://www.docker.com/products/docker-desktop) installed on your system
- API token from [Electricity Maps](https://www.electricitymaps.com/free-tier-api)

## Steps to Run

1. Clone the repository:

    ```bash
    git clone https://github.com/swathi0695/carbon-intensity-app.git
    cd carbon-intensity-app
    ```

2. Create an `.env` file in the root of the project and add your API key:

    ```bash
    touch .env
    ```

    Add the following to `.env`:

    ```bash
    ELECTRICITY_MAPS_API_TOKEN=your_api_key_here
    ```

3. Build and run the Docker container using `docker-compose`:

    ```bash
    sudo docker-compose up --build
    ```

4. Open your browser and visit `http://localhost:5000` to access the Flask app.
    ## API Endpoints

- `http://localhost:5000/`: Displays the average carbon intensity on a webpage.
- `http://localhost:5000/view_data`: Returns the raw carbon intensity data from the Electricity Maps API in JSON format.
- `http://localhost:5000/download_csv`: Generates and downloads a CSV file containing the hourly carbon intensity values along with the average carbon intensity.


## Running Tests

To run the tests inside the Docker container (ensure the container is running):

```bash
sudo docker-compose exec flask-app pytest
```

## Shutting Down

To stop the application, run:

```bash
sudo docker-compose down
```
