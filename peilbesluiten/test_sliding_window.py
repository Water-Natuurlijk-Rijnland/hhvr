#!/usr/bin/env python3
"""
Test Script voor Sliding Window Processor
=========================================

Test de sliding window functionaliteit met voorbeeld data.
"""

from datetime import datetime, timedelta
from sliding_window_processor import SlidingWindowProcessor, MultiWindowProcessor, process_gemaal_series
import json

def test_basic_sliding_window():
    """Test basis sliding window functionaliteit"""
    print("=" * 70)
    print("Test 1: Basis Sliding Window")
    print("=" * 70)
    
    processor = SlidingWindowProcessor(window_minutes=30)
    
    # Simuleer data: stijgend debiet over 1 uur
    base_time = datetime.now() - timedelta(hours=1)
    for i in range(12):  # 12 punten, elke 5 minuten
        timestamp = base_time + timedelta(minutes=i * 5)
        value = 1.0 + (i * 0.1)  # Stijgend van 1.0 naar 2.1
        processor.add_data_point(timestamp, value)
    
    metrics = processor.get_all_metrics()
    print(f"Data punten in venster: {metrics['data_points_count']}")
    print(f"Min debiet: {metrics.get('min_debiet', 'N/A')}")
    print(f"Max debiet: {metrics.get('max_debiet', 'N/A')}")
    print(f"Gemiddeld debiet: {metrics.get('avg_debiet', 'N/A')}")
    
    trend = metrics.get('trend', {})
    if trend:
        print(f"\nTrend:")
        print(f"  Richting: {trend.get('direction', 'N/A')}")
        print(f"  Slope per uur: {trend.get('slope_per_hour', 'N/A')}")
        print(f"  Sterkte: {trend.get('strength', 'N/A')}")
        print(f"  R²: {trend.get('r_squared', 'N/A')}")
    
    change_pct = metrics.get('change_percentage')
    if change_pct is not None:
        print(f"  Verandering: {change_pct}%")
    
    print()


def test_multi_window():
    """Test multi-window processor"""
    print("=" * 70)
    print("Test 2: Multi-Window Processor")
    print("=" * 70)
    
    processor = MultiWindowProcessor(windows_minutes=[30, 60, 180])
    
    # Simuleer 3 uur aan data (elke 5 minuten)
    base_time = datetime.now() - timedelta(hours=3)
    for i in range(36):  # 36 punten over 3 uur
        timestamp = base_time + timedelta(minutes=i * 5)
        # Sinus patroon met stijgende trend
        value = 1.5 + (i * 0.02) + 0.3 * (i % 12) / 12
        processor.add_data_point(timestamp, value)
    
    all_metrics = processor.get_all_metrics()
    
    for window_key, metrics in all_metrics.items():
        print(f"\n{window_key} venster:")
        print(f"  Data punten: {metrics.get('data_points_count', 0)}")
        if metrics.get('trend'):
            trend = metrics['trend']
            print(f"  Trend: {trend['direction']} ({trend['strength']})")
            print(f"  Slope: {trend['slope_per_hour']} per uur")
        if metrics.get('stats'):
            stats = metrics['stats']
            print(f"  Gemiddeld: {stats['avg']:.3f}")
            print(f"  Min-Max: {stats['min']:.3f} - {stats['max']:.3f}")
    
    summary = processor.get_summary()
    print(f"\nSamenvatting:")
    print(f"  Overall status: {summary['overall_status']}")
    print()


def test_gemaal_series_processing():
    """Test verwerking van gemaal timeseries data"""
    print("=" * 70)
    print("Test 3: Gemaal Series Processing")
    print("=" * 70)
    
    # Simuleer gemaal series data (zoals van Hydronet API)
    base_time_ms = int((datetime.now() - timedelta(hours=2)).timestamp() * 1000)
    series_data = []
    
    for i in range(24):  # 24 punten, elke 5 minuten
        timestamp_ms = base_time_ms + (i * 5 * 60 * 1000)
        value = 2.0 + (i * 0.05) + (0.1 if i % 4 == 0 else 0)  # Stijgend met kleine variatie
        status = 'aan' if value > 0.001 else 'uit'
        
        series_data.append({
            'timestamp_ms': timestamp_ms,
            'timestamp': datetime.fromtimestamp(timestamp_ms / 1000).isoformat(),
            'value': value,
            'status': status
        })
    
    # Verwerk met sliding windows
    result = process_gemaal_series(
        gemaal_code="176-036-00021",
        series_data=series_data,
        windows_minutes=[30, 60, 180]
    )
    
    print(f"Gemaal: {result['gemaal_code']}")
    print(f"Huidige waarde: {result['current_value']} m³/s")
    print(f"\nSamenvatting trends:")
    summary = result['summary']
    print(f"  Overall status: {summary['overall_status']}")
    
    if summary['short_term_trend']:
        st = summary['short_term_trend']
        print(f"  Kort termijn (30 min): {st['direction']} ({st['strength']})")
    
    if summary['medium_term_trend']:
        mt = summary['medium_term_trend']
        print(f"  Medium termijn (3 uur): {mt['direction']} ({mt['strength']})")
    
    print(f"\nWindow statistieken:")
    for window_key in ['30_min', '60_min', '180_min']:
        if window_key in result['windows']:
            window = result['windows'][window_key]
            if window.get('stats'):
                stats = window['stats']
                print(f"  {window_key}:")
                print(f"    Punten: {stats['count']}")
                print(f"    Gemiddeld: {stats['avg']:.3f} m³/s")
                print(f"    Min-Max: {stats['min']:.3f} - {stats['max']:.3f} m³/s")
    
    # Export naar JSON voor inspectie
    output_file = "test_sliding_window_output.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, default=str)
    print(f"\nVolledige output opgeslagen in: {output_file}")
    print()


def test_edge_cases():
    """Test edge cases"""
    print("=" * 70)
    print("Test 4: Edge Cases")
    print("=" * 70)
    
    # Test met te weinig data
    processor = SlidingWindowProcessor(window_minutes=30)
    processor.add_data_point(datetime.now(), 1.5)
    
    metrics = processor.get_all_metrics()
    print(f"Met 1 datapunt:")
    print(f"  Heeft voldoende data: {metrics['has_sufficient_data']}")
    print(f"  Trend: {metrics.get('trend', 'Geen trend mogelijk')}")
    
    # Test met constante waarde
    processor2 = SlidingWindowProcessor(window_minutes=30)
    base_time = datetime.now() - timedelta(minutes=20)
    for i in range(5):
        processor2.add_data_point(base_time + timedelta(minutes=i * 5), 2.0)
    
    metrics2 = processor2.get_all_metrics()
    print(f"\nMet constante waarde (2.0):")
    if metrics2.get('trend'):
        trend = metrics2['trend']
        print(f"  Trend richting: {trend['direction']}")
        print(f"  Slope: {trend['slope_per_hour']}")
    
    print()


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("SLIDING WINDOW PROCESSOR TESTS")
    print("=" * 70 + "\n")
    
    test_basic_sliding_window()
    test_multi_window()
    test_gemaal_series_processing()
    test_edge_cases()
    
    print("=" * 70)
    print("Alle tests voltooid!")
    print("=" * 70)

