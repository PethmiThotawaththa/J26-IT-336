"""
database.py
-----------
Lightweight, ultra-fast SQLite Data Access Layer for Component 4.
Uses Python's standard library sqlite3 with thread-safe connections,
dictionary row factories, and complete relational schema.
"""

import os
import sqlite3
from typing import List, Dict, Any, Optional
from backend.app.core.config import settings

DB_FILE = os.path.join(settings.DATA_DIR, "road_maintenance.db")

def get_connection():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Road Corridors
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS road_corridors (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        road_class TEXT DEFAULT 'Class B Highway',
        total_length_km REAL NOT NULL,
        district TEXT DEFAULT 'Colombo',
        lanes INTEGER DEFAULT 2,
        aadt INTEGER DEFAULT 20000,
        daily_esal REAL DEFAULT 1500.0,
        heavy_vehicle_pct REAL DEFAULT 5.0
    );
    """)
    
    # 2. Road Sections
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS road_sections (
        id TEXT PRIMARY KEY,
        corridor_id TEXT NOT NULL,
        corridor_name TEXT,
        start_chainage_km REAL NOT NULL,
        end_chainage_km REAL NOT NULL,
        start_lat REAL NOT NULL,
        start_lon REAL NOT NULL,
        end_lat REAL NOT NULL,
        end_lon REAL NOT NULL,
        altitude_m REAL DEFAULT 15.0,
        surface_type TEXT DEFAULT 'Dense Graded Asphalt Concrete',
        lanes INTEGER DEFAULT 2,
        structural_number REAL DEFAULT 3.8,
        pavement_age_years REAL DEFAULT 4.0,
        current_pci REAL DEFAULT 75.0,
        historical_pci_1yr_ago REAL DEFAULT 78.0,
        historical_decay_rate_annual REAL DEFAULT 3.0,
        crack_density_pct REAL DEFAULT 5.0,
        pothole_count INTEGER DEFAULT 0,
        iri_roughness REAL DEFAULT 2.2,
        rut_depth_mm REAL DEFAULT 3.5,
        daily_esal REAL DEFAULT 1500.0,
        aadt INTEGER DEFAULT 20000,
        heavy_vehicle_pct REAL DEFAULT 5.0,
        annual_precipitation_mm REAL DEFAULT 2674.0,
        monsoon_risk_factor REAL DEFAULT 1.78,
        FOREIGN KEY (corridor_id) REFERENCES road_corridors(id)
    );
    """)
    
    # 3. Inspection Surveys
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inspection_surveys (
        id TEXT PRIMARY KEY,
        section_id TEXT NOT NULL,
        survey_date TEXT NOT NULL,
        pci_score REAL NOT NULL,
        iri_roughness REAL,
        crack_density_pct REAL,
        pothole_count INTEGER DEFAULT 0,
        rut_depth_mm REAL DEFAULT 0.0,
        maintenance_applied TEXT DEFAULT 'None',
        maintenance_cost_lkr REAL DEFAULT 0.0,
        FOREIGN KEY (section_id) REFERENCES road_sections(id)
    );
    """)
    
    # 4. Maintenance Work Orders
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS maintenance_work_orders (
        id TEXT PRIMARY KEY,
        section_id TEXT NOT NULL,
        corridor_id TEXT NOT NULL,
        priority TEXT NOT NULL,
        action TEXT NOT NULL,
        hsr_item_code TEXT DEFAULT 'HSR-53',
        urgency_days INTEGER NOT NULL,
        estimated_cost_lkr REAL NOT NULL,
        emergency_rebuild_cost_lkr REAL NOT NULL,
        preventive_savings_lkr REAL NOT NULL,
        roi_percent REAL DEFAULT 0.0,
        assigned_crew TEXT,
        status TEXT DEFAULT 'QUEUED',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (section_id) REFERENCES road_sections(id)
    );
    """)
    
    conn.commit()
    conn.close()

# Helper queries
def db_query_all(query: str, params: tuple = ()) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()
    result = [dict(row) for row in rows]
    conn.close()
    return result

def db_query_one(query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def db_execute(query: str, params: tuple = ()):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    conn.close()
