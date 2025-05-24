import requests
import json

def fetch_api_data(url, params=None):
    """Fetch data from an API endpoint."""
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return f"Error fetching API data: {str(e)}"

def workflow_trigger(data, endpoint):
    """Trigger a workflow via an API endpoint."""
    try:
        response = requests.post(endpoint, json=data)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return f"Error triggering workflow: {str(e)}"

def example_weather_api(city):
    """Example: Fetch weather data for a city."""
    api_key = "your_api_key_here"  # Replace with your API key
    url = "http://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": api_key, "units": "metric"}
    return fetch_api_data(url, params)
