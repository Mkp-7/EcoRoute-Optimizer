"""
Database operations module for GreenRoute AI
Provides clean interface for database interactions
"""

import sqlite3
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config.settings import DATABASE_PATH


class Database:
    """Database connection and operations manager"""
    
    def __init__(self, db_path: Path = DATABASE_PATH):
        self.db_path = db_path
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """Ensure database file exists"""
        if not self.db_path.exists():
            print(f"⚠️  Database not found at {self.db_path}")
            print("Please run: python scripts/init_db.py")
            raise FileNotFoundError(f"Database not initialized: {self.db_path}")
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        return conn
    
    # ============= ROUTE OPERATIONS =============
    
    def save_route(self, route_data: Dict) -> int:
        """Save a calculated route to database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO routes (
                origin, destination, distance_km, mode, cost_usd, 
                time_hours, carbon_kg, carbon_intensity_avg, weather_impact
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            route_data['origin'],
            route_data['destination'],
            route_data['distance_km'],
            route_data['mode'],
            route_data['cost_usd'],
            route_data['time_hours'],
            route_data['carbon_kg'],
            route_data.get('carbon_intensity_avg'),
            route_data.get('weather_impact'),
        ))
        
        route_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return route_id
    
    def get_routes(self, origin: str, destination: str, limit: int = 10) -> List[Dict]:
        """Get recent routes for an origin-destination pair"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM routes
            WHERE origin = ? AND destination = ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (origin, destination, limit))
        
        routes = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return routes
    
    # ============= CARBON INTENSITY CACHE =============
    
    def cache_carbon_intensity(self, region: str, grid_zone: str, 
                               intensity: float) -> None:
        """Cache carbon intensity data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO carbon_intensity_cache (region, grid_zone, carbon_intensity)
                VALUES (?, ?, ?)
            """, (region, grid_zone, intensity))
            conn.commit()
        except sqlite3.IntegrityError:
            # Already cached for this timestamp
            pass
        finally:
            conn.close()
    
    def get_cached_carbon_intensity(self, region: str, 
                                    max_age_hours: int = 1) -> Optional[float]:
        """Get cached carbon intensity if recent enough"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT carbon_intensity 
            FROM carbon_intensity_cache
            WHERE region = ?
            AND datetime(timestamp) > datetime('now', ?)
            ORDER BY timestamp DESC
            LIMIT 1
        """, (region, f'-{max_age_hours} hours'))
        
        result = cursor.fetchone()
        conn.close()
        
        return result['carbon_intensity'] if result else None
    
    # ============= SHIPMENT OPERATIONS =============
    
    def save_shipment(self, shipment_data: Dict) -> int:
        """Save a shipment query"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO shipments (
                origin, destination, weight_lbs, deadline_hours,
                preference, selected_route_id, carbon_saved_kg, cost_saved_usd
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            shipment_data['origin'],
            shipment_data['destination'],
            shipment_data['weight_lbs'],
            shipment_data.get('deadline_hours'),
            shipment_data.get('preference'),
            shipment_data.get('selected_route_id'),
            shipment_data.get('carbon_saved_kg'),
            shipment_data.get('cost_saved_usd'),
        ))
        
        shipment_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return shipment_id
    
    def get_shipment_stats(self, days: int = 30) -> Dict:
        """Get aggregate shipment statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total_shipments,
                SUM(carbon_saved_kg) as total_carbon_saved,
                AVG(carbon_saved_kg) as avg_carbon_saved,
                SUM(cost_saved_usd) as total_cost_saved
            FROM shipments
            WHERE datetime(created_at) > datetime('now', ?)
        """, (f'-{days} days',))
        
        stats = dict(cursor.fetchone())
        conn.close()
        
        return stats
    
    # ============= VEHICLE TYPES =============
    
    def get_vehicle_types(self) -> List[Dict]:
        """Get all vehicle types"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM vehicle_types")
        vehicles = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return vehicles
    
    def get_vehicle_by_type(self, vehicle_type: str) -> Optional[Dict]:
        """Get specific vehicle type data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM vehicle_types WHERE type = ?", (vehicle_type,))
        result = cursor.fetchone()
        conn.close()
        
        return dict(result) if result else None
    
    # ============= WEATHER CACHE =============
    
    def cache_weather(self, location: str, weather_data: Dict) -> None:
        """Cache weather data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO weather_cache 
                (location, temperature_c, wind_speed_kmh, wind_direction_deg, conditions)
                VALUES (?, ?, ?, ?, ?)
            """, (
                location,
                weather_data.get('temperature_c'),
                weather_data.get('wind_speed_kmh'),
                weather_data.get('wind_direction_deg'),
                weather_data.get('conditions'),
            ))
            conn.commit()
        except sqlite3.IntegrityError:
            pass
        finally:
            conn.close()
    
    def get_cached_weather(self, location: str, 
                          max_age_hours: int = 6) -> Optional[Dict]:
        """Get cached weather if recent enough"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM weather_cache
            WHERE location = ?
            AND datetime(timestamp) > datetime('now', ?)
            ORDER BY timestamp DESC
            LIMIT 1
        """, (location, f'-{max_age_hours} hours'))
        
        result = cursor.fetchone()
        conn.close()
        
        return dict(result) if result else None
    
    # ============= AGENT LOGS =============
    
    def save_agent_log(self, shipment_id: int, log_data: Dict) -> int:
        """Save agent reasoning log"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO agent_logs (shipment_id, reasoning, tools_called, recommendation)
            VALUES (?, ?, ?, ?)
        """, (
            shipment_id,
            log_data.get('reasoning'),
            log_data.get('tools_called'),
            log_data.get('recommendation'),
        ))
        
        log_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return log_id


# Singleton instance
db = Database()
