from typing import Dict, List

from model import simulate_match


def strength_defaults():
    return {
        'elo': 1500,
        'form_index': 0,
        'goals_for_per_match': 1.2,
        'goals_against_per_match': 1.0,
        'recent_goals_for_per_match': 1.2,
        'recent_goals_against_per_match': 1.0,
        'recent_points_per_match': 1.2,
    }


def simulate_match_elo_only(home: Dict, away: Dict, runs=12000):
    home2 = dict(strength_defaults(), **home)
    away2 = dict(strength_defaults(), **away)
    home2['form_index'] = 0
    away2['form_index'] = 0
    home2['recent_goals_for_per_match'] = home2['goals_for_per_match']
    away2['recent_goals_for_per_match'] = away2['goals_for_per_match']
    home2['recent_goals_against_per_match'] = home2['goals_against_per_match']
    away2['recent_goals_against_per_match'] = away2['goals_against_per_match']
    home2['recent_points_per_match'] = 1.2
    away2['recent_points_per_match'] = 1.2
    return simulate_match(home2, away2, runs=runs)


def simulate_match_form_weighted(home: Dict, away: Dict, runs=12000):
    home2 = dict(strength_defaults(), **home)
    away2 = dict(strength_defaults(), **away)
    home2['form_index'] = home2.get('form_index', 0) * 1.35
    away2['form_index'] = away2.get('form_index', 0) * 1.35
    home2['recent_points_per_match'] = home2.get('recent_points_per_match', 1.2) * 1.2
    away2['recent_points_per_match'] = away2.get('recent_points_per_match', 1.2) * 1.2
    return simulate_match(home2, away2, runs=runs)


def simulate_match_goal_rate_focused(home: Dict, away: Dict, runs=12000):
    home2 = dict(strength_defaults(), **home)
    away2 = dict(strength_defaults(), **away)
    home2['elo'] = (home2.get('elo', 1500) * 0.9)
    away2['elo'] = (away2.get('elo', 1500) * 0.9)
    home2['recent_goals_for_per_match'] = home2.get('recent_goals_for_per_match', 1.2) * 1.25
    away2['recent_goals_for_per_match'] = away2.get('recent_goals_for_per_match', 1.2) * 1.25
    home2['recent_goals_against_per_match'] = home2.get('recent_goals_against_per_match', 1.0) * 1.1
    away2['recent_goals_against_per_match'] = away2.get('recent_goals_against_per_match', 1.0) * 1.1
    return simulate_match(home2, away2, runs=runs)


def get_model_registry():
    return {
        'baseline_main': simulate_match,
        'elo_only': simulate_match_elo_only,
        'form_weighted': simulate_match_form_weighted,
        'goal_rate_focused': simulate_match_goal_rate_focused,
    }
