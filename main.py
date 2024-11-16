import os
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
from calculators.excitement_calculator import ExcitementScoreCalculator
from collectors.tmdb_collector import TMDBCollector
from collectors.igdb_collector import IGDBCollector

api_cache = {}

# Load environment variables and set up logging (as before)

def get_date_range(days_back=7, days_forward=7):
    end_date = datetime.now().date() + timedelta(days=days_forward)
    start_date = end_date - timedelta(days=days_back)
    return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')

def get_releases(start_date, end_date):
    tmdb_collector = TMDBCollector(api_key=os.getenv('TMDB_API_KEY'))
    igdb_collector = IGDBCollector(client_id=os.getenv('IGDB_CLIENT_ID'), client_secret=os.getenv('IGDB_CLIENT_SECRET'))

    releases = []
    releases.extend(tmdb_collector.get_releases('movie', start_date, end_date, api_cache))
    releases.extend(tmdb_collector.get_releases('tv', start_date, end_date, api_cache))
    releases.extend(igdb_collector.get_releases(start_date, end_date, api_cache))
    return releases

def find_wake_up_babe_moment(releases, calculator, min_excitement=70, max_results=3):
    for release in releases:
        release['excitement_score'] = calculator.calculate_score(release)
    
    exciting_releases = [r for r in releases if r['excitement_score'] >= min_excitement]
    exciting_releases.sort(key=lambda x: x['excitement_score'], reverse=True)
    
    return exciting_releases[:max_results]

def main():
    logging.info("Starting Wake Up Babe application")

    tmdb_collector = TMDBCollector(api_key=os.getenv('TMDB_API_KEY'))
    igdb_collector = IGDBCollector(client_id=os.getenv('IGDB_CLIENT_ID'), client_secret=os.getenv('IGDB_CLIENT_SECRET'))
    calculator = ExcitementScoreCalculator()

    days_back = 7
    days_forward = 7
    min_excitement = 70
    max_attempts = 5

    for attempt in range(max_attempts):
        start_date, end_date = get_date_range(days_back, days_forward)
        releases = get_releases(start_date, end_date)
        
        wake_up_babe_moments = find_wake_up_babe_moment(releases, calculator, min_excitement)
        
        if wake_up_babe_moments:
            break
        
        days_back += 7
        days_forward += 7
        min_excitement -= 5

    if wake_up_babe_moments:
        print("\nWake Up Babe Moments:")
        for i, moment in enumerate(wake_up_babe_moments, 1):
            print(f"{i}. Wake Up Babe! {moment['title']} ({moment['type']}) is {'coming' if moment['release_date'] > datetime.now().strftime('%Y-%m-%d') else 'here'}!")
            print(f"   Release Date: {moment['release_date']}")
            print(f"   Excitement Score: {moment['excitement_score']:.2f}")
            print()
    else:
        print("No exciting releases found. Maybe it's time to create your own excitement!")

if __name__ == "__main__":
    main()
