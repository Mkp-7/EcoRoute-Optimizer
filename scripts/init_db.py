"""
Database initialization script for GreenRoute AI
Creates SQLite database with necessary tables
"""

import sqlite3
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from config.settings import DATABASE_PATH

def create_tables(conn):
    """Create all necessary database tables"""
    
    cursor = conn.cursor()
    
    # Routes table - stores calculated route options
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS routes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            origin TEXT NOT NULL,
            destination TEXT NOT NULL,
            distance_km REAL NOT NULL,
            mode TEXT NOT NULL,  -- 'diesel_truck', 'electric_truck', 'rail', 'intermodal'
            cost_usd REAL NOT NULL,
            time_hours REAL NOT NULL,
            carbon_kg REAL NOT NULL,
            carbon_intensity_avg REAL,  -- Average grid carbon along route
            weather_impact REAL,  -- Fuel efficiency adjustment due to weather
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Carbon intensity cache - stores API responses to minimize calls
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS carbon_intensity_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            region TEXT NOT NULL,
            grid_zone TEXT,
            carbon_intensity REAL NOT NULL,  -- gCO2/kWh
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(region, timestamp)
        )
    """)
    
    # Vehicle types - reference data for emissions calculations
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vehicle_types (
            type TEXT PRIMARY KEY,
            fuel_type TEXT NOT NULL,  -- 'diesel', 'electric', 'hybrid', 'rail'
            emissions_factor REAL NOT NULL,  -- kg CO2 per km
            cost_per_km REAL NOT NULL,  -- USD per km
            avg_speed_kmh REAL NOT NULL,
            description TEXT
        )
    """)
    
    # Shipments - user query history
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS shipments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            origin TEXT NOT NULL,
            destination TEXT NOT NULL,
            weight_lbs REAL NOT NULL,
            deadline_hours REAL,
            preference TEXT,  -- 'cost', 'time', 'carbon', 'balanced'
            selected_route_id INTEGER,
            carbon_saved_kg REAL,
            cost_saved_usd REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (selected_route_id) REFERENCES routes(id)
        )
    """)
    
    # Weather cache - stores weather API responses
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS weather_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location TEXT NOT NULL,
            temperature_c REAL,
            wind_speed_kmh REAL,
            wind_direction_deg REAL,
            conditions TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(location, timestamp)
        )
    """)
    
    # Agent logs - stores Claude's reasoning for analysis
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agent_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            shipment_id INTEGER NOT NULL,
            reasoning TEXT,  -- Claude's explanation
            tools_called TEXT,  -- JSON list of tool calls
            recommendation TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (shipment_id) REFERENCES shipments(id)
        )
    """)
    
    conn.commit()
    print("✅ Database tables created successfully")


def insert_default_vehicle_types(conn):
    """Insert default vehicle type reference data"""
    
    cursor = conn.cursor()
    
    vehicle_data = [
        ('diesel_truck', 'diesel', 0.62, 1.20, 80, 'Standard diesel freight truck'),
        ('electric_truck', 'electric', 0.18, 1.15, 75, 'Electric freight truck (limited range)'),
        ('rail', 'electric', 0.08, 0.45, 65, 'Freight rail (most carbon efficient)'),
        ('intermodal', 'mixed', 0.15, 0.85, 55, 'Truck to rail hub, then rail to destination'),
    ]
    
    try:
        cursor.executemany("""
            INSERT OR REPLACE INTO vehicle_types 
            (type, fuel_type, emissions_factor, cost_per_km, avg_speed_kmh, description)
            VALUES (?, ?, ?, ?, ?, ?)
        """, vehicle_data)
        
        conn.commit()
        print("✅ Default vehicle types inserted")
    except sqlite3.IntegrityError:
        print("ℹ️  Vehicle types already exist, skipping insert")


def create_indexes(conn):
    """Create indexes for better query performance"""
    
    cursor = conn.cursor()
    
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_routes_origin_dest ON routes(origin, destination)",
        "CREATE INDEX IF NOT EXISTS idx_routes_mode ON routes(mode)",
        "CREATE INDEX IF NOT EXISTS idx_carbon_cache_region ON carbon_intensity_cache(region)",
        "CREATE INDEX IF NOT EXISTS idx_shipments_created ON shipments(created_at)",
    ]
    
    for index_sql in indexes:
        cursor.execute(index_sql)
    
    conn.commit()
    print("✅ Database indexes created")


def init_database():
    """Main initialization function"""
    
    # Ensure data directory exists
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"📁 Database location: {DATABASE_PATH}")
    
    # Create database and tables
    conn = sqlite3.connect(DATABASE_PATH)
    
    try:
        create_tables(conn)
        insert_default_vehicle_types(conn)
        create_indexes(conn)
        
        print("\n✨ Database initialization complete!")
        print(f"📊 Database ready at: {DATABASE_PATH}")
        
    except Exception as e:
        print(f"❌ Error during initialization: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    init_database()
