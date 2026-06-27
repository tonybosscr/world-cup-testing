from typing import Dict, List


def normalize_rank_to_elo_like(fifa_rank: float) -> float:
    return 1750 - (fifa_rank * 4)


def recent_form_from_results(results: List[Dict]) -> float:
    if not results:
        return 0.0
    score = 0.0
    weight = 0.0
    for i, item in enumerate(results[:8]):
        w = max(0.4, 1 - i * 0.08)
        outcome = item.get('outcome')
        gd = float(item.get('goal_diff', 0))
        if outcome == 'W':
            score += (1.0 + 0.15 * gd) * w
        elif outcome == 'D':
            score += 0.25 * w
        else:
            score += (-0.75 + 0.05 * gd) * w
        weight += w
    return score / weight if weight else 0.0


def merge_strengths(base: Dict, fallback_elo: float = 1500.0) -> Dict:
    elo = float(base.get('elo', 0) or 0)
    fifa_rank = float(base.get('fifa_rank', 0) or 0)
    if not elo and fifa_rank:
        elo = normalize_rank_to_elo_like(fifa_rank)
    if not elo:
        elo = fallback_elo
    form_index = float(base.get('form_index', 0) or 0)
    gf = float(base.get('goals_for_per_match', 1.2) or 1.2)
    ga = float(base.get('goals_against_per_match', 1.0) or 1.0)
    recent_gf = float(base.get('recent_goals_for_per_match', gf) or gf)
    recent_ga = float(base.get('recent_goals_against_per_match', ga) or ga)
    recent_ppm = float(base.get('recent_points_per_match', 1.2) or 1.2)
    return {
        'elo': elo,
        'fifa_rank': fifa_rank or 100,
        'form_index': form_index,
        'goals_for_per_match': gf,
        'goals_against_per_match': ga,
        'recent_goals_for_per_match': recent_gf,
        'recent_goals_against_per_match': recent_ga,
        'recent_points_per_match': recent_ppm,
    }
