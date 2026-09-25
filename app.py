"""
Blaze Core Hub: Servisní & Procesní Prototyp (v2.0)
Připraveno pro BLAZE HARMONY s.r.o. | Pozice: Transformation & Process Manager

Architektonický návrh a funkční simulace propojení:
Terénní servis (B2B síť) ➔ Projektově.cz (Operativa / Task API) ➔ GIST (Controlling / Záruky).
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from datetime import datetime

# Import datových modulů a znalostní báze
from data.boiler_knowledge import (
    BOILER_MODELS, ERROR_CODES, PT1000_RESISTANCE_TABLE,
    get_compatible_errors_for_model, search_knowledge_base,
    LABOR_HOURLY_RATE_CZK
)
from data.case_manager import (
    INITIAL_CASES, record_on_site_resolution, record_escalation,
    is_case_already_escalated, is_case_already_resolved, get_existing_case,
    calculate_labor_cost
)
from data.mock_projektove import (
    INITIAL_TASKS, create_task_payload, calculate_dynamic_sla
)
from data.mock_gist import (
    get_initial_df, add_warranty_record, prepare_pareto_data,
    ESTIMATED_LOT_INSTALLATIONS, calculate_supplier_quality_report,
    calculate_model_relative_metrics
)

# --- KONFIGURACE STRÁNKY ---
st.set_page_config(
    page_title="Blaze Core Hub | Procesní & Diagnostický Prototyp",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- NAČTENÍ VLASTNÍHO CSS ---
try:
    with open("assets/custom.css", "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except Exception:
    pass

# --- INICIALIZACE SESSION STATE ---
if "cases" not in st.session_state:
    st.session_state.cases = list(INITIAL_CASES)

if "tasks" not in st.session_state:
    st.session_state.tasks = list(INITIAL_TASKS)

if "gist_df" not in st.session_state:
    st.session_state.gist_df = get_initial_df()

if "last_api_payload" not in st.session_state:
    st.session_state.last_api_payload = None

if "last_action_msg" not in st.session_state:
    st.session_state.last_action_msg = None


# --- VÝPOČTY PRO SIDEBAR (V REÁLNÉM ČASE) ---
active_tasks_count = len([t for t in st.session_state.tasks if t.get("status") not in ["Uzavřeno", "Dokončeno"]])
self_service_cases_count = len([c for c in st.session_state.cases if c.get("resolution_type") == "Vyřešeno v terénu (Self-Service)"])
total_cases_count = len(st.session_state.cases)
dynamic_sla_pct = calculate_dynamic_sla(st.session_state.tasks)

# --- SIDEBAR: FIREMNÍ KONTEXT A NAVIGACE ---
with st.sidebar:
    st.image("assets/blaze_logo.svg", width=200)
    st.markdown(
        "<div style='margin-top: 6px; margin-bottom: 12px;'><span class='blaze-header-badge'>Prototyp: Procesní řízení & integrace</span></div>",
        unsafe_allow_html=True
    )
    st.markdown("---")
    
    st.markdown("### 🏢 Firemní profil & IT ekosystém")
    st.caption("Ověřená data: BLAZE HARMONY, IF System, TOP TECH")
    st.markdown(
        """
        * **Výroba:** Trnávka *(3 500 m², Trumpf robotika, 150 lidí)*
        * **ERP & Sklad:** **HELIOS iNuvio (modul WMS)**
        * **Konstrukce & CAD:** **SOLIDWORKS & 3DEXPERIENCE**
        * **Vizuální manuály:** **SOLIDWORKS Composer**
        * **Operativa & Úkoly:** **Projektově.cz** *(tým p. Hlobila)*
        * **Controlling & Marže:** **GIST Controlling**
        """
    )
    st.markdown("---")
    
    st.markdown("### 🛠️ Stav procesních entit")
    col_sb1, col_sb2 = st.columns(2)
    with col_sb1:
        st.metric("Otevřené úkoly", active_tasks_count, help="Pouze neuzavřené úkoly v Projektově.cz")
    with col_sb2:
        st.metric("Vyřešeno na místě", self_service_cases_count, help="Servisní zásahy bez vzniku garančního nákladu")
        
    st.metric("Aktuální SLA plnění", f"{dynamic_sla_pct} %", help="Vypočteno ze skutečného stavu úkolů v simulaci")

    st.markdown("---")
    if st.button("🔄 Resetovat simulovaná data", use_container_width=True):
        st.session_state.cases = list(INITIAL_CASES)
        st.session_state.tasks = list(INITIAL_TASKS)
        st.session_state.gist_df = get_initial_df()
        st.session_state.last_api_payload = None
        st.session_state.last_action_msg = None
        st.rerun()

    st.markdown("---")
    st.caption("PoC pro výběrové řízení: Transformation & Process Manager")


# --- HLAVNÍ HLAVIČKA ---
col_head1, col_head2 = st.columns([1, 4])
with col_head1:
    st.image("assets/blaze_logo.svg", width=170)
with col_head2:
    st.title("Blaze Core Hub: Návrh procesní integrace")
    st.markdown(
        """
        **Metodický koncept propojení procesů:** Servisní diagnostika certifikovaného technika v terénu 
        ➔ Návrh integračního toku do **Projektově.cz** (operativa a sklad) ➔ Staging a analýza v **GIST Controllingu** (záruční vícenáklady a kvalita).
        """
    )

# --- NAVIGAČNÍ TABS ---
tab_diag, tab_proj, tab_gist, tab_arch = st.tabs([
    "📱 1. Terénní diagnostika (Technik)",
    "📋 2. Projektově.cz (Operativa & API)",
    "📊 3. GIST Controlling & BI (Záruky)",
    "🧭 4. Proces a přínosy (Pilotní projekt)"
])


# ==============================================================================
# TAB 1: TERÉNNÍ DIAGNOSTIKA (TECHNIK U KOTLE)
# ==============================================================================
with tab_diag:
    role_mode = st.radio(
        "Zvolte úroveň rozhraní (RBAC role):",
        [
            "🔧 Servisní režim (Akreditovaný partner — schémata svorkovnic, měření odporů, expedice dílů)",
            "👤 Zákaznický režim (Vizuální asistent obsluhy — L0 Self-Service bez nářadí, animované mikronávody)"
        ],
        horizontal=True,
        index=0
    )
    st.markdown("---")

    if role_mode.startswith("🔧"):
        st.markdown("### 📱 Diagnostická podpora servisního technika v terénu")
        st.caption("Simulovaná znalostní báze postavená na technické dokumentaci kotlů a regulací ecoMAX.")
        
        col_inp1, col_inp2, col_inp3 = st.columns([1.5, 1.2, 1.3])
        
        with col_inp1:
            selected_model = st.selectbox(
                "Model kotle BLAZE HARMONY:",
                list(BOILER_MODELS.keys()),
                index=0,
                help="Výběr modelu striktně filtruje kompatibilní výbavu a možné poruchy."
            )
        
        with col_inp2:
            serial_no = st.text_input("Výrobní číslo kotle:", value="BH-2025-0842")
            lot_no = st.selectbox("Výrobní šarže:", list(ESTIMATED_LOT_INSTALLATIONS.keys()), index=5)

        with col_inp3:
            partner_name = st.selectbox(
                "Servisní partner (Selektivní síť):",
                [
                    "Instalatérství Kovář & Syn (Valašské Meziříčí)",
                    "TermoServis s.r.o. (Přerov)",
                    "Topení Morava s.r.o. (Olomouc)",
                    "Kotle Rychle s.r.o. (Hranice)"
                ]
            )

        # Technická specifikace a kontrola kompatibility
        model_info = BOILER_MODELS[selected_model]
        with st.expander(f"ℹ️ Technický profil modelu: {selected_model}", expanded=False):
            c_p1, c_p2, c_p3 = st.columns(3)
            c_p1.markdown(f"**Typ:** {model_info['type']}")
            c_p1.markdown(f"**Palivo:** {model_info['fuel']}")
            c_p2.markdown(f"**Regulace:** `{model_info['controller']}`")
            c_p2.markdown(f"**Výkon:** {model_info['power_range']}")
            c_p3.markdown(f"**Lambda sonda:** {model_info['lambda_sensor']}")
            c_p3.markdown(f"**Odtahový ventilátor:** {model_info['exhaust_fan']}")
            st.caption(model_info['description'])

        st.markdown("---")
        
        # Dynamický výběr pouze kompatibilních chyb pro daný model
        compatible_errors = get_compatible_errors_for_model(selected_model)
        
        col_err1, col_err2 = st.columns([1.5, 2.5])
        
        with col_err1:
            st.markdown("#### ⚠️ Zjištěné symptomy & chybový kód")
            err_selection = st.radio(
                f"Kódy hlášené regulací `{model_info['controller']}`:",
                list(compatible_errors.keys()),
                format_func=lambda x: f"{x} - {compatible_errors[x]['title']}"
            )
            
            custom_notes = st.text_area(
                "Poznámka technika (vstup pro vyhledání v postupech):",
                value="Multimetr naměřil nekonečný odpor na svorkách 41-42, kouřovod studený.",
                help="Zadejte pozorování z terénu. Vyhledávací engine prohledá text servisních manuálů."
            )

        # Vyhledání v dokumentaci podle kódu i poznámky
        search_result = search_knowledge_base(selected_model, err_selection, custom_notes)
        err_data = search_result["error_data"]

        with col_err2:
            st.markdown(f"#### 🔍 Doporučený servisní postup: {err_data['title']}")
            
            calculated_labor = calculate_labor_cost(err_data['labor_norm_min'])
            
            st.markdown(
                f"""
                <div class='blaze-diag-card'>
                    <strong>Komponenta:</strong> {err_data['component']} (Kód: <code>{err_data['part_number']}</code>)<br>
                    <strong>Indikativní cena dílu:</strong> {err_data['unit_cost_czk']} Kč | 
                    <strong>Normočad výměny:</strong> {err_data['labor_norm_min']} min (Kalkulovaná práce: {calculated_labor} Kč při {LABOR_HOURLY_RATE_CZK} Kč/h)<br>
                    <strong>Příznaky v dokumentaci:</strong> {err_data['symptoms']}
                </div>
                """,
                unsafe_allow_html=True
            )

            # Zobrazení shody z vyhledávání
            if search_result["matched_keywords"]:
                st.success(f"🎯 **Nalezena shoda s poznámkou technika:** klíčová slova `{', '.join(search_result['matched_keywords'])}`")
            elif custom_notes.strip():
                st.info("ℹ️ *Poznámka neobsahuje specifické klíčové termíny z manuálu — zobrazen standardní diagnostický postup.*")

            st.markdown("##### 🛠️ Kroky proměření a odstranění:")
            for step in search_result["highlighted_steps"]:
                st.markdown(step)

            st.caption(f"📖 Doložená reference: *{err_data['source_manual']}*")
            st.caption(f"🔌 Svorkovnice: `{err_data['terminal_mapping']}`")

            # Tabulka odporů pro PT1000
            if err_selection == "E-04":
                with st.expander("📊 Referenční ohmická tabulka čidla PT1000 pro multimetr", expanded=False):
                    st.dataframe(pd.DataFrame(PT1000_RESISTANCE_TABLE), height=180, use_container_width=True)

        # Akční panel pro technika
        st.markdown("---")
        st.markdown("#### ⚡ Rozhodnutí technika v terénu")
        
        # Kontrola idempotence: zda již případ nebyl eskalován nebo vyřešen na místě
        existing_case = get_existing_case(st.session_state.cases, serial_no, err_selection)
        already_escalated = is_case_already_escalated(st.session_state.cases, serial_no, err_selection)
        already_resolved = is_case_already_resolved(st.session_state.cases, serial_no, err_selection)
        is_case_locked = already_escalated or already_resolved
        
        col_act1, col_act2 = st.columns(2)
        
        with col_act1:
            resolve_on_site_clicked = st.button(
                "✅ Závada vyřešena na místě (vyčištěno / seřízeno / bez nákladu)",
                use_container_width=True,
                disabled=is_case_locked,
                help="Zaznamená úspěšný zásah v terénu (Self-Service). Lze použít pouze jednou pro dané v.č. a vadu."
            )

        with col_act2:
            escalate_clicked = st.button(
                "🚨 Potvrzena vadná součástka ➔ Eskalovat případ",
                type="primary",
                use_container_width=True,
                disabled=is_case_locked,
                help="Vytvoří úkol pro expedici dílu a zaeviduje odhad nákladů do schvalování záruk."
            )

        partner_split = partner_name.split("(")
        p_name = partner_split[0].strip()
        p_loc = partner_split[1].replace(")", "").strip() if len(partner_split) > 1 else "ČR"

        if resolve_on_site_clicked:
            new_case = record_on_site_resolution(
                st.session_state.cases,
                selected_model, serial_no, lot_no, p_name, p_loc,
                err_selection, err_data, custom_notes
            )
            st.success(
                f"🎉 **Servisní případ `{new_case['case_id']}` byl zaevidován jako 'Vyřešeno v terénu'!**\n\n"
                f"• Zařízení: `{selected_model}` (v.č. `{serial_no}`)\n"
                f"• Výsledek: Zásah dokončen bez nutnosti expedice dílu a bez zatížení dispečinku.\n"
                f"• Údaj byl propsán do metriky First-Time Fix Rate."
            )
            st.rerun()

        if escalate_clicked:
            if already_escalated:
                st.warning("Tento případ je již evidován jako otevřený servisní požadavek.")
            else:
                # 1. Založení unifikovaného případu v Case Manageru
                new_case = record_escalation(
                    st.session_state.cases,
                    selected_model, serial_no, lot_no, p_name, p_loc,
                    err_selection, err_data, custom_notes
                )
                
                # 2. Vytvoření úkolu v Projektově.cz s Case ID
                task_id = new_case["task_id"]
                due_date = (datetime.now() + pd.Timedelta(days=2)).strftime("%Y-%m-%d")
                
                payload = create_task_payload(
                    new_case["case_id"], selected_model, serial_no, lot_no,
                    err_selection, err_data, p_name, p_loc, custom_notes
                )
                
                new_task = {
                    "id": task_id,
                    "case_id": new_case["case_id"],
                    "title": f"Garanční oprava [{new_case['case_id']}] - {err_data['component']} ({selected_model})",
                    "boiler_model": selected_model,
                    "serial_number": serial_no,
                    "lot": lot_no,
                    "error_code": err_selection,
                    "part_name": err_data["component"],
                    "part_number": err_data["part_number"],
                    "partner_name": p_name,
                    "partner_location": p_loc,
                    "assignee": "Marek Dvořák (Sklad ND & Servis)",
                    "priority": "Vysoká" if err_selection in ["E-04", "E-08"] else "Střední",
                    "status": "Nový (K expedici)",
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "due_date": due_date,
                    "is_sla_met": True,
                    "notes": custom_notes
                }
                st.session_state.tasks.insert(0, new_task)
                st.session_state.last_api_payload = payload

                # 3. Záznam do GIST Controllingu (Oddělený odhad nákladů od schválení)
                st.session_state.gist_df, _ = add_warranty_record(
                    st.session_state.gist_df,
                    case_id=new_case["case_id"],
                    boiler_model=selected_model,
                    serial_number=serial_no,
                    lot=lot_no,
                    component=err_data["component"],
                    part_cost=err_data["unit_cost_czk"],
                    labor_cost=new_case["estimated_labor_cost"],
                    fault_reason=f"Diagnostika {err_selection}: {custom_notes[:35]}..."
                )
                
                st.balloons()
                st.success(
                    f"🚨 **Založen servisní případ `{new_case['case_id']}` s provázanou eskalací!**\n\n"
                    f"1. **Projektově.cz:** Vytvořen úkol `{task_id}` pro expedici náhradního dílu `{err_data['part_number']}`.\n"
                    f"2. **GIST Controlling:** Zaevidován indikativní odhad nákladů {err_data['unit_cost_czk'] + new_case['estimated_labor_cost']} Kč "
                    f"(status: *Čeká na posouzení garance*).\n\n"
                    f"*Data jsou provázána přes Case ID. Prozkoumejte záložky 2 a 3.*"
                )
                st.rerun()

        if already_resolved and existing_case:
            st.info(
                f"ℹ️ **Případ pro kotel `{serial_no}` a vadu `{err_selection}` byl již úspěšně uzavřen na místě** "
                f"pod identifikátorem **`{existing_case['case_id']}`**.\n\n"
                f"*Tlačítka jsou uzamčena pro zamezení vícenásobného odeslání (idempotence). "
                f"Pro evidenci dalšího případu zadejte jiné výrobní číslo nebo vyberte jiný kód závady.*"
            )
        elif already_escalated and existing_case:
            st.warning(
                f"⚠️ **Pro kotel `{serial_no}` a vadu `{err_selection}` již existuje otevřený servisní úkol** "
                f"v Projektově.cz: **`{existing_case.get('task_id', 'PRJ-TASK')}`** (Případ: `{existing_case['case_id']}`).\n\n"
                f"*Případ je v řešení, duplicitní požadavek je blokován.*"
            )

        # --- PŘEHLED NAVRŽENÝCH UPGRADŮ (PRODUKČNÍ ROZVOJ) ---
        st.markdown("---")
        with st.expander("🚀 Plánované rozšíření pro plnou verzi (Technologické & procesní upgrady)", expanded=True):
            st.markdown(
                """
                * 📷 **OCR / QR sken štítku kotle:** Vyfocení výrobního čísla mobilem — automatické dotažení modelu, šarže, historie a stavu záruky z ERP bez ručního zadávání.
                * 🔑 **Automatická identifikace technika (SSO login):** Žádný ruční výběr partnera; systém ověří platnost akreditace pro daný kotel a předvyplní dodací adresu skladu.
                * 📚 **RAG model („Kotelní knihovník“):** Vyhledávání v dokumentaci i z volného popisu technika s přesným proklikem na stránku a schéma v PDF manuálu.
                * 👥 **Dvouúrovňový režim (Guest vs. Serviceman):**
                    * *Guest (koncový zákazník):* Omezeno na bezpečné úkony (čištění, tlak vody) + tlačítko „Objednat spádový servis“.
                    * *Serviceman (technik):* Plný přístup ke schématům svorkovnic, měření odporů a objednávce dílů.
                * 🌍 **Vícejazyčnost (CZ / PL / EN):** Klíčové pro export a polského výrobce regulací Plum — technik píše v rodném jazyce, systém unifikuje kódy dílů pro sklad v Trnávce.
                """
            )

    else:
        # ======================================================================
        # ZÁKAZNICKÝ REŽIM (L0 SELF-SERVICE / VIZUÁLNÍ MIKRONÁVODY)
        # ======================================================================
        st.markdown("### 👤 Vizuální asistent obsluhy kotle (QR Self-Service pro zákazníka)")
        st.caption(
            "Laický průvodce běžnou obsluhou přímo v kotelně. V produkční verzi jsou rozpadová schémata "
            "a vizuální mikronávody automatizovaně generovány přímo z 3D CAD modelů v **SOLIDWORKS Composer**."
        )

        col_sel1, col_sel2 = st.columns([1.2, 1.8])
        with col_sel1:
            cust_panel = st.radio(
                "1. Modelová řada / panel kotle:",
                [
                    "🔥 BLAZE HARMONY & COMFORT (Dotykový panel ecoMAX 860D3)",
                    "🔥 BLAZE PRAKTIK EASY (Otočný regulátor ecoMAX 800D)"
                ]
            )
        with col_sel2:
            if "860D3" in cust_panel:
                act = st.radio(
                    "2. Co potřebujete na kotli provést:",
                    [
                        "👆 Zapnutí regulace a start roztopu (Dotyková obrazovka)",
                        "🟠 Práce s masivním přikládacím madlem a horní klapkou",
                        "🚨 Hlášení poruchy na displeji (Objednat spádový servis)"
                    ]
                )
            else:
                act = st.radio(
                    "2. Co potřebujete na kotli provést:",
                    [
                        "🔘 Zapnutí regulace otočným knoflíkem (Start kotle)",
                        "💧 Kontrola tlaku v otopném systému (Manometr)",
                        "🚨 Hlášení poruchy (Objednat spádový servis)"
                    ]
                )

        st.markdown("---")

        if "860D3" in cust_panel:
            if "Dotyková obrazovka" in act:
                col_v1, col_v2 = st.columns(2)
                with col_v1:
                    st.markdown("##### 1. Celkový pohled na těleso a panel")
                    st.image(
                        "assets/blaze_real_860d3_top_handle.png",
                        caption="Horní panel BLAZE HARMONY s displejem Plum ecoMAX 860D3 a bezpečnostním madlem",
                        use_container_width=True
                    )
                with col_v2:
                    st.markdown("##### 2. Detailní zásah prstem na displeji")
                    st.image(
                        "assets/blaze_real_860d3_touch_on.png",
                        caption="Klepnutí prstem na tlačítko se symbolem fajfky [ANO]: dialog 'Zapnout regulátor?'",
                        use_container_width=True
                    )

                st.markdown(
                    """
                    <div class='blaze-diag-card'>
                        <strong>🎬 Postup krok za krokem:</strong><br>
                        1. Na dotykovém displeji svítí dialogové okno <code>Zapnout regulátor?</code>.<br>
                        2. <strong>Klepněte prstem přímo na tlačítko se symbolem fajfky [ANO]</strong> na levé straně okna (viz foto 2).<br>
                        3. Regulátor okamžitě aktivuje odtahový ventilátor a přejde do fáze rozpalování a řízení spalování.
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                if st.button("✅ Klepnuto na [ANO] — regulátor zapnut!", use_container_width=True):
                    st.success("🎉 Regulátor ecoMAX 860D3 je aktivní, ventilátor nabíhá do provozních otáček.")

            elif "přikládacím madlem" in act:
                col_v1, col_v2 = st.columns([1.2, 1.8])
                with col_v1:
                    st.image(
                        "assets/blaze_real_860d3_top_handle.png",
                        caption="Masivní oranžová hrazda pro přikládání paliva a přímý odtah kouře",
                        use_container_width=True
                    )
                with col_v2:
                    st.markdown(
                        """
                        <div class='blaze-diag-card'>
                            <strong>Obsluha oranžového bezpečnostního madla:</strong><br>
                            • Masivní oranžová hrazda slouží k otevření horní komory a automatickému otevření přímé odtahové klapky do komína.<br>
                            • <strong>Před přiložením:</strong> Plynule zatáhněte za oranžové madlo směrem k sobě. Vyčkejte 5 vteřin, než odtahový ventilátor odsaje zbytkový kouř do komína.<br>
                            • <strong>Po naložení:</strong> Madlo zaklopte zpět až do zacvaknutí západky.
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    if st.button("✅ Madlo zkontrolováno a dovřeno", use_container_width=True):
                        st.success("🎉 Horní komora je hermeticky uzavřena, tah kotle směřuje přes zplyňovací trysku.")

            else:
                st.markdown(
                    """
                    <div style='background: rgba(239, 68, 68, 0.1); border-left: 4px solid #ef4444; padding: 16px; border-radius: 6px; margin-bottom: 16px;'>
                        <strong style='color: #ef4444; font-size: 1.05rem;'>🛑 Bezpečnostní pravidlo BLAZE HARMONY:</strong><br>
                        Při chybových kódech elektroniky, lambda sondy nebo ventilátoru <strong>nikdy nerozebírejte opláštění kotle sami!</strong>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                col_s1, col_s2 = st.columns([1.5, 1.5])
                with col_s1:
                    st.markdown(
                        """
                        * 🏢 **Přiřazený akreditovaný partner:** *Instalatérství Kovář & Syn (Valašské Meziříčí)*  
                        * 📞 **Pohotovostní garanční linka:** +420 777 123 456  
                        * ⏱️ **Garantovaná reakce v sezóně:** do 4 hodin  
                        """
                    )
                with col_s2:
                    if st.button("🚨 Odeslat servisní požadavek spádovému partnerovi", type="primary", use_container_width=True):
                        st.success("📬 **Servisní požadavek byl odeslán.** Akreditovaný servis byl notifikován a ozve se vám pro domluvení termínu.")

        else:
            # Řada BLAZE PRAKTIK EASY s regulací ecoMAX 800D
            if "otočným knoflíkem" in act:
                col_v1, col_v2 = st.columns(2)
                with col_v1:
                    st.markdown("##### 1. Panel v klidovém stavu")
                    st.image(
                        "assets/blaze_real_800d_rotary_idle.png",
                        caption="Panel BLAZE PRAKTIK EASY (ecoMAX 800D): zobrazení '09:18:30 Kotel Vypnut'",
                        use_container_width=True
                    )
                with col_v2:
                    st.markdown("##### 2. Zásah prstem na otočném knoflíku")
                    st.image(
                        "assets/blaze_real_800d_rotary_confirm.png",
                        caption="Stisknutí středu otočného enkodéru na volbě 'Zapnout regulaci? ANO'",
                        use_container_width=True
                    )

                st.markdown(
                    """
                    <div class='blaze-diag-card'>
                        <strong>🎬 Postup pro řadu PRAKTIK EASY (ecoMAX 800D):</strong><br>
                        1. Displej ukazuje <code>Kotel Vypnut</code>.<br>
                        2. <strong>Stiskněte černý otočný knoflík</strong> jednou pro vstup do rychlého menu.<br>
                        3. Na dotaz <code>Zapnout regulaci?</code> otočte knoflík na volbu <strong>ANO</strong> a <strong>stiskněte střed knoflíku</strong> (viz foto 2).<br>
                        4. Zelená kontrolka sepne a kotel zahájí odtah spalin.
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                if st.button("🔘 Stisknuto ANO na otočném knoflíku", use_container_width=True):
                    st.success("🎉 Regulátor ecoMAX 800D spuštěn. Na displeji se zobrazí aktuální teplota kotle.")

            elif "Kontrola tlaku" in act:
                st.markdown(
                    """
                    <div class='blaze-diag-card'>
                        <strong>Kontrola provozního tlaku:</strong><br>
                        • Správný tlak za studena: <strong>1,5 až 2,0 bar</strong>.<br>
                        • Pokud ručička klesne pod 1,2 bar, doplňte otopnou vodu dopouštěcím ventilem v kotelně na 1,6 bar.
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                if st.button("💧 Tlak zkontrolován", use_container_width=True):
                    st.success("🎉 Tlak vody v systému je v optimálním rozmezí.")

            else:
                st.markdown(
                    """
                    <div style='background: rgba(239, 68, 68, 0.1); border-left: 4px solid #ef4444; padding: 14px; border-radius: 6px; margin-bottom: 14px;'>
                        <strong style='color: #ef4444;'>🛑 Bezpečnostní upozornění:</strong><br>
                        Při poruše čidla spalin nebo ventilátoru volejte akreditovaný servis. 
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                if st.button("🚨 Odeslat požadavek akreditovanému servisu", type="primary", use_container_width=True):
                    st.success("📬 **Servisní požadavek odeslán spádovému partnerovi BLAZE HARMONY.**")


# ==============================================================================
# TAB 2: PROJEKTOVĚ.CZ (OPERATIVA, TIKETY & NÁVRH REST API)
# ==============================================================================
with tab_proj:
    st.markdown("### 📋 Projektově.cz: Simulace operativy a zakládání úkolů")
    st.info(
        "💡 **Poznámka k integraci:** Toto rozhraní představuje **simulaci toku dat a návrh integračního kontraktu**. "
        "Konkrétní parametry a autorizační schéma budou předmětem technické specifikace s IT týmem p. Václava Hlobila."
    )
    
    tasks_df = pd.DataFrame(st.session_state.tasks)
    
    col_t1, col_t2, col_t3, col_t4 = st.columns(4)
    col_t1.metric("Celkem evidovaných úkolů", len(tasks_df))
    col_t2.metric("K expedici náhradního dílu", len(tasks_df[tasks_df["status"].str.contains("Nový", na=False)]))
    col_t3.metric("Probíhající montáž v terénu", len(tasks_df[tasks_df["status"] == "V řešení"]))
    col_t4.metric("Dynamické SLA plnění", f"{dynamic_sla_pct} %", help="Vypočteno z reálných záznamů úkolů")
    
    st.markdown("#### 📑 Přehled servisních úkolů v Projektově.cz")
    
    # Tabulka s provázáním na Case ID
    display_tasks = tasks_df[[
        "case_id", "id", "priority", "status", "title", "boiler_model", "serial_number", "part_name", "part_number", "partner_name", "due_date"
    ]].copy()
    display_tasks.columns = [
        "Case ID", "ID úkolu", "Priorita", "Stav", "Název úkolu", "Model kotle", "Výrobní číslo", "Název dílu", "Katalogové číslo ND", "Servisní partner", "Termín (SLA)"
    ]
    
    st.dataframe(display_tasks, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Technický JSON ve sbalovací sekci
    with st.expander("💻 Návrh datového kontraktu pro REST API Projektově.cz (Vstupní payload z terénu)", expanded=False):
        st.caption("Předmět ověření: `POST https://api.projektove.cz/v1/projects/4820/tasks` (Vstupní tok z diagnostiky do úkolu)")
        if st.session_state.last_api_payload:
            st.json(st.session_state.last_api_payload)
        else:
            sample_payload = create_task_payload(
                "CASE-2026-0042", "BLAZE COMFORT 30", "BH-2025-0112", "2025-Q1",
                "E-12", ERROR_CODES["E-12"], "Topení Morava s.r.o.", "Olomouc",
                "Vzorek datového kontraktu před odesláním nového požadavku."
            )
            st.json(sample_payload)

    # Procesní tahák a architektura toku dat
    with st.expander("🚀 Procesní architektura: Proč Projektově.cz a návaznost na ERP sklad (Fáze 1 ➔ Fáze 2)", expanded=True):
        st.markdown(
            """
            * 📥 **Vstup z terénu (Tento PoC):** Data z diagnostiky technika tečou přes REST API přímo do **Projektově.cz** — vytvoří se úkol s Case ID, katalogovým kódem dílu a automatickým SLA.
            * 🛡️ **Schvalovací brána (Approval Gate):** Projektově.cz slouží jako bezpečnostní filtr. Externí montážník nemůže „jen tak“ automaticky vyskladnit díl za tisíce Kč. Dispečer v Trnávce posoudí nárok a stav záruky.
            * 📤 **Výstup do ERP / WMS skladu (Cílová Fáze 2):** Jakmile dispečer v Projektově.cz přepne stav na *„Schváleno k expedici“*, **automatický Webhook** vytvoří rezervaci/výdejku přímo v **HELIOS iNuvio (modul WMS)** a vytiskne štítek pro přepravce.
            * 🔄 **Reverzní logistika (Zpětná vazba):** Součástí úkolu v Projektově.cz je i pokyn pro technika: vrátit vadný díl v krabici zpět do BLAZE na posouzení pro uplatnění refundace u dodavatele (viz záložka 3 - GIST).
            """
        )


# ==============================================================================
# TAB 3: GIST CONTROLLING & BI (ZÁRUKY, PARETO & KVALITA)
# ==============================================================================
with tab_gist:
    st.markdown("### 📊 GIST Controlling: Analýza garančních nákladů a kvality dodávek")
    st.info(
        "💡 **Poznámka ke controllingu:** GIST je páteřní systém pro kalkulace a controlling BLAZE HARMONY. "
        "Aplikace rozlišuje mezi *indikativním odhadem nahlášené záruky* a *skutečně schváleným a zaúčtovaným nákladem*."
    )
    
    df_g = st.session_state.gist_df.copy()
    
    approved_costs = df_g[df_g["warranty_status"].str.contains("Uznáno", na=False)]["actual_cost"].sum()
    pending_estimates = df_g[df_g["warranty_status"] == "Čeká na posouzení garance"]["total_estimated_cost"].sum()
    supplier_refunds = df_g[df_g["warranty_status"].str.contains("Refund", na=False)]["actual_cost"].sum()
    
    # Výpočet First-Time Fix Rate z Case Manageru
    total_cases = len(st.session_state.cases)
    first_time_fix_count = len([c for c in st.session_state.cases if c.get("resolution_type") == "Vyřešeno v terénu (Self-Service)"])
    ftf_rate = round((first_time_fix_count / total_cases) * 100.0, 1) if total_cases > 0 else 0.0

    col_g1, col_g2, col_g3, col_g4 = st.columns(4)
    col_g1.metric("Schválené záruční náklady", f"{approved_costs:,.0f} Kč".replace(",", " "), help="Skutečně zaúčtované záruky po posouzení")
    col_g2.metric("Otevřené odhady v řešení", f"{pending_estimates:,.0f} Kč".replace(",", " "), help="Nové případy čekající na uznání záruky a vyúčtování")
    col_g3.metric("Uplatněné refundy u dodavatelů", f"{supplier_refunds:,.0f} Kč".replace(",", " "), help="Částka nárokovaná zpět u výrobců komponent (např. Bosch)")
    col_g4.metric("First-Time Fix Rate", f"{ftf_rate} %", f"{first_time_fix_count} z {total_cases} případů", help="Podíl případů vyřešených v terénu bez vzniku nákladů")

    st.markdown("---")
    
    col_ch1, col_ch2 = st.columns(2)
    
    with col_ch1:
        st.markdown("##### 📈 Skutečná Paretova analýza nákladů dle komponent (80/20)")
        pareto_df = prepare_pareto_data(df_g)
        
        # Vytvoření kombinovaného Paretova grafu (Sloupce + Kumulativní křivka %)
        fig_pareto = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Sloupce nákladů
        fig_pareto.add_trace(
            go.Bar(
                x=pareto_df["component"],
                y=pareto_df["total_estimated_cost"],
                name="Náklady dílu (Kč)",
                marker_color="#f26522",
                text=pareto_df["total_estimated_cost"],
                textposition="auto"
            ),
            secondary_y=False
        )
        
        # Kumulativní čára procent
        fig_pareto.add_trace(
            go.Scatter(
                x=pareto_df["component"],
                y=pareto_df["cum_pct"],
                name="Kumulativní podíl (%)",
                mode="lines+markers",
                line=dict(color="#1e293b", width=2.5),
                marker=dict(size=7)
            ),
            secondary_y=True
        )
        
        # 80% referenční linka
        fig_pareto.add_hline(y=80, line_dash="dash", line_color="#ef4444", secondary_y=True, annotation_text="80% hranice")
        
        fig_pareto.update_layout(
            height=320,
            margin=dict(l=10, r=10, t=20, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        fig_pareto.update_yaxes(title_text="Náklady celkem (Kč)", secondary_y=False)
        fig_pareto.update_yaxes(title_text="Kumulativní %", range=[0, 105], secondary_y=True)
        st.plotly_chart(fig_pareto, use_container_width=True)
        st.caption("Paretovo pravidlo: Primární fokus jednání o garancích s dodavateli směřuje na položky do 80 % celkových vícenákladů.")

    with col_ch2:
        c_th1, c_th2 = st.columns([1.1, 1.9])
        with c_th1:
            st.markdown("##### 📊 Nákladovost modelových řad")
        with c_th2:
            model_view_mode = st.radio(
                "Pohled na nákladovost:",
                [
                    "Kč / prodaný kus (Relativní)",
                    "Absolutní náklady (Kč)",
                    "Podíl z tržeb (%)"
                ],
                horizontal=True,
                index=0,
                label_visibility="collapsed"
            )

        model_metrics = calculate_model_relative_metrics(df_g)

        if model_view_mode.startswith("Kč"):
            # Relativní jednotkový náklad na prodané těleso
            fig_model = px.bar(
                model_metrics,
                x="model",
                y="cost_per_sold_unit",
                text="cost_per_sold_unit",
                labels={"cost_per_sold_unit": "Záruční náklad (Kč / ks)", "model": "Model kotle"},
                color="cost_per_sold_unit",
                color_continuous_scale=["#10b981", "#f59e0b", "#ef4444"]
            )
            fig_model.update_traces(texttemplate='%{text:.1f} Kč/ks', textposition='outside')
            fig_model.add_hline(
                y=50, line_dash="dash", line_color="#ef4444",
                annotation_text="Interní limit: 50 Kč/ks", annotation_position="top right"
            )
            fig_model.update_layout(
                height=310,
                margin=dict(l=10, r=10, t=25, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                coloraxis_showscale=False
            )
            fig_model.update_yaxes(title_text="Kč na prodané těleso", range=[0, max(float(model_metrics["cost_per_sold_unit"].max()) * 1.35, 60.0)])
            st.plotly_chart(fig_model, use_container_width=True)
            st.caption(
                "🎯 **Controllingový vhled:** Všechny modely plní limit do 50 Kč/ks. "
                "**BLAZE PRAKTIK EASY** (15,2 Kč/ks) dokazuje, že odlehčená konstrukce nezvýšila servisní náročnost. "
                "Vyšší náklad u **BLAZE COMFORT** (27,2 Kč/ks) odpovídá odtahovému ventilátoru a samočisticí mechanice."
            )

        elif model_view_mode.startswith("Absolutní"):
            # Původní absolutní součet
            fig_model = px.bar(
                model_metrics,
                x="model",
                y=["actual_cost", "total_estimated_cost"],
                barmode="group",
                labels={"value": "Částka v Kč", "model": "Model kotle", "variable": "Typ nákladu"},
                color_discrete_map={"actual_cost": "#10b981", "total_estimated_cost": "#f59e0b"}
            )
            fig_model.update_layout(
                height=310,
                margin=dict(l=10, r=10, t=15, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            fig_model.update_yaxes(title_text="Celkové náklady (Kč)")
            st.plotly_chart(fig_model, use_container_width=True)
            st.caption("Absolutní součty nákladů. Pozor na zkreslení objemem: nejprodávanější model logicky kumuluje vyšší absolutní sumu.")

        else:
            # Podíl z tržeb (%)
            fig_model = px.bar(
                model_metrics,
                x="model",
                y="warranty_share_pct",
                text="warranty_share_pct",
                labels={"warranty_share_pct": "Záruky z tržeb (%)", "model": "Model kotle"},
                color="warranty_share_pct",
                color_continuous_scale=["#10b981", "#3b82f6", "#f59e0b"]
            )
            fig_model.update_traces(texttemplate='%{text:.3f} %', textposition='outside')
            fig_model.add_hline(
                y=0.10, line_dash="dash", line_color="#ef4444",
                annotation_text="Toleranční mez: 0,10 % tržeb", annotation_position="top right"
            )
            fig_model.update_layout(
                height=310,
                margin=dict(l=10, r=10, t=25, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                coloraxis_showscale=False
            )
            fig_model.update_yaxes(title_text="% z celkových tržeb", range=[0, max(float(model_metrics["warranty_share_pct"].max()) * 1.4, 0.12)])
            st.plotly_chart(fig_model, use_container_width=True)
            st.caption("Podíl garančních nákladů na tržbách modelové řady. Průmyslový standard v oboru vytápění bývá pod 1,0 % tržeb.")

    # Detekce a evidence výrobních šarží a kvality subdodavatelů
    st.markdown("#### 🔍 Sledování výrobních šarží a kvality subdodavatelů (Vendor Quality & Risk Rating)")
    st.caption(
        "Automatický reporting zmetkovitosti a reklamovanosti nakupovaných komponent. "
        "Propojuje terénní servisní záznamy s nákupními šaržemi v **HELIOS iNuvio (WMS)** a kalkulacemi v **GIST**."
    )

    supp_report = calculate_supplier_quality_report(df_g)

    # 1. Zobrazení kritických upozornění pro controlling a nákup
    crit_rows = supp_report[supp_report["defect_rate_pct"] >= 4.0]
    if not crit_rows.empty:
        for _, cr in crit_rows.iterrows():
            st.error(
                f"🚨 **KRITICKÝ VENDOR RISK:** Dodavatel **{cr['supplier']}** | "
                f"Díl: **{cr['component']}** | Šarže: **{cr['lot']}**\n\n"
                f"• **Míra reklamovanosti: `{cr['defect_rate_pct']} %`** ({cr['defect_count']} vady ze {cr['delivered_qty']} dodaných kusů v šarži — limit je 2.0 %)\n"
                f"• **Finanční dopad:** {cr['total_cost']:,.0f} Kč celkem (z toho nárokováno jako refund: {cr['refund_cost']:,.0f} Kč)\n"
                f"• 🎯 **Doporučená manažerská opatření pro nákup a controlling:**\n"
                f"  1. **Zádržné:** Pozastavit uvolnění zádržného z faktur dodavatele {cr['supplier']}.\n"
                f"  2. **100% refundace:** Vymáhat nejen cenu dílu (3 200 Kč/ks), ale i čas technika v terénu (600 Kč/výjezd).\n"
                f"  3. **WMS příjem v Trnávce:** Nastavit v HELIOS iNuvio WMS blokaci na naskladnění dalších kusů z této šarže."
            )
    else:
        st.success("Žádná výrobní šarže ani dodavatel aktuálně nepřekračují kritický limit zmetkovitosti (4.0 %).")

    # 2. Rychlé KPI metriky kvality dodávek
    col_sq1, col_sq2, col_sq3, col_sq4 = st.columns(4)
    with col_sq1:
        top_risk = supp_report.iloc[0] if not supp_report.empty else None
        if top_risk is not None:
            st.metric(
                "Nejvyšší zmetkovitost šarže",
                f"{top_risk['defect_rate_pct']} %",
                f"{top_risk['supplier'][:16]}.. ({top_risk['lot']})",
                delta_color="inverse",
                help="Nejvyšší relativní podíl reklamovaných dílů vůči dodanému množství v šarži."
            )
    with col_sq2:
        refund_total = supp_report["refund_cost"].sum()
        st.metric(
            "Vymožené refundace u dodavatelů",
            f"{refund_total:,.0f} Kč".replace(",", " "),
            "100 % uplatněno",
            help="Částky, které BLAZE HARMONY neplatí ze svého, ale přenesla je na subdodavatele."
        )
    with col_sq3:
        avg_defect = round(supp_report["defect_rate_pct"].mean(), 1) if not supp_report.empty else 0.0
        st.metric(
            "Průměrná reklamovanost portfolia",
            f"{avg_defect} %",
            "Referenční benchmark",
            help="Průměrná míra reklamací napříč všemi sledovanými komponentami a šaržemi."
        )
    with col_sq4:
        st.metric(
            "Sledovaných kombinací díl/šarže",
            len(supp_report),
            "Párováno na HELIOS WMS",
            help="Počet unikátních dodavatelských sérií evidovaných v centrálním DWH."
        )

    # 3. Interaktivní tabulka Vendor Quality Scorecard
    display_sq = supp_report[[
        "risk_badge", "supplier", "component", "lot", "delivered_qty",
        "defect_count", "defect_rate_pct", "total_cost", "refund_cost", "action"
    ]].copy()
    display_sq.columns = [
        "Stav", "Dodavatel", "Komponenta", "Šarže", "Dodáno (ks)",
        "Reklamováno (ks)", "Reklamovanost (%)", "Náklad celkem (Kč)", "Uplatněný refund (Kč)", "Doporučené opatření"
    ]
    st.dataframe(display_sq, use_container_width=True, hide_index=True)

    with st.expander("💡 Jak tato data pomáhají při vyjednávání s dodavateli (Controlling & Purchasing)", expanded=False):
        st.markdown(
            """
            * 📊 **Tvrdá data pro vyjednávání o cenách a zárukách:** Místo dojmů typu *„ty lambdy od Bosche nějak často odchází“* má nákupní oddělení v ruce přesná čísla: *„V šarži 2025-Q3 máme reklamovanost 6,7 %, což je 3× nad smluvním limitem.“*
            * 🔄 **Automatická reverzní logistika:** Technik v terénu zabalí vadný díl do krabice od nového dílu, vygeneruje štítek z Projektově.cz a díl se vrací do BLAZE k fyzické expertíze pro subdodavatele.
            * 🛡️ **Ochrana marže kotlů:** Pokud subdodavatel uzná refundaci, náklad se nepodepíše na marži prodaného kotle v GIST Controllingu.
            """
        )

    # Staging tabulka GIST
    with st.expander("📥 Staging tabulka pro GIST DWH (Surová data s Case ID)", expanded=False):
        st.dataframe(df_g, use_container_width=True)
        csv_data = df_g.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="💾 Stáhnout CSV export pro GIST Controlling",
            data=csv_data,
            file_name="gist_warranty_staging_blaze.csv",
            mime="text/csv"
        )


# ==============================================================================
# TAB 4: PROCES A PŘÍNOSY (PILOTNÍ PROJEKT)
# ==============================================================================
with tab_arch:
    st.markdown("### 🧭 Proces a přínosy (Pilotní projekt)")
    st.caption("Metodický rámec procesní transformace a interaktivní model návratnosti pro vedení BLAZE HARMONY s.r.o.")
    
    c_m1, c_m2 = st.columns([1.5, 1.5])
    
    with c_m1:
        st.markdown("#### 🔄 Návrh toku procesu (End-to-End)")
        st.markdown(
            """
            ```
            [SOLIDWORKS Composer & 3DEXPERIENCE]
                        │  (3D rozstřely & vizuální manuály)
                        ▼
            [Blaze Core Hub: Technik / Zákazník]
                        │
             ┌──────────┴──────────┐
             ▼                     ▼
      [Vyřešeno na místě]   [Potvrzena vadná součástka]
       (First-Time Fix)            │
                        (Založení Case ID: CASE-2026-xxxx)
                                   │
                         ┌─────────┴─────────┐
                         ▼                   ▼
                 [Projektově.cz]       [GIST Controlling]
                 - Schvalovací brána   - Indikativní odhad
                 - SLA dispečinku      - Posouzení garance
                         │             - Paretova analýza
                         ▼ (Webhook)   - Refundy dodavatelů
                 [HELIOS iNuvio (WMS)]
                 - Rezervace dílu v Trnávce
                 - Tisk expedičního štítku
            ```
            """
        )
        
        st.markdown("#### 🎯 Role Transformation & Process Managera")
        st.markdown(
            """
            * **Procesní čistota místo izolovaných sil:** Propojení existujících investic — **SOLIDWORKS Composer** (3D data) ➔ **Projektově.cz** (operativa & schvalování) ➔ **HELIOS iNuvio WMS** (sklad & expedice) ➔ **GIST** (controlling & marže).
            * **Respekt ke stávajícím nástrojům:** Žádný nákup dalšího těžkopádného systému za miliony. Využití otevřených API a webhooků k automatizaci rutiny.
            * **Podpora selektivní distribuce:** Nástroj slouží jako prémiová podpora certifikované montážní a servisní sítě, kterou BLAZE HARMONY koncem roku 2025 zavedla.
            """
        )

        with st.expander("🏛️ Mapování podnikového ekosystému BLAZE HARMONY s.r.o.", expanded=False):
            st.markdown(
                """
                | Podniková doména | Ověřený systém v BLAZE | Úloha v procesním Hubu |
                | :--- | :--- | :--- |
                | **Konstrukce & PDM** | **SOLIDWORKS & 3DEXPERIENCE** | Zdroj 3D modelů, technických dat a kusovníků (BOM). |
                | **Tvorba manuálů** | **SOLIDWORKS Composer** | Automatizovaný export 3D rozpadů a vizuálních mikronávodů. |
                | **ERP & Sklad** | **HELIOS iNuvio (WMS)** | Skladové hospodářství v Trnávce, automatická rezervace dílů. |
                | **Operativa & Dispečink**| **Projektově.cz** | Evidence servisních incidentů, schvalovací brána a SLA. |
                | **Controlling & BI** | **GIST Controlling** | Sledování marží, Paretova analýza vad (80/20) a refundy subdodavatelů. |
                """
            )
            st.image(
                "assets/blaze_solidworks_toptech.png",
                caption="Referenční případová studie: BLAZE HARMONY s.r.o. — SOLIDWORKS Composer & 3DEXPERIENCE (Zdroj: TOP TECH s.r.o.)",
                use_container_width=True
            )

    with c_m2:
        st.markdown("#### 💰 Interaktivní simulační model přínosů (ROI)")
        st.caption("Upravte posuvníky podle skutečných parametrů provozu pro kalkulaci očekávaných úspor:")
        
        inquiries_month = st.slider("Počet servisních dotazů / incidentů měsíčně:", min_value=50, max_value=800, value=250, step=25)
        avg_call_min = st.slider("Průměrná doba řešení dotazu dispečinkem (minuty):", min_value=10, max_value=45, value=25, step=5)
        self_service_pct = st.slider("Očekávaný podíl dotazů vyřešených v terénu přes portál (%):", min_value=10, max_value=70, value=35, step=5)
        hourly_rate_support = st.slider("Hodinová nákladová sazba technické podpory (Kč/hod):", min_value=300, max_value=800, value=450, step=25)
        monthly_ops_cost = st.slider("Předpokládané měsíční náklady na provoz řešení (Kč/měsíc):", min_value=1000, max_value=10000, value=3000, step=500)

        # Výpočty modelu
        resolved_inquiries = inquiries_month * (self_service_pct / 100.0)
        hours_saved_month = (resolved_inquiries * avg_call_min) / 60.0
        gross_monthly_savings = hours_saved_month * hourly_rate_support
        net_monthly_savings = gross_monthly_savings - monthly_ops_cost
        annual_net_savings = net_monthly_savings * 12

        st.markdown("---")
        st.markdown("##### 📈 Výsledky simulačního modelu:")
        
        c_r1, c_r2 = st.columns(2)
        c_r1.metric("Ušetřená kapacita podpory", f"{hours_saved_month:,.0f} hod/měsíc".replace(",", " "))
        c_r1.metric("Dotazů vyřešených v terénu", f"{resolved_inquiries:,.0f} / měsíc".replace(",", " "))
        c_r2.metric("Čistá měsíční úspora", f"{net_monthly_savings:,.0f} Kč".replace(",", " "))
        c_r2.metric("Čistý roční finanční přínos", f"{annual_net_savings:,.0f} Kč".replace(",", " "))

    st.markdown("---")
    st.markdown("#### 🚀 Navržený plán realizace pilotního projektu (3 měsíce)")
    
    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
        st.markdown("**1. Měsíc: Příprava & Kontrakt**")
        st.markdown(
            """
            * Validace datového kontraktu s p. Hlobilem.
            * Výběr 5 klíčových partnerů selektivní sítě.
            * Revize diagnostických postupů s technickým ředitelem.
            """
        )
    with col_p2:
        st.markdown("**2. Měsíc: Řízený pilot v terénu**")
        st.markdown(
            """
            * Nasazení pro vybrané partnery.
            * Sledování First-Time Fix Rate.
            * Měření reálné úspory času technické podpory.
            """
        )
    with col_p3:
        st.markdown("**3. Měsíc: Vyhodnocení & Škálování**")
        st.markdown(
            """
            * Vyhodnocení Paretova rozpadu vad v GISTu.
            * Schválení plného rolloutu na celou síť.
            * Předání správy procesnímu týmu.
            """
        )

st.markdown("---")
st.caption("BLAZE HARMONY s.r.o. | Metodický a procesní prototyp pro výběrové řízení Transformation & Process Manager")
