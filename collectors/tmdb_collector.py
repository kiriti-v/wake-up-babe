import requests
import logging

class TMDBCollector:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.themoviedb.org/3"

    def get_releases(self, media_type, start_date, end_date, cache):
        cache_key = f'tmdb_{media_type}_{start_date}_{end_date}'
        if cache and cache_key in cache:
            return cache[cache_key]

        logging.info(f"Fetching {media_type} releases from {start_date} to {end_date}")
        url = f"{self.base_url}/discover/{media_type}"
        params = {
            'api_key': self.api_key,
            'primary_release_date.gte': start_date,
            'primary_release_date.lte': end_date,
            'sort_by': 'popularity.desc'
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            results = data.get('results', [])
            releases = [self._format_release(item, media_type) for item in results]
            if cache is not None:
                cache[cache_key] = releases
            logging.info(f"Retrieved {len(results)} {media_type} releases")
            return releases
        except Exception as e:
            logging.error(f"Error fetching {media_type} releases: {e}")
            return []

    def _format_release(self, item, media_type):
        return {
            'title': item.get('title' if media_type == 'movie' else 'name'),
            'release_date': item.get('release_date' if media_type == 'movie' else 'first_air_date'),
            'type': media_type,
            'id': item.get('id'),
            'popularity': item.get('popularity', 0)
        }