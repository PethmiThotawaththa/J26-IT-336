"""
database_seeder.py
------------------
Seeds the SQLite database with harmonized RDA road sections,
inspections, traffic data, and initial maintenance work orders.
"""

import os
import pandas as pd
from backend.app.core.config import settings
from backend.app.models.database import (
    init_db,
    get_connection,
    db_query_one
)
from backend.app.services.maintenance import recommend_maintenance_action

def seed_database(force: bool = False):
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Check if already populated
        cursor.execute("SELECT COUNT(*) as cnt FROM road_sections")
        existing_count = cursor.fetchone()["cnt"]
        if existing_count > 0 and not force:
            print(f"[DatabaseSeeder] Database already populated with {existing_count} sections.")
            conn.close()
            return
            
        print("[DatabaseSeeder] Seeding database from processed RDA datasets...")
        
        # 1. Corridors
        corridors_meta = {
            "B047": {"name": "Battaramulla - Pannipitiya", "len": 7.42, "lanes": 2, "aadt": 41858, "esal": 1499.5, "heavy": 2.36},
            "B174": {"name": "Kottawa - Malabe", "len": 9.47, "lanes": 2, "aadt": 21585, "esal": 947.0, "heavy": 2.54},
            "B214": {"name": "Kirindiwela - Radawana", "len": 9.10, "lanes": 2, "aadt": 19160, "esal": 2390.2, "heavy": 8.04},
            "B240": {"name": "Meegoda - Athurugiriya", "len": 28.00, "lanes": 2, "aadt": 2241, "esal": 331.7, "heavy": 10.16},
            "B263": {"name": "Madinnagoda - Rajagiriya", "len": 5.55, "lanes": 2, "aadt": 31447, "esal": 2380.8, "heavy": 4.83},
            "B435": {"name": "Sri Jayawardenepura - Kotte / Orugodawatta", "len": 7.69, "lanes": 4, "aadt": 32604, "esal": 4540.9, "heavy": 8.51}
        }
        
        for c_id, c_data in corridors_meta.items():
            cursor.execute("""
            INSERT OR REPLACE INTO road_corridors (id, name, road_class, total_length_km, district, lanes, aadt, daily_esal, heavy_vehicle_pct)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (c_id, c_data["name"], "Class B Highway", c_data["len"], "Colombo", c_data["lanes"], c_data["aadt"], c_data["esal"], c_data["heavy"]))
            
        conn.commit()
        
        # 2. Road Sections
        features_csv = os.path.join(settings.DATA_PROCESSED, "deterioration_features.csv")
        if not os.path.exists(features_csv):
            print(f"[DatabaseSeeder] Error: {features_csv} not found.")
            conn.close()
            return
            
        df_sec = pd.read_csv(features_csv)
        work_orders_count = 0
        
        for _, row in df_sec.iterrows():
            cursor.execute("""
            INSERT OR REPLACE INTO road_sections (
                id, corridor_id, corridor_name, start_chainage_km, end_chainage_km,
                start_lat, start_lon, end_lat, end_lon, altitude_m, surface_type,
                lanes, structural_number, pavement_age_years, current_pci,
                historical_pci_1yr_ago, historical_decay_rate_annual, crack_density_pct,
                pothole_count, iri_roughness, rut_depth_mm, daily_esal, aadt,
                heavy_vehicle_pct, annual_precipitation_mm, monsoon_risk_factor
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row["section_id"], row["corridor_id"], row["corridor_name"],
                float(row["start_chainage_km"]), float(row["end_chainage_km"]),
                float(row["start_lat"]), float(row["start_lon"]),
                float(row["end_lat"]), float(row["end_lon"]),
                float(row["altitude_m"]), "Dense Graded Asphalt Concrete",
                int(row["lanes"]), float(row["structural_number"]), float(row["pavement_age_years"]),
                float(row["current_pci"]), float(row["historical_pci_1yr_ago"]),
                float(row["historical_decay_rate_annual"]), float(row["crack_density_pct"]),
                int(row["pothole_count"]), float(row["iri_roughness"]), float(row["rut_depth_mm"]),
                float(row["daily_esal"]), int(row["aadt"]), float(row["heavy_vehicle_pct"]),
                float(row["annual_precipitation_mm"]), float(row["monsoon_risk_factor"])
            ))
            
            # Maintenance work order for deteriorating sections
            cur_pci = float(row["current_pci"])
            if cur_pci < 72.0:
                rec = recommend_maintenance_action(
                    pci=cur_pci,
                    crack_density_pct=float(row["crack_density_pct"]),
                    pothole_count=int(row["pothole_count"]),
                    rut_depth_mm=float(row["rut_depth_mm"]),
                    daily_esal=float(row["daily_esal"])
                )
                crew = "RDA Western Province Pavement Division"
                
                cursor.execute("""
                INSERT OR REPLACE INTO maintenance_work_orders (
                    id, section_id, corridor_id, priority, action, hsr_item_code,
                    urgency_days, estimated_cost_lkr, emergency_rebuild_cost_lkr,
                    preventive_savings_lkr, roi_percent, assigned_crew, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    f"WO-{row['section_id']}", row["section_id"], row["corridor_id"],
                    rec["priority"], rec["action"], rec["hsr_item_code"],
                    rec["urgency_days"], rec["estimated_cost_lkr"], rec["emergency_rebuild_cost_lkr"],
                    rec["preventive_savings_lkr"], rec["roi_percent"], crew, "QUEUED"
                ))
                work_orders_count += 1
                
        conn.commit()
        
        # 3. Inspections
        insp_csv = os.path.join(settings.DATA_PROCESSED, "longitudinal_inspections.csv")
        if os.path.exists(insp_csv):
            df_insp = pd.read_csv(insp_csv)
            for _, r in df_insp.iterrows():
                cursor.execute("""
                INSERT OR REPLACE INTO inspection_surveys (
                    id, section_id, survey_date, pci_score, iri_roughness,
                    crack_density_pct, pothole_count, rut_depth_mm,
                    maintenance_applied, maintenance_cost_lkr
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    r["survey_id"], r["section_id"], r["survey_date"],
                    float(r["pci_score"]), float(r["iri_roughness"]),
                    float(r["crack_density_pct"]), int(r["pothole_count"]),
                    float(r["rut_depth_mm"]), str(r["maintenance_applied"]),
                    float(r["maintenance_cost_lkr"])
                ))
            conn.commit()
            
        print(f"[DatabaseSeeder] Successfully seeded {len(df_sec)} road sections and {work_orders_count} work orders into SQLite.")
        
    except Exception as e:
        conn.rollback()
        print(f"[DatabaseSeeder] Error seeding database: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    seed_database(force=True)
