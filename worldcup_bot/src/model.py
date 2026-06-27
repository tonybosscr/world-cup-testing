from typing import Dict, List

from model_selection import run_selected_model


def build_predictions(matches: List[Dict], strengths: Dict[str, Dict], config: Dict, selected_model_name: str = 'baseline_main'):
    runs = int(config['simulation'].get('runs', 20000))
    confidence_threshold = float(config['simulation'].get('confidence_threshold', 0.55))
    output = []

    for match in matches:
        home_name = match['home_team']
        away_name = match['away_team']
        home = strengths.get(home_name, {
            'elo': 1500,
            'form_index': 0,
            'goals_for_per_match': 1.2,
            'goals_against_per_match': 1.0,
            'recent_goals_for_per_match': 1.2,
            'recent_goals_against_per_match': 1.0,
            'recent_points_per_match': 1.2,
        })
        away = strengths.get(away_name, {
            'elo': 1500,
            'form_index': 0,
            'goals_for_per_match': 1.2,
            'goals_against_per_match': 1.0,
            'recent_goals_for_per_match': 1.2,
            'recent_goals_against_per_match': 1.0,
            'recent_points_per_match': 1.2,
        })
        sim = run_selected_model(selected_model_name, home, away, runs=runs)

        probs = {
            home_name: sim['home_win_prob'],
            'Draw': sim['draw_prob'],
            away_name: sim['away_win_prob'],
        }
        predicted_outcome = max(probs, key=probs.get)
        confidence = probs[predicted_outcome]
        notes = f"Selected model: {selected_model_name}. Informational probabilities, not guarantees."
        if confidence < confidence_threshold:
            notes += ' Tight matchup.'

        output.append({
            'match_id': match['match_id'],
            'home_team': home_name,
            'away_team': away_name,
            'kickoff_utc': match['kickoff_utc'],
            'status': match.get('status', 'scheduled'),
            'venue': match.get('venue', ''),
            'stage': match.get('stage', ''),
            'group': match.get('group', ''),
            'timezone': config.get('timezone', 'Africa/Lagos'),
            'selected_model': selected_model_name,
            'home_win_prob': sim['home_win_prob'],
            'draw_prob': sim['draw_prob'],
            'away_win_prob': sim['away_win_prob'],
            'predicted_outcome': predicted_outcome,
            'confidence': confidence,
            'simulation_runs': sim['simulation_runs'],
            'top_scorelines': sim['top_scorelines'],
            'expected_goals_home': sim['expected_goals_home'],
            'expected_goals_away': sim['expected_goals_away'],
            'home_elo': home.get('elo', 1500),
            'away_elo': away.get('elo', 1500),
            'home_form_index': home.get('form_index', 0),
            'away_form_index': away.get('form_index', 0),
            'notes': notes,
        })

    output.sort(key=lambda x: x['kickoff_utc'])
    return output
