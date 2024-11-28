import requests
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)

def get_weather_forecast(city_name: str, days: int = 1) -> Optional[Dict]:
    """Get weather forecast for a given city."""
    if not city_name:
        logger.warning("No city name provided for weather forecast")
        return None

    logger.info(f"Getting weather forecast for city: {city_name}, days: {days}")
    
    try:
        # Your WeatherAPI key
        api_key = "5a57bb6ed806406083c120306242811"  
        base_url = "http://api.weatherapi.com/v1/forecast.json"
        
        params = {
            'key': api_key,
            'q': city_name,
            'days': days,
            'aqi': "no",
            'alerts': "no"
        }
        
        logger.info(f"Making API request to WeatherAPI with params: {params}")
        response = requests.get(base_url, params=params)
        logger.info(f"Weather API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"Weather API Response Data: {data}")
            
            # Extract relevant location data
            location = data["location"]["name"]
            region = data["location"]["region"]
            country = data["location"]["country"]
            
            logger.info(f"Successfully got weather data for: {location}, {region}, {country}")
            
            # Determine forecast range
            forecast_days = data["forecast"]["forecastday"]
            
            # Dynamic intro text
            intro_text = f"Here's the weather forecast for {location}, {region}, {country}"
            if days == 1:
                intro_text += " for today:"
            else:
                intro_text += f" for the next {days} days:"
            
            # Build the forecast summary
            forecast_summary = intro_text + "\n\n"
            
            for day in forecast_days:
                date = day["date"]
                condition = day["day"]["condition"]["text"]
                maxtemp = day["day"]["maxtemp_c"]
                mintemp = day["day"]["mintemp_c"]
                sunrise = day["astro"]["sunrise"]
                sunset = day["astro"]["sunset"]
                
                # Add details for each day
                forecast_summary += (
                    f"📅 Date: {date}\n"
                    f"🌡️ Temperature: {mintemp}°C to {maxtemp}°C\n"
                    f"🌤️ Conditions: {condition}\n"
                    f"🌅 Sunrise: {sunrise}\n"
                    f"🌇 Sunset: {sunset}\n\n"
                )
            
            logger.info(f"Generated forecast summary: {forecast_summary}")
            return forecast_summary
            
        else:
            logger.error(f"Weather API error: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {str(e)}")
        return None
    except KeyError as e:
        logger.error(f"Error parsing weather data: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error in get_weather_forecast: {str(e)}")
        return None

# # Example usage
# city = "Vadodara"
# forecast_days = 3  # Change to 1, 2, or 3 as needed
# weather_summary = get_weather_forecast(city, days=forecast_days)
# print(weather_summary)
