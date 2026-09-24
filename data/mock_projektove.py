"""
Simulátor Projektově.cz (REST API a Task Management).
Umožňuje evidenci servisních ticketů s vazbou na Case ID a dynamický výpočet SLA.
"""

from datetime import datetime, timedelta
import pandas as pd

INITIAL_TASKS = [
    {
        "id": "PRJ-TASK-1042",
        "case_id": "CASE-2026-0041",
        "title": "Garanční oprava - Výměna odtahového ventilátoru",
        "boiler_model": "BLAZE HARMONY 20",
        "serial_number": "BH-2024-0914",
        "lot": "2024-Q4",
        "error_code": "E-08",
        "part_name": "Odtahový ventilátor EBM-Papst",
        "part_number": "BH-FAN-EBM-180",
        "partner_name": "Instalatérství Kovář & Syn",
        "partner_location": "Valašské Meziříčí",
        "assignee": "Marek Dvořák (Sklad ND & Servis)",
        "priority": "Vysoká",
        "status": "V řešení",
        "created_at": "2026-09-21 08:30",
        "due_date": "2026-09-24",
        "is_sla_met": True,
        "notes": "Díl byl vyskladněn, technik provede montáž ve středu dopoledne."
    },
    {
        "id": "PRJ-TASK-1041",
        "case_id": "CASE-2026-0042",
        "title": "Diagnostika - Chyba komunikace CAN modulu Lambda",
        "boiler_model": "BLAZE COMFORT 30",
        "serial_number": "BH-2025-0112",
        "lot": "2025-Q1",
        "error_code": "E-12",
        "part_name": "Lambda sonda Bosch LSU 4.9",
        "part_number": "BH-LAMBDA-BOSCH49",
        "partner_name": "Topení Morava s.r.o.",
        "partner_location": "Olomouc",
        "assignee": "Jan Novák (Specialista ecoMAX)",
        "priority": "Střední",
        "status": "Nový (K expedici)",
        "created_at": "2026-09-22 14:15",
        "due_date": "2026-09-25",
        "is_sla_met": True,
        "notes": "Zákazník hlásí vysokou spotřebu pelet po aktualizaci software."
    },
    {
        "id": "PRJ-TASK-1038",
        "case_id": "CASE-2026-0038",
        "title": "Výměna zapalovací patrony - 2. garanční rok",
        "boiler_model": "BLAZE COMFORT 30",
        "serial_number": "BH-2024-0651",
        "lot": "2024-Q3",
        "error_code": "E-01",
        "part_name": "Keramická zapalovací patrona FKK",
        "part_number": "BH-IGN-CERAMIC-300W",
        "partner_name": "TermoServis s.r.o.",
        "partner_location": "Přerov",
        "assignee": "Marek Dvořák (Sklad ND & Servis)",
        "priority": "Běžná",
        "status": "Uzavřeno",
        "created_at": "2026-09-18 10:00",
        "due_date": "2026-09-20",
        "is_sla_met": True,
        "notes": "Patrona vyměněna v termínu SLA, kotel v normálním provozu."
    },
    {
        "id": "PRJ-TASK-1035",
        "case_id": "CASE-2026-0035",
        "title": "Dodatečná kalibrace kouřovodu",
        "boiler_model": "BLAZE PRAKTIK EASY 25",
        "serial_number": "BH-2025-0550",
        "lot": "2025-Q3",
        "error_code": "E-04",
        "part_name": "Snímač teploty spalin PT1000",
        "part_number": "BH-SEN-PT1000-SP",
        "partner_name": "TermoServis s.r.o.",
        "partner_location": "Přerov",
        "assignee": "Marek Dvořák (Sklad ND & Servis)",
        "priority": "Běžná",
        "status": "Uzavřeno",
        "created_at": "2026-09-12 11:00",
        "due_date": "2026-09-14",
        "is_sla_met": False,  # Ukázka nedodržení SLA pro reálný výpočet
        "notes": "Zpoždění dodávky dílu od dodavatele čidel o 1 den."
    }
]

def calculate_dynamic_sla(tasks_list) -> float:
    """Vypočítá skutečné plnění SLA z uzavřených a probíhajících úkolů."""
    if not tasks_list:
        return 100.0
    sla_met_count = sum(1 for t in tasks_list if t.get("is_sla_met", True))
    return round((sla_met_count / len(tasks_list)) * 100.0, 1)

def create_task_payload(case_id, boiler_model, serial_number, lot, error_code, error_data, partner_name, partner_location, notes):
    """
    Vytvoří návrh JSON payloadu pro REST API Projektově.cz.
    Označeno jako návrh integračního kontraktu k diskuzi s vedoucím procesů a IT p. Hlobilem.
    """
    now = datetime.now()
    due_date = (now + timedelta(days=2)).strftime("%Y-%m-%d")
    
    payload = {
        "_comment": "NÁVRH INTEGRAČNÍHO KONTRAKTU - Předmět ověření s IT BLAZE HARMONY",
        "api_endpoint": "https://api.projektove.cz/v1/projects/4820/tasks",
        "http_method": "POST",
        "headers": {
            "Authorization": "Bearer <TOKEN_Z_VAULTU>",
            "Content-Type": "application/json",
            "X-Source-System": "Blaze-Core-Hub-v1"
        },
        "payload": {
            "project_id": 4820,
            "project_name": "Záruční a technická podpora BLAZE",
            "task": {
                "case_id": case_id,
                "name": f"Garanční zásah [{case_id}]: {error_data['title']} ({boiler_model})",
                "description": (
                    f"Případ {case_id} evidován ze Servisního Hubu BLAZE HARMONY.\n\n"
                    f"• Zařízení: {boiler_model} (Výr. číslo: {serial_number}, Šarže: {lot})\n"
                    f"• Závada: Kód {error_code} - {error_data['title']}\n"
                    f"• Požadovaný díl: {error_data['component']} (Kód: {error_data['part_number']})\n"
                    f"• Indikativní normočad výměny: {error_data['labor_norm_min']} min\n"
                    f"• Servisní partner: {partner_name} ({partner_location})\n"
                    f"• Záznam technika: {notes}\n"
                    f"• Servisní reference: {error_data['source_manual']}"
                ),
                "priority": "High" if error_code in ["E-04", "E-08"] else "Normal",
                "deadline": due_date,
                "stage": "Nový (K expedici náhradního dílu)",
                "tags": ["Záruka", "Selektivní distribuce", error_code, boiler_model.split()[1]],
                "custom_fields": {
                    "case_id": case_id,
                    "boiler_serial": serial_number,
                    "boiler_lot": lot,
                    "part_number": error_data["part_number"],
                    "estimated_part_cost_czk": error_data["unit_cost_czk"]
                }
            }
        }
    }
    return payload
