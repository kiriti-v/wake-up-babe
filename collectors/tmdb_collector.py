import os
import requests
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class TMDBCollector:
    def __init__(self, start_date, end_date):
        self.api_key = os.getenv('TMDB_API_KEY')
        self.start_date = start_date
        self.end_date = end_date
        self.base_url = 'https://api.themoviedb.org/3'
        self.session = requests.Session()
        self.session.params = {'api_key': self.api_key, 'language': 'en-US'}

    def get_movies(self):
        logging.info('Fetching movies from TMDB')
        url = f"{self.base_url}/discover/movie"
        params = {
            'primary_release_date.gte': self.start_date,
            'primary_release_date.lte': self.end_date,
            'sort_by': 'popularity.desc'
        }
        response = self.session.get(url, params=params)
        data = response.json()
        movies = []
        for item in data.get('results', []):
            movie = {
                'title': item['title'],
                'release_date': item['release_date'],
                'popularity': item['popularity'],
                'type': 'movie'
            }
            movies.append(movie)
        return movies

    def get_tv_shows(self):
        logging.info('Fetching TV shows from TMDB')
        url = f"{self.base_url}/discover/tv"
        params = {
            'first_air_date.gte': self.start_date,
            'first_air_date.lte': self.end_date,
            'sort_by': 'popularity.desc'
        }
        response = self.session.get(url, params=params)
        data = response.json()
        tv_shows = []
        for item in data.get('results', []):
            tv_show = {
                'title': item['name'],
                'release_date': item['first_air_date'],
                'popularity': item['popularity'],
                'type': 'tv'
            }
            tv_shows.append(tv_show)
        return tv_shows