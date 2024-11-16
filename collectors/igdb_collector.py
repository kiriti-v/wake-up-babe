import requests
from datetime import datetime
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler("app_debug.log"),
        logging.StreamHandler()
    ]
)

class IGDBCollector:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None

    def _get_access_token(self):
        url = "https://id.twitch.tv/oauth2/token"
        params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'client_credentials'
        }
        try:
            response = requests.post(url, params=params)
            response.raise_for_status()
            json_response = response.json()
            logging.debug(f"IGDB Access Token Response: {json_response}")
            self.access_token = json_response['access_token']
        except Exception as e:
            logging.error(f"Error getting IGDB access token: {e}")
            raise

    def _make_request(self, url, data):
        headers = {
            'Client-ID': self.client_id,
            'Authorization': f'Bearer {self.access_token}'
        }
        logging.debug(f"Making request to IGDB: URL={url}, Data={data}")
        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 401:
            logging.info("Access token expired, refreshing token...")
            self._get_access_token()
            headers['Authorization'] = f'Bearer {self.access_token}'
            response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        return response.json()

    def get_releases(self, start_date, end_date, cache):
        cache_key = f'igdb_{start_date}_{end_date}'
        if cache and cache_key in cache:
            return cache[cache_key]

        if not self.access_token:
            self._get_access_token()

        logging.info(f"Fetching game releases from {start_date} to {end_date}")
        unix_start = int(datetime.strptime(start_date, '%Y-%m-%d').timestamp())
        unix_end = int(datetime.strptime(end_date, '%Y-%m-%d').timestamp())

        release_dates_url = "https://api.igdb.com/v4/release_dates"
        release_dates_data = f'''
            fields game, date, platform;
            where date >= {unix_start} & date <= {unix_end};
            sort date asc;
        '''

        try:
            release_dates = self._make_request(release_dates_url, release_dates_data)
            logging.debug(f"IGDB Release Dates Response: {release_dates}")

            if not release_dates:
                logging.info("No game releases found in the given date range.")
                return []

            # Get unique game IDs to avoid duplicates
            unique_game_ids = list(set(rd['game'] for rd in release_dates))

            # Fetch game details
            games = self._get_games(unique_game_ids)

            # Map game IDs to game details
            games_dict = {game['id']: game for game in games}

            # Combine release dates and game details
            releases = []
            for rd in release_dates:
                game = games_dict.get(rd['game'])
                if game and game['id'] not in [r['id'] for r in releases]:  # Avoid duplicates by game ID
                    release = self._format_release(rd, game)
                    releases.append(release)
                else:
                    logging.warning(f"Game ID {rd['game']} not found in game data or duplicate.")
            
            if cache is not None:
                cache[cache_key] = releases
            logging.info(f"Retrieved {len(releases)} game releases")
            return releases
        except Exception as e:
            logging.error(f"Error fetching game releases: {e}")
            return []

    def _get_games(self, game_ids):
        games_url = "https://api.igdb.com/v4/games"
        # Combine game_ids into a single query
        game_ids_str = ','.join(map(str, game_ids))
        games_data = f'''
            fields id, name;
            where id = ({game_ids_str});
        '''
        try:
            game_response = self._make_request(games_url, games_data)
            logging.debug(f"IGDB Games Response for IDs {game_ids}: {game_response}")
            if game_response:
                return game_response  # Return all games in the response
        except Exception as e:
            logging.error(f"Error fetching game data for IDs {game_ids}: {e}")
        return []



    def _format_release(self, release_date_entry, game):
        return {
            'title': game.get('name'),
            'release_date': datetime.fromtimestamp(release_date_entry['date']).strftime('%Y-%m-%d'),
            'type': 'game',
            'id': game.get('id'),
        }
