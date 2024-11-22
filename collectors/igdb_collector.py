import os
import requests
import logging
import time
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class IGDBCollector:
    def __init__(self, start_date, end_date):
        self.client_id = os.getenv('IGDB_CLIENT_ID')
        self.client_secret = os.getenv('IGDB_CLIENT_SECRET')
        
        # Validate credentials
        if not self.client_id or not self.client_secret:
            raise ValueError("IGDB credentials not found in .env file")
            
        self.access_token = self.get_access_token()
        # Convert dates to Unix timestamps
        self.start_date = int(time.mktime(datetime.strptime(start_date, '%Y-%m-%d').timetuple()))
        self.end_date = int(time.mktime(datetime.strptime(end_date, '%Y-%m-%d').timetuple()))
        self.session = requests.Session()
        self.base_url = 'https://api.igdb.com/v4'
        self.headers = {
            'Client-ID': self.client_id,
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/json',
            'Content-Type': 'text/plain'  # IGDB expects text/plain for the query
        }

    def get_access_token(self):
        logging.info('Fetching IGDB access token')
        url = 'https://id.twitch.tv/oauth2/token'
        params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'client_credentials'
        }
        
        try:
            response = requests.post(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if 'access_token' not in data:
                logging.error(f"Unexpected API response: {data}")
                raise ValueError("Access token not found in API response")
                
            logging.info('Successfully obtained IGDB access token')
            return data['access_token']
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to get IGDB access token: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logging.error(f"API Response: {e.response.text}")
            raise

    def get_games(self):
        if not self.access_token:
            logging.error("No access token available")
            return []
            
        logging.info('Fetching games from IGDB')
        try:
            # First, get games directly with release date filter
            games_query = f"""
                fields 
                    name,
                    first_release_date,
                    rating,
                    total_rating,
                    platforms.name,
                    cover.url,
                    aggregated_rating,
                    follows;
                where first_release_date >= {self.start_date} 
                & first_release_date <= {self.end_date}
                & category = 0
                & version_parent = null;
                sort first_release_date asc;
                limit 500;
            """
            
            logging.debug(f"IGDB Query: {games_query}")  # Add debug logging
            
            games_response = self.session.post(
                f"{self.base_url}/games",
                headers=self.headers,
                data=games_query
            )
            games_response.raise_for_status()
            games_data = games_response.json()
            
            if not games_data:
                logging.info("No games found in the specified range")
                return []
            
            # Process games data
            games = []
            for item in games_data:
                # Get platform names instead of IDs
                platforms = []
                if 'platforms' in item:
                    platforms = [p.get('name', '') for p in item.get('platforms', [])]
                
                # Get cover URL if available
                cover_url = None
                if 'cover' in item and 'url' in item['cover']:
                    # Convert thumbnail to full-size image
                    cover_url = item['cover']['url'].replace('t_thumb', 't_cover_big')
                    if not cover_url.startswith('https:'):
                        cover_url = 'https:' + cover_url

                # Calculate a popularity score from available metrics
                popularity = (
                    (item.get('follows', 0) * 10) +  # Weight follows more heavily
                    (item.get('rating', 0) * 0.5) +  # Regular user rating
                    (item.get('aggregated_rating', 0) * 0.5)  # Critics rating
                )

                game = {
                    'title': item.get('name'),
                    'release_date': datetime.utcfromtimestamp(item.get('first_release_date')).strftime('%Y-%m-%d') if item.get('first_release_date') else None,
                    'popularity': popularity,  # Our calculated popularity
                    'rating': item.get('rating', 0),
                    'total_rating': item.get('total_rating', 0),
                    'platforms': platforms,
                    'cover_url': cover_url,
                    'type': 'game'
                }
                
                if game['release_date']:  # Only add games with valid release dates
                    games.append(game)
                        
            logging.info(f'Successfully fetched {len(games)} games')
            return games
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching games from IGDB: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logging.error(f"API Response: {e.response.text}")
            return []
