#!/usr/bin/env python3
"""
Auto-refresh skill voor periodieke gemaal data updates.
Haalt elke 30 minuten (configureerbaar) nieuwe data op voor alle gemalen.
"""

import sys
import json
import time
import signal
import argparse
from pathlib import Path
from datetime import datetime
import subprocess

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Global flag voor graceful shutdown
shutdown_requested = False

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    global shutdown_requested
    print(f"\n[{datetime.now().isoformat()}] Shutdown signal ontvangen, stoppen na huidige cyclus...", file=sys.stderr)
    shutdown_requested = True

def run_data_refresh(python_cmd, script_path, output_path):
    """
    Voer een enkele data refresh cyclus uit.

    Returns:
        dict: Status informatie over de refresh
    """
    start_time = time.time()
    print(f"\n{'='*70}", file=sys.stderr)
    print(f"[{datetime.now().isoformat()}] Start data refresh cyclus...", file=sys.stderr)
    print(f"{'='*70}\n", file=sys.stderr)

    try:
        # Run generate_gemaal_status.py
        result = subprocess.run(
            [python_cmd, str(script_path)],
            cwd=script_path.parent,
            capture_output=True,
            text=True,
            timeout=600  # 10 minuten timeout
        )

        duration = time.time() - start_time

        if result.returncode == 0:
            # Check of output bestand is aangemaakt/geupdate
            if output_path.exists():
                file_time = datetime.fromtimestamp(output_path.stat().st_mtime)
                file_age = (datetime.now() - file_time).total_seconds()

                if file_age < 120:  # Bestand is binnen 2 minuten geupdate
                    status = {
                        'success': True,
                        'timestamp': datetime.now().isoformat(),
                        'duration_seconds': round(duration, 1),
                        'output_file': str(output_path),
                        'file_updated': file_time.isoformat()
                    }

                    print(f"\n✓ Data refresh succesvol in {duration:.1f} seconden", file=sys.stderr)
                    print(f"  Output: {output_path}", file=sys.stderr)
                    print(f"  Laatste update: {file_time.strftime('%Y-%m-%d %H:%M:%S')}", file=sys.stderr)

                    return status
                else:
                    return {
                        'success': False,
                        'error': f'Output bestand niet recent geupdate (ouder dan {file_age:.0f}s)',
                        'timestamp': datetime.now().isoformat(),
                        'duration_seconds': round(duration, 1)
                    }
            else:
                return {
                    'success': False,
                    'error': 'Output bestand niet gevonden',
                    'timestamp': datetime.now().isoformat(),
                    'duration_seconds': round(duration, 1)
                }
        else:
            error_msg = result.stderr[-500:] if result.stderr else 'Onbekende fout'
            print(f"\n✗ Data refresh gefaald: {error_msg}", file=sys.stderr)
            return {
                'success': False,
                'error': error_msg,
                'timestamp': datetime.now().isoformat(),
                'duration_seconds': round(duration, 1),
                'returncode': result.returncode
            }

    except subprocess.TimeoutExpired:
        duration = time.time() - start_time
        print(f"\n✗ Data refresh timeout na {duration:.1f} seconden", file=sys.stderr)
        return {
            'success': False,
            'error': 'Timeout na 10 minuten',
            'timestamp': datetime.now().isoformat(),
            'duration_seconds': round(duration, 1)
        }
    except Exception as e:
        duration = time.time() - start_time
        print(f"\n✗ Data refresh exception: {str(e)}", file=sys.stderr)
        return {
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat(),
            'duration_seconds': round(duration, 1)
        }


def main():
    """Main entry point voor auto-refresh skill."""
    parser = argparse.ArgumentParser(
        description='Automatische periodieke data refresh voor gemalen'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=30,
        help='Interval in minuten tussen refreshes (default: 30)'
    )
    parser.add_argument(
        '--max-cycles',
        type=int,
        default=0,
        help='Maximum aantal refresh cycli (0 = oneindig, default: 0)'
    )
    parser.add_argument(
        '--output-path',
        type=str,
        default='../simulatie-peilbeheer/public/data/gemaal_status_latest.json',
        help='Pad naar output JSON bestand'
    )
    parser.add_argument(
        '--log-file',
        type=str,
        help='Optioneel: schrijf logs naar bestand'
    )
    parser.add_argument(
        '--run-once',
        action='store_true',
        help='Voer slechts één refresh uit en stop'
    )

    args = parser.parse_args()

    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Paths
    script_path = Path(__file__).parent.parent / 'generate_gemaal_status.py'
    output_path = Path(__file__).parent.parent / args.output_path

    # Find Python command
    python_cmd = sys.executable

    # Validate script exists
    if not script_path.exists():
        print(json.dumps({
            'success': False,
            'error': f'Script niet gevonden: {script_path}'
        }))
        sys.exit(1)

    print(f"\n{'='*70}", file=sys.stderr)
    print(f"AUTO-REFRESH GEMAAL DATA", file=sys.stderr)
    print(f"{'='*70}", file=sys.stderr)
    print(f"Interval:      {args.interval} minuten", file=sys.stderr)
    print(f"Max cycles:    {'oneindig' if args.max_cycles == 0 else args.max_cycles}", file=sys.stderr)
    print(f"Output:        {output_path}", file=sys.stderr)
    print(f"Script:        {script_path}", file=sys.stderr)
    print(f"Python:        {python_cmd}", file=sys.stderr)
    if args.run_once:
        print(f"Mode:          Single run", file=sys.stderr)
    print(f"{'='*70}\n", file=sys.stderr)

    cycle_count = 0
    results_history = []

    try:
        while not shutdown_requested:
            cycle_count += 1

            # Run refresh
            result = run_data_refresh(python_cmd, script_path, output_path)
            results_history.append(result)

            # Output result
            print(json.dumps(result))
            sys.stdout.flush()

            # Check max cycles
            if args.max_cycles > 0 and cycle_count >= args.max_cycles:
                print(f"\n[{datetime.now().isoformat()}] Maximum aantal cycli ({args.max_cycles}) bereikt, stoppen...", file=sys.stderr)
                break

            # Run once mode
            if args.run_once:
                print(f"\n[{datetime.now().isoformat()}] Single run mode, stoppen...", file=sys.stderr)
                break

            # Wait for next cycle
            if not shutdown_requested:
                wait_seconds = args.interval * 60
                print(f"\n[{datetime.now().isoformat()}] Wachten {args.interval} minuten tot volgende refresh...", file=sys.stderr)
                print(f"  Volgende refresh: {datetime.fromtimestamp(time.time() + wait_seconds).strftime('%Y-%m-%d %H:%M:%S')}", file=sys.stderr)

                # Sleep in chunks to allow for graceful shutdown
                for i in range(wait_seconds):
                    if shutdown_requested:
                        break
                    time.sleep(1)

    except KeyboardInterrupt:
        print(f"\n[{datetime.now().isoformat()}] Keyboard interrupt, stoppen...", file=sys.stderr)

    finally:
        # Summary
        success_count = sum(1 for r in results_history if r.get('success'))
        print(f"\n{'='*70}", file=sys.stderr)
        print(f"AUTO-REFRESH SAMENVATTING", file=sys.stderr)
        print(f"{'='*70}", file=sys.stderr)
        print(f"Totaal cycli:        {cycle_count}", file=sys.stderr)
        print(f"Succesvol:           {success_count}", file=sys.stderr)
        print(f"Gefaald:             {cycle_count - success_count}", file=sys.stderr)
        if results_history:
            avg_duration = sum(r.get('duration_seconds', 0) for r in results_history) / len(results_history)
            print(f"Gem. duur:           {avg_duration:.1f} seconden", file=sys.stderr)
        print(f"{'='*70}\n", file=sys.stderr)

        # Exit code
        sys.exit(0 if success_count == cycle_count else 1)


if __name__ == '__main__':
    main()
