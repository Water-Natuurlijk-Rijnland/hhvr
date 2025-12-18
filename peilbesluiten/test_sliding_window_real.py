#!/usr/bin/env python3
"""
Test Sliding Window Processor met Echte API Data
=================================================

Haalt echte gemaal data op van Hydronet API en test de sliding window processor.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from fetch_hydronet_gemaal_data import HydronetGemaalDataFetcher, CHART_ID
from sliding_window_processor import process_gemaal_series

# Test gemaal code
TEST_GEMAAL_CODE = "176-036-00021"  # Gemaal Zwetterpolder

def test_with_real_api():
    """Test sliding window processor met echte API data"""
    print("=" * 70)
    print("TEST SLIDING WINDOW MET ECHTE API DATA")
    print("=" * 70)
    print()
    
    # Initialize fetcher
    temp_dir = Path("temp_data")
    temp_dir.mkdir(exist_ok=True)
    fetcher = HydronetGemaalDataFetcher(CHART_ID, temp_dir)
    
    print(f"Ophalen data voor gemaal: {TEST_GEMAAL_CODE}")
    print("Dit kan even duren...")
    print()
    
    try:
        # Fetch data from API
        data = fetcher.fetch_gemaal_data(TEST_GEMAAL_CODE)
        
        if not data:
            print("❌ Geen data ontvangen van API")
            return False
        
        if 'series' not in data or len(data['series']) == 0:
            print("❌ Geen series data gevonden in API response")
            print(f"Data keys: {list(data.keys())}")
            return False
        
        series = data['series'][0]
        if 'data' not in series or len(series['data']) == 0:
            print("❌ Geen data punten gevonden in series")
            return False
        
        series_data = series['data']
        print(f"✅ {len(series_data)} datapunten ontvangen")
        print()
        
        # Toon eerste en laatste punten
        if len(series_data) > 0:
            first_point = series_data[0]
            last_point = series_data[-1]
            
            print("Eerste datapunt:")
            print(f"  Timestamp: {first_point.get('timestamp', 'N/A')}")
            print(f"  Waarde: {first_point.get('value', 'N/A')} m³/s")
            print(f"  Status: {first_point.get('status', 'N/A')}")
            print()
            
            print("Laatste datapunt:")
            print(f"  Timestamp: {last_point.get('timestamp', 'N/A')}")
            print(f"  Waarde: {last_point.get('value', 'N/A')} m³/s")
            print(f"  Status: {last_point.get('status', 'N/A')}")
            print()
        
        # Process met sliding windows
        print("=" * 70)
        print("SLIDING WINDOW PROCESSING")
        print("=" * 70)
        print()
        
        windowed_data = process_gemaal_series(
            TEST_GEMAAL_CODE,
            series_data,
            windows_minutes=[30, 60, 180]
        )
        
        # Toon resultaten
        print(f"Gemaal: {windowed_data['gemaal_code']}")
        print(f"Huidige waarde: {windowed_data['current_value']} m³/s")
        print(f"Verwerkt op: {windowed_data['processed_at']}")
        print()
        
        # Trends per venster
        print("TRENDS PER VENSTER:")
        print("-" * 70)
        
        for window_key in ['30_min', '60_min', '180_min']:
            window_data = windowed_data['windows'].get(window_key, {})
            
            if window_data.get('has_sufficient_data'):
                print(f"\n{window_key} venster:")
                
                # Stats
                if window_data.get('stats'):
                    stats = window_data['stats']
                    print(f"  Data punten: {stats['count']}")
                    print(f"  Venster duur: {stats['window_duration_minutes']:.1f} minuten")
                    print(f"  Min debiet: {stats['min']:.3f} m³/s")
                    print(f"  Max debiet: {stats['max']:.3f} m³/s")
                    print(f"  Gemiddeld debiet: {stats['avg']:.3f} m³/s")
                    print(f"  Totaal debiet: {stats['sum']:.3f} m³/s")
                
                # Trend
                if window_data.get('trend'):
                    trend = window_data['trend']
                    print(f"  Trend richting: {trend['direction']}")
                    print(f"  Trend sterkte: {trend['strength']}")
                    print(f"  Slope per uur: {trend['slope_per_hour']:.3f} m³/s/uur")
                    print(f"  R² (betrouwbaarheid): {trend['r_squared']:.3f}")
                
                # Change percentage
                if 'change_percentage' in window_data:
                    change = window_data['change_percentage']
                    print(f"  Verandering: {change:+.2f}%")
            else:
                print(f"\n{window_key} venster: Onvoldoende data ({window_data.get('data_points_count', 0)} punten)")
        
        # Summary
        print()
        print("=" * 70)
        print("SAMENVATTING")
        print("=" * 70)
        
        summary = windowed_data['summary']
        print(f"Overall status: {summary['overall_status']}")
        
        if summary.get('short_term_trend'):
            st = summary['short_term_trend']
            print(f"Kort termijn (30 min): {st['direction']} ({st['strength']})")
        
        if summary.get('medium_term_trend'):
            mt = summary['medium_term_trend']
            print(f"Medium termijn (3 uur): {mt['direction']} ({mt['strength']})")
        
        if summary.get('long_term_trend'):
            lt = summary['long_term_trend']
            print(f"Lang termijn (6 uur): {lt['direction']} ({lt['strength']})")
        
        # Sla resultaten op
        output_file = Path("test_sliding_window_real_output.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(windowed_data, f, indent=2, default=str)
        
        print()
        print(f"✅ Volledige output opgeslagen in: {output_file}")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Fout tijdens test: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_multiple_gemalen():
    """Test met meerdere gemalen om verschillende patronen te zien"""
    print("=" * 70)
    print("TEST MET MEERDERE GEMALEN")
    print("=" * 70)
    print()
    
    # Laad gemaal codes uit GeoJSON
    geojson_file = Path("rijnland_kaartlagen/Gemaal/Gemaal_layer0.geojson")
    
    if not geojson_file.exists():
        print(f"❌ GeoJSON bestand niet gevonden: {geojson_file}")
        return False
    
    fetcher = HydronetGemaalDataFetcher(CHART_ID, Path("temp_data"))
    codes = fetcher.load_gemaal_codes_from_geojson(str(geojson_file))
    
    if not codes:
        print("❌ Geen gemaal codes gevonden")
        return False
    
    # Test met eerste 3 gemalen
    test_codes = codes[:3]
    print(f"Testen met {len(test_codes)} gemalen: {', '.join(test_codes)}")
    print()
    
    results = []
    
    for code in test_codes:
        print(f"Ophalen data voor {code}...")
        try:
            data = fetcher.fetch_gemaal_data(code)
            
            if data and 'series' in data and len(data['series']) > 0:
                series = data['series'][0]
                if 'data' in series and len(series['data']) > 0:
                    series_data = series['data']
                    
                    windowed_data = process_gemaal_series(
                        code,
                        series_data,
                        windows_minutes=[30, 60]
                    )
                    
                    summary = windowed_data['summary']
                    current_value = windowed_data['current_value']
                    
                    results.append({
                        'code': code,
                        'current_value': current_value,
                        'overall_status': summary['overall_status'],
                        'data_points': len(series_data)
                    })
                    
                    print(f"  ✅ {code}: {current_value} m³/s, status: {summary['overall_status']}")
                else:
                    print(f"  ⚠️  {code}: Geen data punten")
            else:
                print(f"  ⚠️  {code}: Geen series data")
        
        except Exception as e:
            print(f"  ❌ {code}: Fout - {e}")
        
        print()
    
    # Samenvatting
    print("=" * 70)
    print("SAMENVATTING")
    print("=" * 70)
    
    if results:
        increasing = sum(1 for r in results if r['overall_status'] == 'increasing')
        decreasing = sum(1 for r in results if r['overall_status'] == 'decreasing')
        stable = sum(1 for r in results if r['overall_status'] == 'stable')
        
        print(f"Totaal getest: {len(results)}")
        print(f"Stijgend: {increasing}")
        print(f"Dalend: {decreasing}")
        print(f"Stabiel: {stable}")
    
    return len(results) > 0


if __name__ == "__main__":
    print()
    
    # Test met één gemaal
    success = test_with_real_api()
    
    if success:
        print()
        print("=" * 70)
        # Optioneel: test met meerdere gemalen (comment uit voor automatische test)
        # response = input("Wil je ook testen met meerdere gemalen? (j/n): ")
        # if response.lower() == 'j':
        #     print()
        #     test_multiple_gemalen()
        
        # Automatisch testen met meerdere gemalen (max 3 voor snelheid)
        print("Automatisch testen met meerdere gemalen...")
        print()
        test_multiple_gemalen()
    
    print()
    print("=" * 70)
    print("TEST VOLTOOID")
    print("=" * 70)

