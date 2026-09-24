"""
Simulátor GIST Controlling & BI (Staging vrstva a finanční analýza záruk).
Zajišťuje vazbu na Case ID, oddělení odhadů od schválených nákladů a skutečnou Paretovu analýzu.
"""

import pandas as pd
from datetime import datetime

INITIAL_GIST_DATA = [
    # BLAZE PRAKTIK EASY 25
    {
        "id": 1, "case_id": "CASE-2026-0001", "date": "2026-01-15",
        "model": "BLAZE PRAKTIK EASY 25", "serial_number": "BH-2025-0401", "lot": "2025-Q4",
        "component": "Snímač teploty spalin PT1000", "supplier": "Sensors s.r.o.",
        "part_cost": 850, "labor_cost": 400, "total_estimated_cost": 1250, "actual_cost": 1250,
        "warranty_status": "Uznáno výrobcem", "fault_reason": "Teplotní šok čidla"
    },
    {
        "id": 2, "case_id": "CASE-2026-0004", "date": "2026-02-04",
        "model": "BLAZE PRAKTIK EASY 25", "serial_number": "BH-2025-0442", "lot": "2025-Q4",
        "component": "Snímač teploty spalin PT1000", "supplier": "Sensors s.r.o.",
        "part_cost": 850, "labor_cost": 400, "total_estimated_cost": 1250, "actual_cost": 1250,
        "warranty_status": "Uznáno výrobcem", "fault_reason": "Zkrat ve svorkovnici"
    },
    {
        "id": 3, "case_id": "CASE-2026-0009", "date": "2026-02-18",
        "model": "BLAZE PRAKTIK EASY 25", "serial_number": "BH-2026-0012", "lot": "2026-Q1",
        "component": "Odtahový ventilátor EBM-Papst", "supplier": "EBM-Papst CZ",
        "part_cost": 4850, "labor_cost": 800, "total_estimated_cost": 5650, "actual_cost": 5650,
        "warranty_status": "Uznáno výrobcem", "fault_reason": "Zadřené ložisko"
    },
    {
        "id": 4, "case_id": "CASE-2026-0015", "date": "2026-03-02",
        "model": "BLAZE PRAKTIK EASY 25", "serial_number": "BH-2026-0045", "lot": "2026-Q1",
        "component": "Snímač teploty spalin PT1000", "supplier": "Sensors s.r.o.",
        "part_cost": 850, "labor_cost": 400, "total_estimated_cost": 1250, "actual_cost": 1250,
        "warranty_status": "Uznáno výrobcem", "fault_reason": "Mechanické poškození při instalaci"
    },
    
    # BLAZE HARMONY 20
    {
        "id": 5, "case_id": "CASE-2026-0018", "date": "2026-01-20",
        "model": "BLAZE HARMONY 20", "serial_number": "BH-2025-0280", "lot": "2025-Q3",
        "component": "Lambda sonda Bosch LSU 4.9", "supplier": "Bosch Termotechnika",
        "part_cost": 3200, "labor_cost": 600, "total_estimated_cost": 3800, "actual_cost": 3800,
        "warranty_status": "Uznáno subdodavatelem (Refund)", "fault_reason": "Výrobní vada vyhřívání"
    },
    {
        "id": 6, "case_id": "CASE-2026-0021", "date": "2026-01-29",
        "model": "BLAZE HARMONY 20", "serial_number": "BH-2025-0295", "lot": "2025-Q3",
        "component": "Lambda sonda Bosch LSU 4.9", "supplier": "Bosch Termotechnika",
        "part_cost": 3200, "labor_cost": 600, "total_estimated_cost": 3800, "actual_cost": 3800,
        "warranty_status": "Uznáno subdodavatelem (Refund)", "fault_reason": "Zkrat topného tělesa"
    },
    {
        "id": 7, "case_id": "CASE-2026-0025", "date": "2026-02-11",
        "model": "BLAZE HARMONY 20", "serial_number": "BH-2025-0310", "lot": "2025-Q3",
        "component": "Lambda sonda Bosch LSU 4.9", "supplier": "Bosch Termotechnika",
        "part_cost": 3200, "labor_cost": 600, "total_estimated_cost": 3800, "actual_cost": 3800,
        "warranty_status": "Uznáno subdodavatelem (Refund)", "fault_reason": "Zkrat topného tělesa"
    },
    {
        "id": 8, "case_id": "CASE-2026-0041", "date": "2026-02-24",
        "model": "BLAZE HARMONY 20", "serial_number": "BH-2024-0914", "lot": "2024-Q4",
        "component": "Odtahový ventilátor EBM-Papst", "supplier": "EBM-Papst CZ",
        "part_cost": 4850, "labor_cost": 800, "total_estimated_cost": 5650, "actual_cost": 5650,
        "warranty_status": "Uznáno výrobcem", "fault_reason": "Chyba Hallovy sondy"
    },

    # BLAZE COMFORT 30
    {
        "id": 9, "case_id": "CASE-2026-0038", "date": "2026-09-18",
        "model": "BLAZE COMFORT 30", "serial_number": "BH-2024-0651", "lot": "2024-Q3",
        "component": "Keramická zapalovací patrona FKK", "supplier": "FKK Corporation",
        "part_cost": 1450, "labor_cost": 467, "total_estimated_cost": 1917, "actual_cost": 1917,
        "warranty_status": "Uznáno výrobcem", "fault_reason": "Opotřebení spirály po 2 letech"
    },
    {
        "id": 10, "case_id": "CASE-2026-0042", "date": "2026-09-22",
        "model": "BLAZE COMFORT 30", "serial_number": "BH-2025-0112", "lot": "2025-Q1",
        "component": "Lambda sonda Bosch LSU 4.9", "supplier": "Bosch Termotechnika",
        "part_cost": 3200, "labor_cost": 600, "total_estimated_cost": 3800, "actual_cost": 3800,
        "warranty_status": "Uznáno subdodavatelem (Refund)", "fault_reason": "Interní zkrat modulu"
    },

    # BLAZE NATURAL PLUS 18 (Pouze kompatibilní díly!)
    {
        "id": 11, "case_id": "CASE-2026-0030", "date": "2026-01-25",
        "model": "BLAZE NATURAL PLUS 18", "serial_number": "BH-2025-0102", "lot": "2025-Q1",
        "component": "Snímač teploty spalin PT1000", "supplier": "Sensors s.r.o.",
        "part_cost": 850, "labor_cost": 400, "total_estimated_cost": 1250, "actual_cost": 1250,
        "warranty_status": "Uznáno výrobcem", "fault_reason": "Teplotní šok v kouřovodu"
    }
]

SUPPLIER_MAPPING = {
    "Snímač teploty spalin PT1000": "Sensors s.r.o.",
    "Lambda sonda Bosch LSU 4.9": "Bosch Termotechnika",
    "Odtahový ventilátor EBM-Papst": "EBM-Papst CZ",
    "Keramická zapalovací patrona FKK": "FKK Corporation",
    "Komunikační kabel / pokojový termostat": "Elektro partner s.r.o."
}

# Odhadovaný počet instalací na šarži pro výpočet relativní četnosti
ESTIMATED_LOT_INSTALLATIONS = {
    "2024-Q3": 180,
    "2024-Q4": 220,
    "2025-Q1": 250,
    "2025-Q2": 240,
    "2025-Q3": 210,
    "2025-Q4": 260,
    "2026-Q1": 190
}

def get_initial_df():
    """Vrací pandas DataFrame pro inicializaci GIST tabulky v session_state."""
    return pd.DataFrame(INITIAL_GIST_DATA)

def add_warranty_record(df, case_id, boiler_model, serial_number, lot, component, part_cost, labor_cost, fault_reason):
    """
    Přidá novou garanční událost do GIST staging tabulky.
    DŮLEŽITÉ: Nový záznam má status 'Čeká na posouzení garance' a actual_cost = 0.
    """
    new_id = int(df["id"].max()) + 1 if not df.empty else 1
    supplier = SUPPLIER_MAPPING.get(component, "BLAZE Interní díly")
    total_estimated = part_cost + labor_cost
    
    new_row = {
        "id": new_id,
        "case_id": case_id,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "model": boiler_model,
        "serial_number": serial_number,
        "lot": lot,
        "component": component,
        "supplier": supplier,
        "part_cost": part_cost,
        "labor_cost": labor_cost,
        "total_estimated_cost": total_estimated,
        "actual_cost": 0,  # Skutečný náklad není zaúčtován před schválením garance
        "warranty_status": "Čeká na posouzení garance",
        "fault_reason": fault_reason
    }
    
    updated_df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    return updated_df, new_row

def prepare_pareto_data(df):
    """
    Připraví data pro korektní Paretovu analýzu:
    Seřazené komponenty podle celkového nákladu, kumulativní součet a kumulativní procenta (0-100 %).
    """
    summary = df.groupby("component")["total_estimated_cost"].sum().sort_values(ascending=False).reset_index()
    total_sum = summary["total_estimated_cost"].sum()
    if total_sum > 0:
        summary["cum_cost"] = summary["total_estimated_cost"].cumsum()
        summary["cum_pct"] = (summary["cum_cost"] / total_sum) * 100.0
    else:
        summary["cum_cost"] = 0
        summary["cum_pct"] = 0
    return summary


# Odhadované velikosti dodavatelských sérií / nákupních šarží pro výpočet PPM a zmetkovitosti
COMPONENT_LOT_SIZES = {
    ("Lambda sonda Bosch LSU 4.9", "2025-Q3"): 45,
    ("Lambda sonda Bosch LSU 4.9", "2025-Q1"): 60,
    ("Snímač teploty spalin PT1000", "2025-Q4"): 120,
    ("Snímač teploty spalin PT1000", "2026-Q1"): 110,
    ("Snímač teploty spalin PT1000", "2025-Q1"): 85,
    ("Odtahový ventilátor EBM-Papst", "2026-Q1"): 90,
    ("Odtahový ventilátor EBM-Papst", "2024-Q4"): 80,
    ("Keramická zapalovací patrona FKK", "2024-Q3"): 60,
}

def calculate_supplier_quality_report(df):
    """
    Agreguje data podle dodavatele, komponenty a šarže.
    Vypočítává relativní míru zmetkovitosti / reklamovanosti vůči dodané šarži,
    finanční dopad a klasifikaci rizika pro nákupní controlling.
    """
    records = []
    grouped = df.groupby(["supplier", "component", "lot"])
    
    for (supplier, component, lot), group in grouped:
        defects = len(group)
        delivered = COMPONENT_LOT_SIZES.get((component, lot), 75)
        defect_rate = round((defects / delivered) * 100.0, 1)
        
        total_cost = group["total_estimated_cost"].sum()
        refund_cost = group[group["warranty_status"].str.contains("Refund", na=False)]["actual_cost"].sum()
        net_blaze_cost = total_cost - refund_cost
        
        if defect_rate >= 4.0:
            risk_label = "Kritické (> 4 %)"
            risk_badge = "🔴 Kritické"
            action_recommendation = "Pozastavit platby zádržného, 100% refundace práce technika, prověřit dodávku."
        elif defect_rate >= 2.0:
            risk_label = "Zvýšené (2-4 %)"
            risk_badge = "🟡 Sledováno"
            action_recommendation = "Zvýšit namátkovou kontrolu při příjmu na skladě v Trnávce."
        else:
            risk_label = "V normě (< 2 %)"
            risk_badge = "🟢 V normě"
            action_recommendation = "Běžný provoz bez eskalace."

        records.append({
            "supplier": supplier,
            "component": component,
            "lot": lot,
            "delivered_qty": delivered,
            "defect_count": defects,
            "defect_rate_pct": defect_rate,
            "total_cost": total_cost,
            "refund_cost": refund_cost,
            "net_blaze_cost": net_blaze_cost,
            "risk_label": risk_label,
            "risk_badge": risk_badge,
            "action": action_recommendation
        })
        
    res_df = pd.DataFrame(records)
    if not res_df.empty:
        res_df = res_df.sort_values(by=["defect_rate_pct", "total_cost"], ascending=[False, False]).reset_index(drop=True)
    return res_df


# Odhadovaná prodejní báze (expedované kotle) a průměrná cena pro relativní controlling
MODEL_SALES_VOLUME = {
    "BLAZE HARMONY 20": 850,
    "BLAZE PRAKTIK EASY 25": 620,
    "BLAZE COMFORT 30": 210,
    "BLAZE NATURAL PLUS 18": 320
}

MODEL_AVG_PRICE_CZK = {
    "BLAZE HARMONY 20": 115000,
    "BLAZE PRAKTIK EASY 25": 89000,
    "BLAZE COMFORT 30": 139000,
    "BLAZE NATURAL PLUS 18": 79000
}

def calculate_model_relative_metrics(df):
    """
    Agreguje náklady podle modelových řad a přepočítává je na:
    1. Absolutní náklady (odhad vs. skutečnost v Kč)
    2. Jednotkový záruční náklad na prodaný kus (Kč / ks)
    3. Procento záručních nákladů z tržeb modelu (%)
    4. Míru reklamovanosti zařízení (% vadných kusů z instalované báze)
    """
    grouped = df.groupby("model").agg(
        total_estimated_cost=("total_estimated_cost", "sum"),
        actual_cost=("actual_cost", "sum"),
        incident_count=("id", "count")
    ).reset_index()

    grouped["sold_units"] = grouped["model"].map(MODEL_SALES_VOLUME).fillna(300)
    grouped["avg_price"] = grouped["model"].map(MODEL_AVG_PRICE_CZK).fillna(100000)
    
    # Celkové tržby modelové řady
    grouped["total_revenue"] = grouped["sold_units"] * grouped["avg_price"]
    
    # Jednotkový garanční náklad na prodaný kus (Kč/ks)
    grouped["cost_per_sold_unit"] = (grouped["total_estimated_cost"] / grouped["sold_units"]).round(1)
    grouped["actual_per_sold_unit"] = (grouped["actual_cost"] / grouped["sold_units"]).round(1)
    
    # Podíl záruk na tržbách (v promilích / procentech)
    grouped["warranty_share_pct"] = ((grouped["total_estimated_cost"] / grouped["total_revenue"]) * 100.0).round(3)
    
    # Relativní četnost poruch (% prodaných kotlů s reklamací)
    grouped["incident_rate_pct"] = ((grouped["incident_count"] / grouped["sold_units"]) * 100.0).round(2)
    
    return grouped


