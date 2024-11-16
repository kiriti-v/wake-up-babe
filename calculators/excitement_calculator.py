import logging
from datetime import datetime, timedelta

class ExcitementScoreCalculator:
    def __init__(self):
        pass

    def calculate_score(self, release):
        base_popularity = min(release.get('popularity', 50), 100)  # Default 50 if no popularity
        release_date = datetime.strptime(release['release_date'], '%Y-%m-%d')
        days_until_release = (release_date - datetime.now()).days

        # Popularity score: Weight = 50%
        popularity_score = base_popularity * 0.5

        # Recency score: Weight = 30%
        # Higher excitement for upcoming releases, lower for distant past/future
        if days_until_release < 0:
            recency_score = max(0, 100 + days_until_release * 1)  # Past: score reduces by 1 point per day in the past
        else:
            recency_score = max(0, 100 - days_until_release * 2)  # Future: score reduces by 2 points per day into the future
        recency_score *= 0.3

        # media type score: Weight = 20%
        # a boost for games, less for TV/movies, cause poor games
        type_boost = 20 if release['type'] == 'game' else 10
        type_score = type_boost * 0.2

        # sum of the weighted components
        final_score = popularity_score + recency_score + type_score

        logging.info(f"Calculated excitement score for {release['title']}: {final_score:.2f}")
        return min(final_score, 100)  # Ensure the score does not exceed 100