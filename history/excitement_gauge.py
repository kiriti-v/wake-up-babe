import os
from pytrends.request import TrendReq
import praw
from textblob import TextBlob
from dotenv import load_dotenv
from datetime import datetime, timedelta
from fuzzywuzzy import fuzz

# Load environment variables
load_dotenv()

REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT')

class GoogleTrendsAnalyzer:
    def __init__(self):
        self.pytrends = TrendReq(hl='en-US', tz=360)

    def get_trend_score(self, title):
        print(f"Analyzing Google Trends for: {title}")
        today = datetime.now()
        start_date = (today - timedelta(days=30)).strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
        
        self.pytrends.build_payload([title], timeframe=f'{start_date} {end_date}')
        interest_over_time = self.pytrends.interest_over_time()
        
        if interest_over_time.empty:
            print(f"No trend data found for: {title}")
            return 0
        
        trend_values = interest_over_time[title].values
        if len(trend_values) < 2:
            print(f"Insufficient trend data for: {title}")
            return 0
        
        initial_volume = trend_values[0]
        final_volume = trend_values[-1]
        trend_score = (final_volume - initial_volume) / initial_volume if initial_volume > 0 else 0
        
        normalized_score = max(0, min(100, trend_score * 100))
        print(f"Trend score for {title}: {normalized_score:.2f}")
        return normalized_score

class RedditSentimentAnalyzer:
    def __init__(self):
        self.reddit = praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            user_agent=REDDIT_USER_AGENT
        )

    def get_sentiment_score(self, title, media_type):
        print(f"Analyzing Reddit sentiment for: {title} ({media_type})")
        subreddits = {
            'movie': ['movies'],
            'tv': ['television'],
            'game': ['gaming', 'Games']
        }
        
        sentiment_scores = []
        engagement_scores = []

        for subreddit_name in subreddits.get(media_type, ['all']):
            print(f"Searching in subreddit: {subreddit_name}")
            subreddit = self.reddit.subreddit(subreddit_name)
            for submission in subreddit.search(title, limit=5, sort='hot', time_filter='month'):
                text = submission.title + ' ' + (submission.selftext or '')
                sentiment_scores.append(TextBlob(text).sentiment.polarity)
                
                engagement_score = (submission.score + submission.num_comments) / 100
                engagement_scores.append(min(engagement_score, 100))  # Cap at 100

                submission.comments.replace_more(limit=0)
                for comment in submission.comments.list()[:10]:
                    sentiment_scores.append(TextBlob(comment.body).sentiment.polarity)

        if not sentiment_scores:
            print(f"No Reddit data found for: {title}")
            return 0

        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
        avg_engagement = sum(engagement_scores) / len(engagement_scores) if engagement_scores else 0

        final_score = (avg_sentiment + 1) * 50 * 0.7 + avg_engagement * 0.3
        print(f"Reddit sentiment score for {title}: {final_score:.2f}")
        return final_score

class ExcitementGauge:
    def __init__(self):
        self.trends_analyzer = GoogleTrendsAnalyzer()
        self.sentiment_analyzer = RedditSentimentAnalyzer()

    def gauge_excitement(self, title, media_type):
        print(f"\nGauging excitement for: {title} ({media_type})")
        
        # Fuzzy match for Google Trends
        trend_score = max(self.trends_analyzer.get_trend_score(variant) 
                          for variant in self.generate_title_variants(title))
        
        # Fuzzy match for Reddit
        sentiment_score = max(self.sentiment_analyzer.get_sentiment_score(variant, media_type) 
                              for variant in self.generate_title_variants(title))
        
        excitement_score = 0.6 * trend_score + 0.4 * sentiment_score
        print(f"Final excitement score for {title}: {excitement_score:.2f}")
        return excitement_score

    def generate_title_variants(self, title):
        # Generate variations of the title
        words = title.split()
        variants = [title]
        if len(words) > 1:
            variants.append(' '.join(words[:-1]))  # Remove last word
            variants.append(' '.join(words[1:]))   # Remove first word
        return variants

def main(releases):
    excitement_gauge = ExcitementGauge()
    for release in releases:
        # Check if 'type' key exists, if not, try to infer from other keys
        if 'type' not in release:
            if 'title' in release:
                release['type'] = 'movie'
            elif 'name' in release:
                release['type'] = 'tv'
            else:
                print(f"Warning: Unable to determine type for release: {release}")
                continue  # Skip this release

        excitement_score = excitement_gauge.gauge_excitement(
            release.get('title') or release.get('name', 'Unknown Title'), 
            release['type']
        )
        release['excitement_score'] = excitement_score

    # Sort releases by excitement score
    releases.sort(key=lambda x: x['excitement_score'], reverse=True)
    return releases

if __name__ == "__main__":
    from title_collector import main as get_releases
    
    print("Fetching releases...")
    releases = get_releases()
    print(f"\nTotal releases fetched: {len(releases)}")
    
    for media_type in ['movie', 'tv', 'game']:
        type_count = sum(1 for release in releases if release['type'] == media_type)
        print(f"{media_type.capitalize()}s: {type_count}")
    
    print("\nAnalyzing excitement for releases...")
    # Select one item of each type for testing
    test_releases = []
    types_seen = set()
    for release in releases:
        if release['type'] not in types_seen and len(test_releases) < 3:  # Process up to 3 different types
            test_releases.append(release)
            types_seen.add(release['type'])
    
    excited_releases = main(test_releases)
    
    print("\nMost Exciting Releases:")
    for i, release in enumerate(excited_releases, 1):
        print(f"{i}. {release['type'].capitalize()}: {release['title']} - Release Date: {release['release_date']} - Excitement Score: {release['excitement_score']:.2f}")
