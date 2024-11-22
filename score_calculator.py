import datetime
import logging

class ScoreCalculator:
    def calculate_scores(self, releases):
        logging.info('Calculating excitement scores')
        today = datetime.datetime.now()
        scored_releases = []
        for release in releases:
            base_popularity_score = self._calculate_popularity_score(release)
            recency_factor = self._calculate_recency_factor(release['release_date'], today)
            type_weight = self._get_type_weight(release['type'])
            platform_bonus = self._get_platform_bonus(release)

            excitement_score = (base_popularity_score * recency_factor * type_weight) + platform_bonus
            release['excitement_score'] = round(excitement_score, 2)
            scored_releases.append(release)
        return scored_releases

    def _calculate_popularity_score(self, release):
        if release['type'] == 'game':
            # Games already have a normalized popularity score from the collector
            return release.get('popularity', 0)
        else:
            # Movies and TV shows
            popularity = release.get('popularity', 0)
            rating = release.get('rating', 0)
            total_rating = release.get('total_rating', 0)
            return (popularity * 0.6) + (rating * 0.2) + (total_rating * 0.2)

    def _calculate_recency_factor(self, release_date_str, today):
        release_date = datetime.datetime.strptime(release_date_str, '%Y-%m-%d')
        days_difference = abs((today - release_date).days)
        recency_factor = max(1 - (days_difference / 30), 0.1)  # Decay over a month
        return recency_factor

    def _get_type_weight(self, media_type):
        weights = {'movie': 1.2, 'tv': 1.1, 'game': 1.3}
        return weights.get(media_type, 1)

    def _get_platform_bonus(self, release):
        if release['type'] == 'game':
            unique_platforms = len(set(release.get('platforms', [])))
            return unique_platforms * 2  # Each unique platform adds a bonus
        return 0 