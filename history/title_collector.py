import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
TMDB_API_KEY = os.getenv('TMDB_API_KEY')
IGDB_CLIENT_ID = os.getenv('IGDB_CLIENT_ID')
IGDB_CLIENT_SECRET = os.getenv('IGDB_CLIENT_SECRET')

def get_date_range():
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    tomorrow = today + timedelta(days=1)
    return yesterday.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d'), tomorrow.strftime('%Y-%m-%d')

def get_tmdb_releases(media_type):
    base_url = "https://api.themoviedb.org/3"
    yesterday, today, tomorrow = get_date_range()
    print(f"Fetching {media_type} releases from {yesterday} to {tomorrow}")

    if media_type == 'movie':
        url = f"{base_url}/discover/movie?api_key={TMDB_API_KEY}&primary_release_date.gte={yesterday}&primary_release_date.lte={tomorrow}"
    else:  # TV shows
        url = f"{base_url}/discover/tv?api_key={TMDB_API_KEY}&first_air_date.gte={yesterday}&first_air_date.lte={tomorrow}"

    response = requests.get(url)
    print(f"TMDB API Response for {media_type}: Status {response.status_code}")
    
    if response.status_code != 200:
        print(f"Error fetching {media_type}s: {response.status_code}")
        print(f"Response: {response.text}")
        return []
    
    results = response.json().get('results', [])
    print(f"Retrieved {len(results)} {media_type} releases")
    return [{'title': item['title' if media_type == 'movie' else 'name'],
             'type': media_type,
             'release_date': item['release_date' if media_type == 'movie' else 'first_air_date'],
             'id': item['id']} for item in results]

def get_igdb_releases():
    print("Fetching game releases")
    auth_url = f"https://id.twitch.tv/oauth2/token?client_id={IGDB_CLIENT_ID}&client_secret={IGDB_CLIENT_SECRET}&grant_type=client_credentials"
    auth_response = requests.post(auth_url)
    print(f"IGDB Auth Response: Status {auth_response.status_code}")
    if auth_response.status_code != 200:
        print(f"Error authenticating with IGDB: {auth_response.text}")
        return []
    access_token = auth_response.json()['access_token']

    headers = {
        'Client-ID': IGDB_CLIENT_ID,
        'Authorization': f'Bearer {access_token}'
    }

    today = datetime.now()
    unix_start = int((today - timedelta(days=1)).timestamp())
    unix_end = int((today + timedelta(days=1)).timestamp())

    data = f'fields name,release_dates.date; where release_dates.date >= {unix_start} & release_dates.date <= {unix_end}; sort release_dates.date asc;'

    response = requests.post('https://api.igdb.com/v4/games', headers=headers, data=data)
    print(f"IGDB API Response: Status {response.status_code}")
    if response.status_code != 200:
        print(f"Error fetching games: {response.text}")
        return []
    
    games = response.json()
    print(f"Retrieved {len(games)} game releases")
    return [{'title': game['name'],
             'type': 'game',
             'release_date': datetime.fromtimestamp(game['release_dates'][0]['date']).strftime('%Y-%m-%d'),
             'id': game['id']} for game in games]

def main():
    movies = get_tmdb_releases('movie')
    tv_shows = get_tmdb_releases('tv')
    games = get_igdb_releases()

    all_releases = movies + tv_shows + games
    print(f"\nTotal releases collected: {len(all_releases)}")
    print(f"Movies: {len(movies)}, TV Shows: {len(tv_shows)}, Games: {len(games)}")
    return all_releases

if __name__ == "__main__":
    releases = main()
    print("\nSample of collected releases:")
    for release in releases[:5]:  # Only print first 5 releases
        release_type = release.get('type', 'Unknown')
        title = release.get('title') or release.get('name', 'Untitled')
        date = release.get('release_date') or release.get('first_air_date', 'Unknown date')
        print(f"{release_type.capitalize()}: {title} - Release Date: {date}")
