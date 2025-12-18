#!/usr/bin/env python3
"""
Skill handler voor sliding window processing van gemaal data.
Dit script is onderdeel van de gemaal-data Claude skill.
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from fetch_hydronet_gemaal_data import HydronetGemaalDataFetcher, CHART_ID
from sliding_window_processor import MultiWindowProcessor


def process_from_api(gemaal_code, window_sizes):
    """Process data directly from API."""
    output_dir = Path(__file__).parent.parent / 'gemaal_data_cache'
    fetcher = HydronetGemaalDataFetcher(chart_id=CHART_ID, output_dir=output_dir)

    print(f"Ophalen van data voor gemaal: {gemaal_code}...", file=sys.stderr)
    data = fetcher.fetch_gemaal_data(gemaal_code)

    if not data or 'series' not in data or not data['series']:
        return None, "Geen data gevonden voor dit gemaal"

    series = data['series'][0]
    if not series['data']:
        return None, "Geen datapunten gevonden"

    return series['data'], None


def process_from_json(gemaal_code, json_path):
    """Process data from existing JSON file."""
    try:
        with open(json_path, 'r') as f:
            gemaal_data = json.load(f)

        if 'stations' not in gemaal_data or gemaal_code not in gemaal_data['stations']:
            return None, f"Gemaal {gemaal_code} niet gevonden in JSON"

        station = gemaal_data['stations'][gemaal_code]

        # Reconstruct data points from stored data
        # Note: We might not have full historical data in the JSON
        if 'debiet' in station and 'timestamp' in station:
            data_point = {
                'timestamp': station['timestamp'],
                'value': station['debiet'],
                'status': station['status']
            }
            return [data_point], None
        else:
            return None, "Onvoldoende data in JSON bestand"

    except FileNotFoundError:
        return None, f"JSON bestand niet gevonden: {json_path}"
    except json.JSONDecodeError:
        return None, "Ongeldig JSON formaat"


def main():
    """Main entry point voor de process-sliding-windows skill."""
    parser = argparse.ArgumentParser(
        description='Verwerk gemaal data met sliding window analyse'
    )
    parser.add_argument(
        '--gemaal-code',
        type=str,
        help='Code van het gemaal (vereist bij data-source=api)'
    )
    parser.add_argument(
        '--data-source',
        choices=['api', 'json'],
        default='api',
        help='Bron van data (default: api)'
    )
    parser.add_argument(
        '--json-path',
        type=str,
        default='simulatie-peilbeheer/public/data/gemaal_status_latest.json',
        help='Pad naar JSON bestand (voor data-source=json)'
    )
    parser.add_argument(
        '--window-sizes',
        type=str,
        default='30,60,180',
        help='Comma-separated window sizes in minuten (default: 30,60,180)'
    )
    parser.add_argument(
        '--output-format',
        choices=['json', 'pretty', 'trends-only'],
        default='pretty',
        help='Output format (default: pretty)'
    )

    args = parser.parse_args()

    # Parse window sizes
    try:
        window_sizes = [int(x.strip()) for x in args.window_sizes.split(',')]
    except ValueError:
        print(json.dumps({
            'success': False,
            'error': 'Ongeldige window-sizes format. Gebruik bijv: 30,60,180'
        }))
        sys.exit(1)

    # Validate gemaal_code for API source
    if args.data_source == 'api' and not args.gemaal_code:
        print(json.dumps({
            'success': False,
            'error': 'gemaal-code is vereist bij data-source=api'
        }))
        sys.exit(1)

    try:
        # Fetch data based on source
        if args.data_source == 'api':
            data_points, error = process_from_api(args.gemaal_code, window_sizes)
        else:
            data_points, error = process_from_json(args.gemaal_code, args.json_path)

        if error:
            print(json.dumps({
                'success': False,
                'error': error
            }))
            sys.exit(1)

        if not data_points:
            print(json.dumps({
                'success': False,
                'error': 'Geen data punten om te verwerken'
            }))
            sys.exit(1)

        # Initialize multi-window processor
        processor = MultiWindowProcessor(window_sizes)

        # Process all data points
        print(f"Verwerken van {len(data_points)} datapunten...", file=sys.stderr)
        for point in data_points:
            timestamp = datetime.fromisoformat(point['timestamp'].replace('Z', '+00:00'))
            processor.add_data_point(timestamp, point['value'])

        # Get metrics
        all_metrics = processor.get_all_metrics()
        summary = processor.get_summary()

        result = {
            'success': True,
            'gemaal_code': args.gemaal_code if args.gemaal_code else 'N/A',
            'data_source': args.data_source,
            'processed_points': len(data_points),
            'window_sizes': window_sizes,
            'metrics': all_metrics,
            'summary': summary
        }

        # Output based on format
        if args.output_format == 'json':
            print(json.dumps(result, indent=2))
        elif args.output_format == 'trends-only':
            trends = {
                window: metrics.get('trend', {})
                for window, metrics in all_metrics.items()
            }
            print(json.dumps({
                'gemaal': args.gemaal_code,
                'trends': trends,
                'overall': summary.get('overall_status', 'unknown')
            }, indent=2))
        else:  # pretty
            print(f"\n{'='*70}")
            print(f"SLIDING WINDOW ANALYSE: {args.gemaal_code if args.gemaal_code else 'N/A'}")
            print(f"{'='*70}\n")

            print(f"Data bron:        {args.data_source}")
            print(f"Verwerkte punten: {len(data_points)}")
            print(f"Window sizes:     {', '.join(map(str, window_sizes))} minuten\n")

            for window_minutes, metrics in all_metrics.items():
                print(f"\n{'-'*70}")
                print(f"WINDOW: {window_minutes} minuten")
                print(f"{'-'*70}")

                stats = metrics.get('stats', {})
                trend = metrics.get('trend', {})

                if stats:
                    print(f"\nStatistieken:")
                    print(f"  Punten:       {stats.get('count', 0)}")
                    print(f"  Min:          {stats.get('min', 0):.3f} m³/s")
                    print(f"  Max:          {stats.get('max', 0):.3f} m³/s")
                    print(f"  Gemiddeld:    {stats.get('avg', 0):.3f} m³/s")
                    print(f"  Totaal:       {stats.get('sum', 0):.3f} m³")

                if trend:
                    direction_emoji = {
                        'increasing': '↗',
                        'decreasing': '↘',
                        'stable': '→'
                    }
                    print(f"\nTrend:")
                    print(f"  Richting:     {direction_emoji.get(trend.get('direction', ''), '?')} {trend.get('direction', 'unknown').upper()}")
                    print(f"  Sterkte:      {trend.get('strength', 'unknown').upper()}")
                    print(f"  Slope/uur:    {trend.get('slope_per_hour', 0):.4f} m³/s")
                    print(f"  R²:           {trend.get('r_squared', 0):.3f}")
                    print(f"  Verandering:  {trend.get('change_percentage', 0):.1f}%")

            print(f"\n{'='*70}")
            print(f"OVERALL STATUS: {summary.get('overall_status', 'unknown').upper()}")
            print(f"{'='*70}\n")

            if 'short_term_trend' in summary:
                st = summary['short_term_trend']
                print(f"Short-term:  {st.get('direction', 'N/A')} ({st.get('strength', 'N/A')})")
            if 'medium_term_trend' in summary:
                mt = summary['medium_term_trend']
                print(f"Medium-term: {mt.get('direction', 'N/A')} ({mt.get('strength', 'N/A')})")
            if 'long_term_trend' in summary and summary['long_term_trend']:
                lt = summary['long_term_trend']
                print(f"Long-term:   {lt.get('direction', 'N/A')} ({lt.get('strength', 'N/A')})")

            print(f"\n{'='*70}\n")

        sys.exit(0)

    except Exception as e:
        import traceback
        error_result = {
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }
        print(json.dumps(error_result, indent=2), file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
