#!/usr/bin/env python3
"""
Sliding Window Processor voor Gemaal Data
==========================================

Berekent trends en aggregaties over verschillende tijdvensters voor gemaal timeseries data.
Gebaseerd op hoofdstuk 4 van Digital Twins boek - streaming data processing met sliding windows.
"""

from collections import deque
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class SlidingWindowProcessor:
    """
    Processor voor sliding window aggregaties en trend detectie over timeseries data.
    
    Gebruikt sliding windows om trends te berekenen zonder te wachten op batch completion.
    """
    
    def __init__(self, window_minutes: int = 30):
        """
        Initialiseer sliding window processor.
        
        Args:
            window_minutes: Grootte van het sliding window in minuten
        """
        self.window_minutes = window_minutes
        self.window = timedelta(minutes=window_minutes)
        self.data_points = deque()  # (timestamp, value) tuples
    
    def add_data_point(self, timestamp: datetime, value: float):
        """
        Voeg een nieuw datapunt toe aan het sliding window.
        Oude punten buiten het venster worden automatisch verwijderd.
        
        Args:
            timestamp: Timestamp van het datapunt
            value: Waarde van het datapunt (bijv. debiet in m³/s)
        """
        # Verwijder oude punten buiten het venster
        cutoff = timestamp - self.window
        
        while self.data_points and self.data_points[0][0] < cutoff:
            self.data_points.popleft()
        
        # Voeg nieuw punt toe
        self.data_points.append((timestamp, value))
    
    def add_series_data(self, series_data: List[Dict]):
        """
        Voeg meerdere datapunten toe uit een timeseries.
        
        Args:
            series_data: Lijst van dicts met 'timestamp_ms' en 'value' keys
        """
        for point in series_data:
            timestamp_ms = point.get('timestamp_ms', 0)
            value = point.get('value', 0)
            
            if timestamp_ms > 0:
                timestamp = datetime.fromtimestamp(timestamp_ms / 1000)
                self.add_data_point(timestamp, value)
    
    def get_window_stats(self) -> Optional[Dict]:
        """
        Bereken statistieken over het huidige sliding window.
        
        Returns:
            Dict met statistieken of None als er te weinig data is
        """
        if len(self.data_points) < 2:
            return None
        
        values = [dp[1] for dp in self.data_points]
        timestamps = [dp[0] for dp in self.data_points]
        
        return {
            'count': len(values),
            'min': min(values),
            'max': max(values),
            'avg': sum(values) / len(values),
            'sum': sum(values),
            'first_value': values[0],
            'last_value': values[-1],
            'window_start': timestamps[0].isoformat() if timestamps else None,
            'window_end': timestamps[-1].isoformat() if timestamps else None,
            'window_duration_minutes': (timestamps[-1] - timestamps[0]).total_seconds() / 60 if len(timestamps) > 1 else 0
        }
    
    def get_trend(self) -> Optional[Dict]:
        """
        Bereken trend over het sliding window met lineaire regressie.
        
        Returns:
            Dict met trend informatie of None als er te weinig data is
        """
        if len(self.data_points) < 2:
            return None
        
        # Converteer naar relatieve tijd (seconden vanaf eerste punt)
        first_timestamp = self.data_points[0][0]
        times = [(dp[0] - first_timestamp).total_seconds() for dp in self.data_points]
        values = [dp[1] for dp in self.data_points]
        
        n = len(times)
        sum_x = sum(times)
        sum_y = sum(values)
        sum_xy = sum(times[i] * values[i] for i in range(n))
        sum_x2 = sum(t**2 for t in times)
        
        # Bereken slope (trend) met lineaire regressie
        denominator = n * sum_x2 - sum_x * sum_x
        if denominator == 0:
            return None
        
        slope = (n * sum_xy - sum_x * sum_y) / denominator
        
        # Bepaal trend richting
        if abs(slope) < 0.001:
            trend_direction = 'stable'
        elif slope > 0:
            trend_direction = 'increasing'
        else:
            trend_direction = 'decreasing'
        
        # Bereken R² (coefficient of determination) voor trend betrouwbaarheid
        y_mean = sum_y / n
        ss_tot = sum((v - y_mean)**2 for v in values)
        ss_res = sum((values[i] - (slope * times[i] + (sum_y - slope * sum_x) / n))**2 for i in range(n))
        
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        
        return {
            'slope': round(slope, 6),  # Verandering per seconde
            'slope_per_hour': round(slope * 3600, 3),  # Verandering per uur
            'direction': trend_direction,
            'r_squared': round(r_squared, 3),  # Betrouwbaarheid (0-1)
            'strength': 'strong' if abs(slope) > 0.01 else 'moderate' if abs(slope) > 0.001 else 'weak'
        }
    
    def get_change_percentage(self) -> Optional[float]:
        """
        Bereken percentage verandering over het venster.
        
        Returns:
            Percentage verandering of None als er te weinig data is
        """
        if len(self.data_points) < 2:
            return None
        
        first_value = self.data_points[0][1]
        last_value = self.data_points[-1][1]
        
        if first_value == 0:
            return None
        
        change_pct = ((last_value - first_value) / abs(first_value)) * 100
        return round(change_pct, 2)
    
    def get_all_metrics(self) -> Dict:
        """
        Bereken alle metrics over het sliding window.
        
        Returns:
            Dict met alle berekende metrics
        """
        stats = self.get_window_stats()
        trend = self.get_trend()
        change_pct = self.get_change_percentage()
        
        result = {
            'data_points_count': len(self.data_points),
            'window_minutes': self.window_minutes,
            'has_sufficient_data': len(self.data_points) >= 2
        }
        
        if stats:
            result.update({
                'stats': stats,
                'min_debiet': round(stats['min'], 3),
                'max_debiet': round(stats['max'], 3),
                'avg_debiet': round(stats['avg'], 3),
                'total_debiet': round(stats['sum'], 3)
            })
        
        if trend:
            result.update({
                'trend': trend,
                'trend_direction': trend['direction'],
                'trend_strength': trend['strength']
            })
        
        if change_pct is not None:
            result['change_percentage'] = change_pct
        
        return result


class MultiWindowProcessor:
    """
    Processor die meerdere sliding windows tegelijk beheert voor verschillende tijdvensters.
    
    Bijvoorbeeld: 30 minuten, 1 uur, 6 uur vensters voor verschillende trend analyses.
    """
    
    def __init__(self, windows_minutes: List[int] = [30, 60, 180, 360]):
        """
        Initialiseer multi-window processor.
        
        Args:
            windows_minutes: Lijst van venster groottes in minuten
        """
        self.processors = {
            minutes: SlidingWindowProcessor(window_minutes=minutes)
            for minutes in windows_minutes
        }
    
    def add_data_point(self, timestamp: datetime, value: float):
        """
        Voeg datapunt toe aan alle windows.
        
        Args:
            timestamp: Timestamp van het datapunt
            value: Waarde van het datapunt
        """
        for processor in self.processors.values():
            processor.add_data_point(timestamp, value)
    
    def add_series_data(self, series_data: List[Dict]):
        """
        Voeg timeseries data toe aan alle windows.
        
        Args:
            series_data: Lijst van datapunten
        """
        for processor in self.processors.values():
            processor.add_series_data(series_data)
    
    def get_all_metrics(self) -> Dict:
        """
        Haal metrics op voor alle windows.
        
        Returns:
            Dict met metrics per window grootte
        """
        result = {}
        
        for window_minutes, processor in self.processors.items():
            metrics = processor.get_all_metrics()
            result[f'{window_minutes}_min'] = metrics
        
        return result
    
    def get_summary(self) -> Dict:
        """
        Haal samenvatting op met belangrijkste trends.
        
        Returns:
            Dict met samenvatting van trends over verschillende vensters
        """
        all_metrics = self.get_all_metrics()
        
        summary = {
            'short_term_trend': None,  # 30 min
            'medium_term_trend': None,  # 1-3 uur
            'long_term_trend': None,  # 6+ uur
            'overall_status': 'unknown'
        }
        
        # Kort termijn (30 min)
        if '30_min' in all_metrics and all_metrics['30_min'].get('trend'):
            summary['short_term_trend'] = all_metrics['30_min']['trend']
        
        # Medium termijn (1-3 uur)
        if '180_min' in all_metrics and all_metrics['180_min'].get('trend'):
            summary['medium_term_trend'] = all_metrics['180_min']['trend']
        
        # Lang termijn (6+ uur)
        if '360_min' in all_metrics and all_metrics['360_min'].get('trend'):
            summary['long_term_trend'] = all_metrics['360_min']['trend']
        
        # Bepaal overall status op basis van trends
        trends = [t for t in [
            summary['short_term_trend'],
            summary['medium_term_trend'],
            summary['long_term_trend']
        ] if t]
        
        if trends:
            directions = [t['direction'] for t in trends]
            if all(d == 'increasing' for d in directions):
                summary['overall_status'] = 'increasing'
            elif all(d == 'decreasing' for d in directions):
                summary['overall_status'] = 'decreasing'
            elif all(d == 'stable' for d in directions):
                summary['overall_status'] = 'stable'
            else:
                summary['overall_status'] = 'mixed'
        
        return summary


def process_gemaal_series(gemaal_code: str, series_data: List[Dict], 
                         windows_minutes: List[int] = [30, 60, 180]) -> Dict:
    """
    Verwerk timeseries data voor een gemaal met sliding windows.
    
    Args:
        gemaal_code: Code van het gemaal
        series_data: Lijst van datapunten uit de API
        windows_minutes: Lijst van venster groottes
    
    Returns:
        Dict met verwerkte metrics en trends
    """
    processor = MultiWindowProcessor(windows_minutes=windows_minutes)
    processor.add_series_data(series_data)
    
    all_metrics = processor.get_all_metrics()
    summary = processor.get_summary()
    
    # Haal laatste datapunt op
    last_point = series_data[-1] if series_data else None
    current_value = last_point.get('value', 0) if last_point else 0
    
    return {
        'gemaal_code': gemaal_code,
        'current_value': round(current_value, 3),
        'current_timestamp': last_point.get('timestamp') if last_point else None,
        'windows': all_metrics,
        'summary': summary,
        'processed_at': datetime.now().isoformat()
    }

