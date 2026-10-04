import urllib.request
import json
import math
import sys

BASE_URL = 'http://localhost:8000'

def check_no_nan_inf(obj, path=''):
    if isinstance(obj, dict):
        for k, v in obj.items():
            check_no_nan_inf(v, f'{path}.{k}')
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            check_no_nan_inf(item, f'{path}[{i}]')
    elif isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            raise ValueError(f'Invalid float (NaN/inf) at {path}: {obj}')

def run_suite():
    print(f"Connecting to {BASE_URL}...")
    try:
        zones_res = urllib.request.urlopen(f'{BASE_URL}/zones')
        zones = json.loads(zones_res.read().decode())
        zone_ids = [z['id'] for z in zones]
        print(f"Discovered zones: {zone_ids}")
    except Exception as e:
        print(f"Failed to fetch zones: {e}")
        sys.exit(1)

    all_passed = True
    for zone in zone_ids:
        print(f"\n--- Testing Zone: {zone} ---")
        endpoints = [
            ('history', f'/zones/{zone}/history', 'GET', None),
            ('predict?days=7', f'/zones/{zone}/predict?days=7', 'GET', None),
            ('features', f'/zones/{zone}/features', 'GET', None),
            ('metrics', f'/zones/{zone}/metrics', 'GET', None),
            ('suggestion', f'/zones/{zone}/suggestion', 'GET', None),
            ('anomalies', f'/zones/{zone}/anomalies', 'GET', None),
            ('simulate', f'/zones/{zone}/simulate', 'POST', {'temperature': 29.5, 'day_of_week': 3, 'ac_penetration_pct': 60.0}),
            ('peak-load', f'/zones/{zone}/peak-load', 'GET', None),
            ('ac-insight', f'/zones/{zone}/ac-insight', 'GET', None),
        ]
        for name, ep, method, body in endpoints:
            req = urllib.request.Request(f'{BASE_URL}{ep}')
            if method == 'POST':
                req.add_header('Content-Type', 'application/json')
                data = json.dumps(body).encode('utf-8')
            else:
                data = None
            try:
                res = urllib.request.urlopen(req, data=data)
                raw = res.read().decode()
                parsed = json.loads(raw)
                check_no_nan_inf(parsed)
                print(f"  [OK 200] {name:16}")
            except Exception as e:
                print(f"  [FAIL]   {name:16} -> {e}")
                all_passed = False

    # Comparison endpoint
    print("\n--- Testing Comparison ---")
    try:
        res = urllib.request.urlopen(f'{BASE_URL}/zones/comparison')
        parsed = json.loads(res.read().decode())
        check_no_nan_inf(parsed)
        print(f"  [OK 200] comparison       ({len(parsed)} zones returned)")
    except Exception as e:
        print(f"  [FAIL]   comparison       -> {e}")
        all_passed = False

    if all_passed:
        print("\nSUCCESS: All endpoints for all zones returned HTTP 200 with zero NaN/inf values!")
    else:
        print("\nFAILURE: Some tests did not pass.")
        sys.exit(1)

if __name__ == '__main__':
    run_suite()
