import requests
import json
import os
import re
from datetime import datetime


#connect to the API
def connect_to_api(params):
    try:
        response = requests.get(params["url"], params=params["query"])
        response.raise_for_status()
        print("Successfully connected to the weather API.")
        return response.json()
    except requests.exceptions.RequestException as e:
        return None

#getting and validating input from the user
def get_city():
    while True:
        city = input("Enter city name or 'q' to exit: ").strip()
        if re.match(r"^[a-zA-ZÀ-ÿ' -]+$", city):
            return city
        else:
            print("Invalid input. Please enter a valid city name.")

#getting and validating the API key from the user
def get_api_key():
    while True:
        print("You need an API key to access the OpenWeatherMap API. You can get one by signing up at https://home.openweathermap.org/users/sign_up")
        api_key = input("Enter your OpenWeatherMap API key or 'q' to exit: ").strip()
        if api_key.lower() == "q":
            print("Goodbye!")
            exit()
        if re.match(r"^[a-f0-9]{32}$", api_key):
            return api_key
        else:
            print("Invalid API key. Please enter a valid 32-character API key.")

#finding the city and getting the current weather data
def get_data(api_key, city):
    url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "url": url,
        "query": {
            "q": city,
            "appid": api_key,
            "units": "metric"
        }
    }
    try:
        data = connect_to_api(params) 
        if data and data["cod"] == 200:
            city = data["name"]
            weather = data["weather"][0]["description"]
            temperature = data["main"]["temp"]
            print(f"City: {city}")
            print(f"Description: {weather}")
            print(f"Temperature: {temperature}°C")
            return data
        else:
            return None
    except Exception as e:
        print(f"Failed to get data. Error: {e}")
        return None
    
#getting the forecast data for the next 5 days
def get_forecast(api_key, city):
    url = "http://api.openweathermap.org/data/2.5/forecast"
    params = {
        "url": url,
        "query": {
            "q": city,
            "appid": api_key,
            "units": "metric"
        }
    }
    try:
        data = connect_to_api(params) 
        if not data: 
            print("Error: Unable to fetch data from the API. Please check your connection or city name.")
            return None
        if data["cod"] == "200":
            forecast_list = data["list"]
            daily_forecast = []
            for forecast in forecast_list:
                date = forecast.get("dt_txt", "N/A")
                temperature = forecast["main"].get("temp", "N/A")
                description = forecast["weather"][0].get("description", "N/A")

                daily_forecast.append({
                    "Timestamp": date,
                    "Temperature": temperature,
                    "Description": description,
                })
                print(f"Date: {date} - Temp.: {temperature}°C - Desc.: {description}")
            return daily_forecast
        else:
            print("Error:", data.get("message", "Unknown error in forecast data"))
            return None
    except Exception as e:
        print(f"Failed to get forecast data. Error: {e}")
        return None

#saving the forecast data to a .json file   
def save(daily_forecast):
    cur_dir  = os.path.dirname(os.path.abspath(__file__))
    stamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    file_name = f"weather_forecast_{stamp}.json"
    file_path = os.path.join(cur_dir, file_name)
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(daily_forecast, file, indent=4)
    print(f"Forecast data saved successfully to {file_path}.") 

#helper function to validate user input for Yes/No questions
def get_yes_no_input(prompt):
    while True:
        user_input = input(prompt).strip().lower()
        if user_input in ['yes', 'y']:
            return True
        elif user_input in ['no', 'n']:
            return False
        else:
            print("Invalid input. Please only choose between yes or no.")

#main logic of the program
def main():
    print("Welcome to the Weather API Scraper")
    api_key = get_api_key()
    while True:
        city = get_city()
        if city == "q":
            print("Goodbye!")
            break
        weather_data = get_data(api_key, city)
        if weather_data is None:
            print("Failed to get weather data. Please try again.")
            continue
        if weather_data:
            if get_yes_no_input("Do you want to see the 5 day forecast? Yes/No: "):
                forecast_data = get_forecast(api_key, city)
                if forecast_data:
                    if get_yes_no_input("Do you want to save the data to a .json file? Yes/No: "):
                        save(forecast_data)

if __name__ == "__main__":
    main()
