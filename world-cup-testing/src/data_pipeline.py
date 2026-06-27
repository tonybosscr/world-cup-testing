from pathlib import Path
import json
from typing import Dict, List, Tuple

from api_clients import get_provider
from form_ingestion import build_recent_results_from_matches, compute_attack_defense_from_recent_results
from ratings import merge_strengths, recent_form_from_results


def fetch_matches_and_strengths(config: Dict, data_dir: Path) -> Tuple[List[Dict], Dict[str, Dict], Dict[str, List[Dict]]]:
    provider_name = config.get('data_provider', {}).get('name', 'worldcup26_free')
    provider = get_provider(provider_name)
    matches = provider.get_matches()
    strengths = provider.get_team_strengths()

    recent_results = build_recent_results_from_matches(
        matches,
        lookback_days=int(config.get('form_ingestion', {}).get('lookback_days', 365)),
        max_matches=int(config.get('form_ingestion', {}).get('max_recent_matches', 8)),
    )
    recent_attack_defense = compute_attack_defense_from_recent_results(recent_results)

    merged_strengths = {}
    for team in set(list(strengths.keys()) + list(recent_results.keys())):
        base = strengths.get(team, {})
        base.update(recent_attack_defense.get(team, {}))
        base['form_index'] = recent_form_from_results(recent_results.get(team, []))
        merged_strengths[team] = merge_strengths(base)

    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / 'live_matches.json').write_text(json.dumps(matches, indent=2), encoding='utf-8')
    (data_dir / 'team_strengths.json').write_text(json.dumps(merged_strengths, indent=2), encoding='utf-8')
    (data_dir / 'recent_results.json').write_text(json.dumps(recent_results, indent=2), encoding='utf-8')
    return matches, merged_strengths, recent_results
