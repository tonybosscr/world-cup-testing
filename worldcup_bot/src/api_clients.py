import os
from typing import Dict, List, Optional
import requests


class FootballDataProvider:
    def get_matches(self) -> List[Dict]:
        raise NotImplementedError

    def get_team_strengths(self) -> Dict[str, Dict]:
        raise NotImplementedError


class WorldCup26FreeProvider(FootballDataProvider):
    BASE_URL = os.getenv('WORLDCUP26_API_BASE_URL', 'https://worldcup26.ir')

    def _get(self, path: str):
        url = f"{self.BASE_URL.rstrip('/')}/{path.lstrip('/')}"
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        return r.json()

    def get_matches(self) -> List[Dict]:
        data = self._get('/get/games')
        games = data if isinstance(data, list) else data.get('data', data.get('games', []))
        mapped = []
        for idx, game in enumerate(games):
            home = game.get('home_team') or game.get('team_home') or game.get('homeTeam') or {}
            away = game.get('away_team') or game.get('team_away') or game.get('awayTeam') or {}
            home_name = home.get('name') if isinstance(home, dict) else str(home)
            away_name = away.get('name') if isinstance(away, dict) else str(away)
            kickoff = game.get('utc_date') or game.get('date') or game.get('kickoff') or game.get('datetime')

            # best-effort score parsing
            home_score = None
            away_score = None
            score = game.get('score') or {}
            if isinstance(score, dict):
                home_score = score.get('home') if score.get('home') is not None else score.get('home_score')
                away_score = score.get('away') if score.get('away') is not None else score.get('away_score')
            if home_score is None:
                home_score = game.get('home_score')
            if away_score is None:
                away_score = game.get('away_score')

            mapped.append({
                'match_id': str(game.get('id', f'wc26-{idx+1}')),
                'home_team': home_name,
                'away_team': away_name,
                'kickoff_utc': kickoff,
                'status': game.get('status', 'scheduled'),
                'venue': game.get('stadium') or game.get('venue') or '',
                'stage': game.get('stage_name') or game.get('stage') or '',
                'group': game.get('group_label') or game.get('group') or '',
                'home_score': home_score,
                'away_score': away_score,
            })
        return [m for m in mapped if m['home_team'] and m['away_team'] and m['kickoff_utc']]

    def get_team_strengths(self) -> Dict[str, Dict]:
        teams_data = self._get('/get/teams')
        teams = teams_data if isinstance(teams_data, list) else teams_data.get('data', teams_data.get('teams', []))
        strengths = {}
        for team in teams:
            name = team.get('name') or team.get('team_name') or team.get('enName')
            if not name:
                continue
            strengths[name] = {
                'elo': float(team.get('elo', team.get('rating', 1500)) or 1500),
                'fifa_rank': float(team.get('fifa_rank', team.get('rank', 100)) or 100),
                'form_index': float(team.get('form_index', 0) or 0),
                'goals_for_per_match': float(team.get('gf_per_match', 1.2) or 1.2),
                'goals_against_per_match': float(team.get('ga_per_match', 1.0) or 1.0),
            }
        return strengths


class ApiFootballLikeProvider(FootballDataProvider):
    def __init__(self):
        self.base_url = os.getenv('FOOTBALL_API_BASE_URL', '').rstrip('/')
        self.api_key = os.getenv('FOOTBALL_API_KEY', '')
        self.host = os.getenv('FOOTBALL_API_HOST', '')
        if not self.base_url:
            raise ValueError('FOOTBALL_API_BASE_URL is required for ApiFootballLikeProvider')

    def _headers(self):
        headers = {}
        if self.api_key:
            headers['x-apisports-key'] = self.api_key
            headers['Authorization'] = self.api_key
        if self.host:
            headers['x-rapidapi-host'] = self.host
        return headers

    def _get(self, path: str, params: Optional[Dict] = None):
        url = f"{self.base_url}/{path.lstrip('/')}"
        r = requests.get(url, headers=self._headers(), params=params or {}, timeout=30)
        r.raise_for_status()
        return r.json()

    def get_matches(self) -> List[Dict]:
        data = self._get('/fixtures', params={'season': 2026, 'search': 'World Cup'})
        response = data.get('response', data.get('data', []))
        mapped = []
        for idx, item in enumerate(response):
            fixture = item.get('fixture', item)
            teams = item.get('teams', {})
            goals = item.get('goals', {})
            mapped.append({
                'match_id': str(fixture.get('id', f'fixture-{idx+1}')),
                'home_team': teams.get('home', {}).get('name'),
                'away_team': teams.get('away', {}).get('name'),
                'kickoff_utc': fixture.get('date'),
                'status': fixture.get('status', {}).get('short', 'NS'),
                'venue': (fixture.get('venue') or {}).get('name', ''),
                'stage': item.get('league', {}).get('round', ''),
                'group': '',
                'home_score': goals.get('home'),
                'away_score': goals.get('away'),
            })
        return [m for m in mapped if m['home_team'] and m['away_team'] and m['kickoff_utc']]

    def get_team_strengths(self) -> Dict[str, Dict]:
        return {}


def get_provider(name: str) -> FootballDataProvider:
    name = (name or 'worldcup26_free').strip().lower()
    if name == 'worldcup26_free':
        return WorldCup26FreeProvider()
    if name == 'api_football_like':
        return ApiFootballLikeProvider()
    raise ValueError(f'Unsupported provider: {name}')
