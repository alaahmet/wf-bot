from flask import Flask
from threading import Thread
from discord.ext import tasks, commands
from itertools import cycle
import discord
import requests # Import the requests library
import os # Import the os library
from dotenv import load_dotenv # Import dotenv

load_dotenv() # Load environment variables from .env file

app = Flask('')


@app.route('/')
def main():
  return "Your Bot Is Ready"


def run():
  app.run(host="0.0.0.0", port=8000)


def keep_alive():
  server = Thread(target=run)
  server.start()

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

CITIES = [
    {"name": "Karlsruhe", "lat": 49.0069, "lon": 8.4037},
    {"name": "Zurich", "lat": 47.3769, "lon": 8.5417},
    {"name": "Istanbul", "lat": 41.0082, "lon": 28.9784}
]

city_cycle = cycle(CITIES)

async def get_weather(city):
    if WEATHER_API_KEY == "YOUR_API_KEY_HERE" or not WEATHER_API_KEY: # Check if None or placeholder
        return f"Weather for {city['name']} (API Key needed)"
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?lat={city['lat']}&lon={city['lon']}&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        weather_description = data['weather'][0]['description']
        temp = data['main']['temp']
        return f"{weather_description.split()[-1]}, {int(temp)}°C"
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather for {city['name']}: {e}")
        return f"Weather for {city['name']} (Error)"
    except KeyError:
        print(f"Unexpected API response for {city['name']}")
        return f"Weather for {city['name']} (API Error)"

TOKEN = os.getenv("TOKEN")
intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)


@tasks.loop(seconds=4)
async def change_status():
    current_city = next(city_cycle)
    weather_status = await get_weather(current_city)
    activity = discord.CustomActivity(name=f"{current_city['name']} | {weather_status}")
    await bot.change_presence(activity=activity)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    change_status.start()  # Start the weather status loop

if __name__ == '__main__':
  keep_alive()
  bot.run(TOKEN)
