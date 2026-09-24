"""
Správce servisních případů (Case Manager).
Zajišťuje jednotný životní cyklus servisního případu (Case ID), provázanost na Projektově.cz,
GIST Controlling a evidenci případů vyřešených v terénu bez eskalace (First-Time Fix).
"""

from datetime import datetime, timedelta
import pandas as pd
from data.boiler_knowledge import LABOR_HOURLY_RATE_CZK

INITIAL_CASES = [
    {
        "case_id": "CASE-2026-0038",
        "created_at": "2026-09-18 09:45",
        "boiler_model": "BLAZE COMFORT 30",
        "serial_number": "BH-2024-0651",
        "lot": "2024-Q3",
        "partner_name": "TermoServis s.r.o.",
        "partner_location": "Přerov",
        "error_code": "E-01",
        "component": "Keramická zapalovací patrona FKK",
        "part_number": "BH-IGN-CERAMIC-300W",
        "resolution_type": "Eskalováno (Garanční výměna)",
        "task_id": "PRJ-TASK-1038",
        "estimated_part_cost": 1450,
        "estimated_labor_cost": 467,
        "actual_cost": 1917,
        "warranty_status": "Uznáno výrobcem",
        "case_status": "Uzavřeno",
        "notes": "Patrona vyměněna po 2 letech, opotřebení spirály."
    },
    {
        "case_id": "CASE-2026-0039",
        "created_at": "2026-09-19 11:20",
        "boiler_model": "BLAZE PRAKTIK EASY 25",
        "serial_number": "BH-2025-0720",
        "lot": "2025-Q4",
        "partner_name": "Instalatérství Kovář & Syn",
        "partner_location": "Valašské Meziříčí",
        "error_code": "E-04",
        "component": "Snímač teploty spalin PT1000",
        "part_number": "BH-SEN-PT1000-SP",
        "resolution_type": "Vyřešeno v terénu (Self-Service)",
        "task_id": None,
        "estimated_part_cost": 0,
        "estimated_labor_cost": 0,
        "actual_cost": 0,
        "warranty_status": "Bez nákladu",
        "case_status": "Uzavřeno",
        "notes": "Zjištěn zanesený kouřovod a uvolněný šroub svorky 41. Očištěno a dotaženo, odpor 1078 Ω v normě."
    },
    {
        "case_id": "CASE-2026-0040",
        "created_at": "2026-09-20 14:10",
        "boiler_model": "BLAZE HARMONY 20",
        "serial_number": "BH-2025-0318",
        "lot": "2025-Q3",
        "partner_name": "Topení Morava s.r.o.",
        "partner_location": "Olomouc",
        "error_code": "E-12",
        "component": "Lambda sonda Bosch LSU 4.9",
        "part_number": "BH-LAMBDA-BOSCH49",
        "resolution_type": "Vyřešeno v terénu (Self-Service)",
        "task_id": None,
        "estimated_part_cost": 0,
        "estimated_labor_cost": 0,
        "actual_cost": 0,
        "warranty_status": "Bez nákladu",
        "case_status": "Uzavřeno",
        "notes": "Provedena úspěšná rekalibrace lambda sondy na čerstvém vzduchu v servisním menu ecoMAX. Zbytkový O2 v normě."
    },
    {
        "case_id": "CASE-2026-0041",
        "created_at": "2026-09-21 08:30",
        "boiler_model": "BLAZE HARMONY 20",
        "serial_number": "BH-2024-0914",
        "lot": "2024-Q4",
        "partner_name": "Instalatérství Kovář & Syn",
        "partner_location": "Valašské Meziříčí",
        "error_code": "E-08",
        "component": "Odtahový ventilátor EBM-Papst",
        "part_number": "BH-FAN-EBM-180",
        "resolution_type": "Eskalováno (Garanční výměna)",
        "task_id": "PRJ-TASK-1042",
        "estimated_part_cost": 4850,
        "estimated_labor_cost": 800,
        "actual_cost": 5650,
        "warranty_status": "Uznáno výrobcem",
        "case_status": "V řešení",
        "notes": "Vadná Hallova sonda na motoru ventilátoru, vyskladněn nový díl."
    },
    {
        "case_id": "CASE-2026-0042",
        "created_at": "2026-09-22 14:15",
        "boiler_model": "BLAZE COMFORT 30",
        "serial_number": "BH-2025-0112",
        "lot": "2025-Q1",
        "partner_name": "Topení Morava s.r.o.",
        "partner_location": "Olomouc",
        "error_code": "E-12",
        "component": "Lambda sonda Bosch LSU 4.9",
        "part_number": "BH-LAMBDA-BOSCH49",
        "resolution_type": "Eskalováno (Garanční výměna)",
        "task_id": "PRJ-TASK-1041",
        "estimated_part_cost": 3200,
        "estimated_labor_cost": 600,
        "actual_cost": 3800,
        "warranty_status": "Uznáno subdodavatelem (Refund)",
        "case_status": "Nový (K expedici)",
        "notes": "Přepálené vyhřívací těleso v sondě Bosch."
    }
]

def calculate_labor_cost(labor_norm_min: int) -> int:
    """Kalkuluje normočad práce na základě standardní sazby 800 Kč/hod."""
    hours = labor_norm_min / 60.0
    return int(round(hours * LABOR_HOURLY_RATE_CZK))

def get_next_case_id(cases_list) -> str:
    """Generuje sekvenční ID případu."""
    highest_num = 42
    for c in cases_list:
        try:
            num = int(c["case_id"].split("-")[-1])
            if num > highest_num:
                highest_num = num
        except Exception:
            pass
    return f"CASE-2026-{highest_num + 1:04d}"

def get_existing_case(cases_list, serial_number: str, error_code: str):
    """
    Zjišťuje, zda pro dané sériové číslo a kód chyby již existuje evidovaný případ.
    Vrací nalezený případ nebo None.
    """
    s_clean = serial_number.strip().upper()
    for c in cases_list:
        if c["serial_number"].strip().upper() == s_clean and c["error_code"] == error_code:
            return c
    return None

def is_case_already_escalated(cases_list, serial_number: str, error_code: str) -> bool:
    """Kontrola idempotence: zabraňuje duplicitní eskalaci otevřeného případu pro stejný kotel a chybu."""
    c = get_existing_case(cases_list, serial_number, error_code)
    if c and c["resolution_type"] == "Eskalováno (Garanční výměna)" and c["case_status"] in ["Nový", "Nový (K expedici)", "V řešení"]:
        return True
    return False

def is_case_already_resolved(cases_list, serial_number: str, error_code: str) -> bool:
    """Kontrola idempotence: zabraňuje opakovanému spamování vyřešení na místě pro stejný kotel a chybu."""
    c = get_existing_case(cases_list, serial_number, error_code)
    if c and c["resolution_type"] == "Vyřešeno v terénu (Self-Service)":
        return True
    return False

def record_on_site_resolution(cases_list, boiler_model, serial_number, lot, partner_name, partner_location, error_code, error_data, technician_notes):
    """Zaznamená úspěšný servisní zásah v terénu bez vzniku nákladů (First-Time Fix)."""
    case_id = get_next_case_id(cases_list)
    new_case = {
        "case_id": case_id,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "boiler_model": boiler_model,
        "serial_number": serial_number.strip(),
        "lot": lot,
        "partner_name": partner_name,
        "partner_location": partner_location,
        "error_code": error_code,
        "component": error_data["component"],
        "part_number": error_data["part_number"],
        "resolution_type": "Vyřešeno v terénu (Self-Service)",
        "task_id": None,
        "estimated_part_cost": 0,
        "estimated_labor_cost": 0,
        "actual_cost": 0,
        "warranty_status": "Bez nákladu",
        "case_status": "Uzavřeno",
        "notes": f"Vyřešeno svépomocí dle doporučeného postupu. {technician_notes}"
    }
    cases_list.insert(0, new_case)
    return new_case

def record_escalation(cases_list, boiler_model, serial_number, lot, partner_name, partner_location, error_code, error_data, technician_notes):
    """Zaznamená eskalaci případu a vygeneruje podklad pro úkol v Projektově.cz i záznam v GISTu."""
    case_id = get_next_case_id(cases_list)
    task_id = f"PRJ-TASK-{1043 + len([c for c in cases_list if c['task_id']])}"
    labor_cost = calculate_labor_cost(error_data["labor_norm_min"])
    part_cost = error_data["unit_cost_czk"]
    
    new_case = {
        "case_id": case_id,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "boiler_model": boiler_model,
        "serial_number": serial_number.strip(),
        "lot": lot,
        "partner_name": partner_name,
        "partner_location": partner_location,
        "error_code": error_code,
        "component": error_data["component"],
        "part_number": error_data["part_number"],
        "resolution_type": "Eskalováno (Garanční výměna)",
        "task_id": task_id,
        "estimated_part_cost": part_cost,
        "estimated_labor_cost": labor_cost,
        "actual_cost": 0,  # Skutečný náklad bude zaúčtován až po schválení
        "warranty_status": "Čeká na posouzení garance",
        "case_status": "Nový (K expedici)",
        "notes": technician_notes
    }
    cases_list.insert(0, new_case)
    return new_case
