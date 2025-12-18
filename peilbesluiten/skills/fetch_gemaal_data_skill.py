#!/usr/bin/env python3
"""
Skill handler voor het ophalen van gemaal data van Hydronet API.
Dit script is onderdeel van de gemaal-data Claude skill.
"""

import sys
import json
import argparse
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from fetch_hydronet_gemaal_data import HydronetGemaalDataFetcher, CHART_ID


def main():
    """Main entry point voor de fetch-gemaal-data skill."""
    parser = argparse.ArgumentParser(
        description='Haal gemaal data op van Hydronet Water Control Room API'
    )
    parser.add_argument(
        'gemaal_code',
        type=str,
        help='Code van het gemaal (bijv. 176-036-00021)'
    )
    parser.add_argument(
        '--include-raw',
        action='store_true',
        help='Include raw API response in output'
    )
    parser.add_argument(
        '--output-format',
        choices=['json', 'pretty', 'summary'],
        default='pretty',
        help='Output format (default: pretty)'
    )

    args = parser.parse_args()

    try:
        # Initialize fetcher with chart_id and output directory
        output_dir = Path(__file__).parent.parent / 'gemaal_data_cache'
        fetcher = HydronetGemaalDataFetcher(chart_id=CHART_ID, output_dir=output_dir)

        # Fetch data
        print(f"Ophalen van data voor gemaal: {args.gemaal_code}...", file=sys.stderr)
        data = fetcher.fetch_gemaal_data(args.gemaal_code)

        if not data or 'series' not in data or not data['series']:
            print(json.dumps({
                'success': False,
                'error': 'Geen data gevonden voor dit gemaal',
                'gemaal_code': args.gemaal_code
            }))
            sys.exit(1)

        # Extract laatste datapunt
        series = data['series'][0]
        last_point = series['data'][-1] if series['data'] else None

        result = {
            'success': True,
            'gemaal_code': args.gemaal_code,
            'data': {
                'series_name': series['name'],
                'total_points': len(series['data']),
                'latest': last_point,
                'time_range': {
                    'start': series['data'][0]['timestamp'] if series['data'] else None,
                    'end': last_point['timestamp'] if last_point else None
                }
            }
        }

        # Add full series data
        if args.include_raw:
            result['raw_data'] = data

        # Output based on format
        if args.output_format == 'json':
            print(json.dumps(result, indent=2))
        elif args.output_format == 'summary':
            if last_point:
                summary = {
                    'gemaal': args.gemaal_code,
                    'status': last_point['status'],
                    'debiet': f"{last_point['value']:.3f} m³/s",
                    'timestamp': last_point['timestamp'],
                    'datapunten': len(series['data'])
                }
                print(json.dumps(summary, indent=2))
        else:  # pretty
            print(f"\n{'='*60}")
            print(f"GEMAAL DATA REPORT: {args.gemaal_code}")
            print(f"{'='*60}\n")

            if last_point:
                print(f"Status:           {last_point['status'].upper()}")
                print(f"Debiet:           {last_point['value']:.3f} m³/s")
                print(f"Timestamp:        {last_point['timestamp']}")
                print(f"Totaal punten:    {len(series['data'])}")

                if series['data']:
                    print(f"\nTijd range:")
                    print(f"  Start:  {series['data'][0]['timestamp']}")
                    print(f"  Eind:   {last_point['timestamp']}")

                # Statistics
                values = [p['value'] for p in series['data']]
                if values:
                    print(f"\nStatistieken:")
                    print(f"  Min:    {min(values):.3f} m³/s")
                    print(f"  Max:    {max(values):.3f} m³/s")
                    print(f"  Gem:    {sum(values)/len(values):.3f} m³/s")

            print(f"\n{'='*60}\n")

        sys.exit(0)

    except Exception as e:
        error_result = {
            'success': False,
            'error': str(e),
            'gemaal_code': args.gemaal_code
        }
        print(json.dumps(error_result, indent=2))
        sys.exit(1)


if __name__ == '__main__':
    main()
