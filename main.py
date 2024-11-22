import os
import datetime
from dotenv import load_dotenv
from collectors.tmdb_collector import TMDBCollector
from collectors.igdb_collector import IGDBCollector
from score_calculator import ScoreCalculator
import logging
from flask import Flask, render_template, request

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s:%(levelname)s:%(message)s',
    handlers=[
        logging.FileHandler('app_debug.log'),
        logging.StreamHandler()
    ]
)

app = Flask(__name__)

@app.route('/')
def home():
    try:
        # Input parameters from environment variables
        date_range_forward = int(os.getenv('DATE_RANGE_FORWARD', 7))
        date_range_backward = int(os.getenv('DATE_RANGE_BACKWARD', 7))
        score_threshold = int(os.getenv('SCORE_THRESHOLD', 70))
        
        # Calculate date range
        today = datetime.datetime.now()
        start_date = (today - datetime.timedelta(days=date_range_backward)).strftime('%Y-%m-%d')
        end_date = (today + datetime.timedelta(days=date_range_forward)).strftime('%Y-%m-%d')

        # Initialize collectors with date range
        tmdb = TMDBCollector(start_date, end_date)
        igdb = IGDBCollector(start_date, end_date)
        
        # Get releases
        movies = tmdb.get_movies()
        tv_shows = tmdb.get_tv_shows()
        games = igdb.get_games()
        
        # Combine all releases
        all_releases = movies + tv_shows + games
        
        # Deduplicate releases
        unique_releases = {(r['title'], r['release_date']): r for r in all_releases}.values()
        
        # Calculate excitement scores
        score_calculator = ScoreCalculator()
        scored_releases = score_calculator.calculate_scores(unique_releases)
        
        # Filter based on score threshold and sort
        wake_up_babes = [
            release for release in scored_releases 
            if release['excitement_score'] >= score_threshold
        ]
        wake_up_babes.sort(key=lambda x: x['excitement_score'], reverse=True)
        
        return render_template('index.html', releases=wake_up_babes)
        
    except Exception as e:
        logging.error(f"Error in home route: {str(e)}")
        return render_template('index.html', releases=[], error="An error occurred while fetching releases.")

def calculate_excitement_scores(releases):
    """
    Calculates the excitement scores for a list of releases.

    Args:
        releases (list): List of release dictionaries.

    Returns:
        list: List of releases with calculated excitement scores.
    """
    score_calculator = ScoreCalculator()
    # Assuming ScoreCalculator has a method `calculate_scores` that processes the releases
    scored_releases = score_calculator.calculate_scores(releases)
    return scored_releases

def main():
    try:
        # Input parameters
        date_range_forward = int(os.getenv('DATE_RANGE_FORWARD', 7))
        date_range_backward = int(os.getenv('DATE_RANGE_BACKWARD', 7))
        score_threshold = int(os.getenv('SCORE_THRESHOLD', 70))
        
        # Date calculations
        today = datetime.datetime.now()
        start_date = (today - datetime.timedelta(days=date_range_backward)).strftime('%Y-%m-%d')
        end_date = (today + datetime.timedelta(days=date_range_forward)).strftime('%Y-%m-%d')

        all_releases = []
        
        # Collect TMDB data
        try:
            tmdb_collector = TMDBCollector(start_date, end_date)
            movies = tmdb_collector.get_movies()
            tv_shows = tmdb_collector.get_tv_shows()
            all_releases.extend(movies + tv_shows)
        except Exception as e:
            logging.error(f"Error collecting TMDB data: {str(e)}")
        
        # Collect IGDB data
        try:
            igdb_collector = IGDBCollector(start_date, end_date)
            games = igdb_collector.get_games()
            all_releases.extend(games)
        except Exception as e:
            logging.error(f"Error collecting IGDB data: {str(e)}")
        
        if not all_releases:
            print("No releases found. Please check your API credentials and try again.")
            return
        
        # Deduplicate data
        unique_releases = { (r['title'], r['release_date']): r for r in all_releases }.values()
        
        # Calculate excitement scores
        score_calculator = ScoreCalculator()
        scored_releases = score_calculator.calculate_scores(unique_releases)
        
        # Filter based on score threshold
        wake_up_babe_moments = [release for release in scored_releases if release['excitement_score'] >= score_threshold]
        
        # Sort by excitement score
        wake_up_babe_moments.sort(key=lambda x: x['excitement_score'], reverse=True)
        
        if not wake_up_babe_moments:
            print("\nNo 'Wake Up Babe' moments found that meet the excitement threshold.")
            return
            
        # Output results
        print("\nTop 'Wake Up Babe' Moments:")
        for release in wake_up_babe_moments:
            print(f"\nTitle: {release['title']}")
            print(f"Type: {release['type'].capitalize()}")
            print(f"Release Date: {release['release_date']}")
            print(f"Excitement Score: {release['excitement_score']}")
            
            # Show additional details for games
            if release['type'] == 'game':
                if release.get('platforms'):
                    print(f"Platforms: {', '.join(release['platforms'])}")
                if release.get('cover_url'):
                    print(f"Cover: {release['cover_url']}")
            print("---")
            
    except Exception as e:
        logging.error(f"An unexpected error occurred: {str(e)}")
        print("An error occurred. Please check the logs for details.")

if __name__ == '__main__':
    app.run(debug=True)
