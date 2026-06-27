from typing import Dict, List


def expected_outcome_probability(probs: Dict[str, float], actual: str) -> float:
    return float(probs.get(actual, 0.0) or 0.0)


def calibration_bins(records: List[Dict], bin_size: float = 0.1) -> List[Dict]:
    bins = []
    start = 0.0
    while start < 1.0:
        end = round(min(1.0, start + bin_size), 10)
        bins.append({'start': start, 'end': end, 'items': []})
        start = end

    for r in records:
        p = float(r.get('predicted_prob', 0) or 0)
        assigned = False
        for b in bins:
            if (p >= b['start'] and p < b['end']) or (b['end'] == 1.0 and p == 1.0):
                b['items'].append(r)
                assigned = True
                break
        if not assigned and bins:
            bins[-1]['items'].append(r)

    out = []
    for b in bins:
        items = b['items']
        if items:
            avg_pred = sum(float(i['predicted_prob']) for i in items) / len(items)
            avg_actual = sum(float(i['actual_hit']) for i in items) / len(items)
            out.append({
                'bin_start': b['start'],
                'bin_end': b['end'],
                'count': len(items),
                'avg_predicted': avg_pred,
                'actual_frequency': avg_actual,
                'gap': avg_pred - avg_actual,
            })
        else:
            out.append({
                'bin_start': b['start'],
                'bin_end': b['end'],
                'count': 0,
                'avg_predicted': None,
                'actual_frequency': None,
                'gap': None,
            })
    return out


def expected_calibration_error(bin_rows: List[Dict]) -> float:
    total = sum(int(b['count']) for b in bin_rows)
    if total == 0:
        return 0.0
    ece = 0.0
    for b in bin_rows:
        if not b['count'] or b['avg_predicted'] is None or b['actual_frequency'] is None:
            continue
        weight = b['count'] / total
        ece += weight * abs(float(b['avg_predicted']) - float(b['actual_frequency']))
    return ece
