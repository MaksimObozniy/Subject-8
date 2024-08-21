import os
import json
import folium
import requests
from flask import Flask
from geopy import distance
from dotenv import load_dotenv


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url,
                            params={
                                "geocode": address,
                                "apikey": apikey,
                                "format": "json",
                            })
    response.raise_for_status()
    found_places = response.json(
    )['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lat, lon


def get_name_distance(a):
    return a['distance']


def hello_world():
    with open('index.html') as file:
        return file.read()


def main():

    load_dotenv()
    api_key = os.getenv('API_KEY')
    
    with open("coffee.json", "r", encoding="CP1251") as my_file:
        file_contents = my_file.read()
        coffee_name = json.loads(file_contents)

    user_location = input("Где вы находитесь? ")
    coords = fetch_coordinates(api_key, user_location)

    coffee_dict = []

    for cofee in coffee_name:
        title = cofee['Name']
        latitude = cofee['geoData']['coordinates'][1]
        langtitude = cofee['geoData']['coordinates'][0]
        coordination_caffee = (latitude, langtitude)
        dist = distance.distance(coords, coordination_caffee).miles
        coffee_list = {
            'title': title,
            'distance': dist,
            'latitude': latitude,
            'longtitude': langtitude
        }
        coffee_dict.append(coffee_list)

    b = sorted(coffee_dict, key=get_name_distance)

    m = folium.Map(location=coords, zoom_start=12)

    for i in range(5):
        folium.Marker(
            location=[b[i]['latitude'], b[i]['longtitude']],
            tooltip="Click me!",
            popup=b[i]['title'],
            icon=folium.Icon(icon="cloud"),
        ).add_to(m)

    m.save("index.html")

    app = Flask(__name__)
    app.add_url_rule('/', 'hello', hello_world)
    app.run('0.0.0.0')

if __name__ == "__main__":
    main()
