import math
import random
from typing import Dict


def expected_goals(team: Dict, opp: Dict, neutral=True):
    elo_attack = team['elo'] / 500.0
    form_boost = team.get('form_index', 0) * 0.28
    scoring = team.get('recent_goals_for_per_match', team.get('goals_for_per_match', 1.2)) * 0.60
    opp_def = opp.get('recent_goals_against_per_match', opp.get('goals_against_per_match', 1.0)) * 0.48
    opp_elo_drag = (1600 - opp['elo']) / 1000.0
    recent_ppm = team.get('recent_points_per_match', 1.2) * 0.10
    venue = 0.0 if neutral else 0.08
    lam = max(0.2, 0.55 + elo_attack + form_boost + scoring - opp_def + opp_elo_drag + recent_ppm + venue)
    return min(lam, 3.8)


def poisson_sample(lmbda: float) -> int:
    L = math.exp(-lmbda)
    k = 0
    p = 1.0
    while p > L:
        k += 1
        p *= random.random()
    return k - 1


def simulate_match(home: Dict, away: Dict, runs=20000):
    home_wins = 0
    away_wins = 0
    draws = 0
    score_counter = {}

    lam_home = expected_goals(home, away, neutral=True)
    lam_away = expected_goals(away, home, neutral=True)

    for _ in range(runs):
        hg = poisson_sample(lam_home)
        ag = poisson_sample(lam_away)
        key = f"{hg}-{ag}"
        score_counter[key] = score_counter.get(key, 0) + 1
        if hg > ag:
            home_wins += 1
        elif ag > hg:
            away_wins += 1
        else:
            draws += 1

    top_scores = sorted(score_counter.items(), key=lambda x: x[1], reverse=True)[:3]
    return {
        'home_win_prob': home_wins / runs,
        'draw_prob': draws / runs,
        'away_win_prob': away_wins / runs,
        'simulation_runs': runs,
        'top_scorelines': [
            {'score': s, 'probability': c / runs} for s, c in top_scores
        ],
        'expected_goals_home': lam_home,
        'expected_goals_away': lam_away,
    }
