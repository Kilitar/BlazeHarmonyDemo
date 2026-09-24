"""
Databáze znalostí a matice kompatibility kotlů BLAZE HARMONY s.r.o.
Zajišťuje striktní provázanost: Model -> Regulace -> Kompatibilní komponenty a závady.
"""

LABOR_HOURLY_RATE_CZK = 800  # Standardní hodinová zúčtovací sazba garančního servisu

BOILER_MODELS = {
    "BLAZE PRAKTIK EASY 25": {
        "type": "Zplyňovací kotel na dřevo (ekonomická řada 2025)",
        "fuel": "Kusové dřevo (vlhkost do 20 %)",
        "controller": "ecoMAX 800D",
        "power_range": "12 - 25 kW",
        "lambda_sensor": "Volitelná výbava (Bosch LSU 4.9)",
        "exhaust_fan": "Ano (EBM-Papst s regulací)",
        "ignition_element": "Ne (ruční zápal)",
        "compatible_errors": ["E-04", "E-08", "E-12"],
        "description": "Nová cenově dostupná řada reagující na ukončení dotačních titulů. Zaměřeno na jednoduchou obsluhu a nízké výrobní náklady.",
    },
    "BLAZE HARMONY 20": {
        "type": "Kombinovaný / zplyňovací kotel (Vlajková loď)",
        "fuel": "Dřevo / Pelety (automatický přechod)",
        "controller": "ecoMAX 860P s dotykovým panelem",
        "power_range": "6 - 20 kW",
        "lambda_sensor": "Standardně osazena",
        "exhaust_fan": "Ano (EBM-Papst s Hallovou sondou)",
        "ignition_element": "Ano (keramická patrona pro pelety)",
        "compatible_errors": ["E-04", "E-12", "E-08", "E-01"],
        "description": "Patentovaná třícestná konstrukce a rotační hořák. Maximální účinnost nad 92 % a splnění nejpřísnějších norem.",
    },
    "BLAZE COMFORT 30": {
        "type": "Automatický kotel na pelety",
        "fuel": "Dřevní pelety ENplus A1",
        "controller": "ecoMAX 920",
        "power_range": "9 - 30 kW",
        "lambda_sensor": "Standardně osazena",
        "exhaust_fan": "Ano (EBM-Papst s Hallovou sondou)",
        "ignition_element": "Ano (keramická patrona)",
        "compatible_errors": ["E-01", "E-04", "E-08", "E-12"],
        "description": "Plně automatické čištění výměníku a odpopelnění. Určeno pro náročné instalace s požadavkem na minimální údržbu.",
    },
    "BLAZE NATURAL PLUS 18": {
        "type": "Splyňovací kotel s přirozeným komínovým tahem",
        "fuel": "Kusové dřevo",
        "controller": "ecoMAX 200 (Základní regulace)",
        "power_range": "9 - 18 kW",
        "lambda_sensor": "Není součástí (mechanické směšování)",
        "exhaust_fan": "Není součástí (provoz na přirozený tah)",
        "ignition_element": "Ne (ruční zápal)",
        "compatible_errors": ["E-04", "E-COMM-01"],
        "description": "Schopnost provozu v samotížném režimu bez odtahového ventilátoru. Neobsahuje lambda sondu ani zapalovací patronu.",
    }
}

ERROR_CODES = {
    "E-04": {
        "title": "Porucha snímače teploty spalin / Přehřátí spalin",
        "component": "Snímač teploty spalin PT1000",
        "part_number": "BH-SEN-PT1000-SP",
        "unit_cost_czk": 850,
        "labor_norm_min": 30,
        "symptoms": "Řídicí jednotka hlásí přehřátí spalin nad 280 °C nebo rozpojený obvod snímače (displej ukazuje --- °C).",
        "root_causes": [
            "Přerušený vodič nebo zkrat ve svorkovnici snímače spalin (svorky 41-42).",
            "Vadné čidlo PT1000 (teplotní šok v kouřovodu nebo mechanické poškození).",
            "Zanesený kouřovod a silná vrstva popílku izolující čidlo od proudu spalin."
        ],
        "diagnostics_steps": [
            "1. Vypněte hlavní vypínač kotle a nechte těleso kouřovodu zchladnout pod 40 °C.",
            "2. Odpojte konektor snímače spalin ze svorek 41 a 42 na základní desce ecoMAX.",
            "3. Multimetrem změřte ohmický odpor snímače přímo na odpojených vodičích:",
            "   • Při 0 °C: cca 1000 Ω\n   • Při 20 °C (pokojová teplota): cca 1077 Ω až 1082 Ω\n   • Při 100 °C: cca 1385 Ω",
            "4. Pokud multimetr naměří nekonečný odpor (přerušení) nebo odpor < 100 Ω (zkrat), čidlo je vadné a je nutná výměna.",
            "5. Zkontrolujte čistotu jímky čidla a zda není vodič spečený o plášť kotle."
        ],
        "terminal_mapping": "ecoMAX -> Svorky 41 (SPAL_IN) a 42 (GND_SPAL)",
        "source_manual": "Servisní a instalační manuál BLAZE PRAKTIK & HARMONY, kap. 8.3: Diagnostika čidel a svorkovnice, str. 47",
        "keywords": ["pt1000", "spalin", "teplota", "odpor", "ohm", "svorky 41", "42", "přehřátí", "multimetr"]
    },
    "E-12": {
        "title": "Porucha širokopásmové Lambda sondy",
        "component": "Lambda sonda Bosch LSU 4.9",
        "part_number": "BH-LAMBDA-BOSCH49",
        "unit_cost_czk": 3200,
        "labor_norm_min": 45,
        "symptoms": "Jednotka přejde do nouzového režimu řízení spalování (fixní poměr vzduchu). Hodnota zbytkového O2 kolísá nebo je zamrzlá na 21.0 %.",
        "root_causes": [
            "Přepálené vyhřívání lambda sondy vlivem agresivního kondenzátu nebo dehtu.",
            "Koroze kontaktů v 6-pinovém konektoru Lambda modulu (CAN bus modul).",
            "Zanesení ochranné mřížky sondy nespáleným dehtem (vlhké palivo > 25 %)."
        ],
        "diagnostics_steps": [
            "1. Zkontrolujte hlášení na modulu Lambda sondy (LED dioda – zelená bliká = vyhřívání, červená = chyba komunikace).",
            "2. V servisním menu 'Nastavení kotle -> Diagnostika -> Lambda' spusťte test kalibrace na čerstvém vzduchu.",
            "3. Vyjměte sondu z kouřovodu a změřte odpor topného tělíska mezi piny 3 a 4 (normální hodnota 3.0 až 4.5 Ω při 20 °C).",
            "4. Pokud je odpor topného tělíska přerušený, jednotka sondu nerozehřeje a je nutná výměna celého tělesa sondy.",
            "5. Při montáži nové sondy použijte výhradně keramickou pastu na závit M18x1.5 (nikdy ne maziva na bázi silikonu!)."
        ],
        "terminal_mapping": "Lambda CAN-BUS modul -> Svorkovnice BUS (CAN_H, CAN_L, 12V, GND)",
        "source_manual": "Manuál řídicí jednotky ecoMAX 860 / Lambda modul BLAZE, str. 32-34",
        "keywords": ["lambda", "bosch", "lsu", "o2", "kyslík", "vyhřívání", "kalibrace", "kanálový modul", "can bus"]
    },
    "E-08": {
        "title": "Chyba otáček odtahového ventilátoru (Hallova sonda)",
        "component": "Odtahový ventilátor EBM-Papst s Hallovou sondou",
        "part_number": "BH-FAN-EBM-180",
        "unit_cost_czk": 4850,
        "labor_norm_min": 60,
        "symptoms": "Kotel nesepne odtah při požadavku na zápal nebo spadne do chyby při překročení limitu otáček. Ztráta podtlaku.",
        "root_causes": [
            "Zadřené ložisko oběžného kola způsobené usazeným kreosotem (spalování nevhodného paliva).",
            "Závada Hallova snímače otáček na zadní hřídeli motoru ventilátoru.",
            "Vadný rozběhový kondenzátor motoru (kapacita klesla pod 1.5 µF)."
        ],
        "diagnostics_steps": [
            "1. Rukou v ochranné rukavici protočte oběžné kolo ventilátoru (musí jít zcela hladce bez drhnutí a vůle).",
            "2. Pokud se kolo točí těžce, očistěte lopatky škrabkou a chemickým rozpouštědlem dehtu.",
            "3. Multimetrem zkontrolujte kapacitu rozběhového kondenzátoru (svorky C1-C2 motoru, nominál 2 µF ±5%).",
            "4. Na servisním konektoru ventilátoru změřte napětí tachometru (Hallova sonda): při otáčení kolem rukou musí napětí pulzovat 0–5 V DC.",
            "5. Pokud impulsy chybí i při hladkém otáčení, vyměňte elektronickou desku ventilátoru nebo kompletní motor."
        ],
        "terminal_mapping": "ecoMAX -> Svorky 21 (L_FAN), 22 (N), 23 (PE) + Tacho konektor",
        "source_manual": "Servisní a diagnostický manuál odtahových systémů BLAZE HARMONY, str. 19-21",
        "keywords": ["ventilátor", "ebm", "hallova sonda", "otáčky", "kondenzátor", "tah", "ložisko", "svorky 21"]
    },
    "E-01": {
        "title": "Neúspěšné zapálení / Ztráta plamene",
        "component": "Keramická zapalovací patrona FKK",
        "part_number": "BH-IGN-CERAMIC-300W",
        "unit_cost_czk": 1450,
        "labor_norm_min": 35,
        "symptoms": "Po uplynutí maximálního času zapalování (15 min) nedošlo ke vzrůstu teploty spalin. Pelety v hořáku doutnají bez plamene.",
        "root_causes": [
            "Prasklé nebo přepálené topné tělísko keramické zapalovací patrony.",
            "Zanesená foukací tryska vzduchu kolem patrony popelem.",
            "Nekvalitní pelety s vysokým obsahem popela nebo vysokou vlhkostí."
        ],
        "diagnostics_steps": [
            "1. V menu 'Ruční test výstupů' aktivujte výstup 'Zapalovač' na dobu 2 minut.",
            "2. Klešťovým ampérmetrem změřte proud na napájecím vodiči patrony (normální proud cca 1.2 A až 1.4 A při 230 V).",
            "3. Pokud je proud nulový, patronu odpojte a změřte odpor (normální studený odpor: 140 až 180 Ω).",
            "4. Odpor nekonečno = přepálená keramická spirála -> vyměňte patronu.",
            "5. Vyčistěte kanálek sekundárního zapalovacího vzduchu od spečenců a popela stlačeným vzduchem."
        ],
        "terminal_mapping": "ecoMAX -> Svorky 31 (IGN_L), 32 (IGN_N)",
        "source_manual": "Instalační a uživatelská příručka hořáků BLAZE HARMONY, str. 28",
        "keywords": ["zapalovač", "patrona", "fkk", "pelety", "zápal", "plamen", "proud", "ampér", "odpor 140"]
    },
    "E-COMM-01": {
        "title": "Ztráta komunikace s pokojovým termostatem",
        "component": "Komunikační kabel / pokojový termostat",
        "part_number": "BH-ACC-ROOM-WIRE",
        "unit_cost_czk": 450,
        "labor_norm_min": 25,
        "symptoms": "Kotel netopí do topného okruhu, na jednotce svítí symbol odpojeného pokojového panelu.",
        "root_causes": [
            "Přerušená dvoudrátová linka k termostatu.",
            "Uvolněný šroubek ve svorkovnici pokojového panelu.",
            "Vybité záložní baterie v bezdrátovém přijímači."
        ],
        "diagnostics_steps": [
            "1. Zkontrolujte napájení a baterie pokojového termostatu.",
            "2. Zkuste propojit svorky pokojového termostatu na regulaci krátkou propojkou (tzv. klema).",
            "3. Pokud kotel po propojení sepne čerpadlo, závada je ve vedení nebo v termostatu, nikoliv v kotli."
        ],
        "terminal_mapping": "ecoMAX 200 -> Svorky T1 - T2 (Beznapěťový kontakt)",
        "source_manual": "Uživatelská příručka regulace BLAZE ecoMAX 200, str. 12",
        "keywords": ["termostat", "komunikace", "vedení", "klema", "okruh", "pokojový"]
    }
}

PT1000_RESISTANCE_TABLE = [
    {"temp_c": -10, "ohms": 960.9},
    {"temp_c": 0, "ohms": 1000.0},
    {"temp_c": 10, "ohms": 1039.0},
    {"temp_c": 20, "ohms": 1077.9},
    {"temp_c": 25, "ohms": 1097.3},
    {"temp_c": 50, "ohms": 1194.0},
    {"temp_c": 80, "ohms": 1309.0},
    {"temp_c": 100, "ohms": 1385.1},
    {"temp_c": 150, "ohms": 1573.3},
    {"temp_c": 200, "ohms": 1758.6},
    {"temp_c": 250, "ohms": 1941.0},
    {"temp_c": 300, "ohms": 2120.5}
]

def get_compatible_errors_for_model(model_name: str) -> dict:
    """Vrací slovník chyb, které jsou fyzicky a konstrukčně kompatibilní s daným modelem kotle."""
    model_data = BOILER_MODELS.get(model_name)
    if not model_data:
        return {}
    allowed_keys = model_data.get("compatible_errors", [])
    return {k: v for k, v in ERROR_CODES.items() if k in allowed_keys}

def search_knowledge_base(model_name: str, error_code: str, note_text: str) -> dict:
    """
    Transparentní vyhledávání v technické dokumentaci na základě zadané chyby a poznámky technika.
    Vrací stav shody, úryvek a doporučení.
    """
    err_data = ERROR_CODES.get(error_code)
    if not err_data:
        return {
            "status": "not_found",
            "message": "Vybraný chybový kód nebyl v databázi nalezen."
        }
    
    # Analýza klíčových slov z poznámky technika
    note_lower = note_text.lower().strip()
    keywords = err_data.get("keywords", [])
    matched_keywords = [kw for kw in keywords if kw in note_lower]
    
    # Vyhledání konkrétních kroků odpovídajících poznámce
    relevant_steps = []
    if note_lower:
        for step in err_data["diagnostics_steps"]:
            step_lower = step.lower()
            if any(term in step_lower for term in note_lower.split() if len(term) > 3):
                relevant_steps.append(step)
    
    return {
        "status": "match" if matched_keywords or not note_text else "partial_match",
        "matched_keywords": matched_keywords,
        "highlighted_steps": relevant_steps if relevant_steps else err_data["diagnostics_steps"],
        "error_data": err_data
    }
