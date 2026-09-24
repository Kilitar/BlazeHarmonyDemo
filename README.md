# 🔥 Blaze Core Hub (v2.0)
> **Procesní a diagnostický prototyp pro BLAZE HARMONY s.r.o.**  
> Připraveno pro pozici *Transformation & Process Manager*.

Funkční simulace a architektonický demonstrátor propojení:
**Terénní servis (B2B síť montážníků)** ➔ **Projektově.cz (Operativní řízení & REST API)** ➔ **HELIOS iNuvio (WMS / Sklad)** ➔ **GIST (Controlling & Garance)**.

---

## 🏛️ Klíčové součásti prototypu

1. **📱 1. Terénní diagnostika (Technik / Zákazník):**
   * Role-based přístup: **Servisní režim** (akreditovaný montážník) vs. **Zákaznický režim** (L0 Self-Service).
   * Validace modelových řad (*BLAZE HARMONY, PRAKTIK EASY, COMFORT, NATURAL PLUS*).
   * Vizuální manuály a mikronávody pro regulátory **ecoMAX 860D3** a **ecoMAX 800D** (napojení na SOLIDWORKS Composer).
   * Unifikované zakládání servisních incidentů s globálním `Case ID`.

2. **📋 2. Projektově.cz (Operativa, Schvalovací brána & API):**
   * Simulace dispečinku a správy úkolů.
   * **Approval Gate:** Ochrana před neoprávněným čerpáním dílů ze skladu.
   * Návrh JSON datového kontraktu pro REST API.
   * Dynamický výpočet SLA a plánované napojení Webhooku do **HELIOS iNuvio (modul WMS)**.

3. **📊 3. GIST Controlling & BI (Záruky & Kvalita):**
   * Oddělení indikativních odhadů od schválených a zaúčtovaných nákladů.
   * Skutečná Paretova analýza nákladovosti komponent (pravidlo 80/20).
   * **Multi-view nákladovost modelů:** Absolutní náklady, jednotkový náklad na prodané těleso (Kč/ks) a podíl ze záručních tržeb (%).
   * **Vendor Quality & Risk Rating:** Sledování zmetkovitosti dodavatelů a výrobních šarží (Bosch, Sensors, EBM-Papst, FKK) a uplatňování refundací.

4. **🧭 4. Proces a přínosy (Pilotní projekt & ROI):**
   * End-to-End procesní mapa podnikového ekosystému.
   * Interaktivní simulační model návratnosti (ROI kalkulačka).
   * 90denní plán realizace pilotního projektu (3 fáze).

---

## 🚀 Rychlé spuštění (Local Run)

```bash
# 1. Klonování repozitáře
git clone <URL_REPOZITARE>
cd PoC_Blaze_Harmony

# 2. Vytvoření a aktivace virtuálního prostředí (doporučeno)
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux / macOS:
source venv/bin/activate

# 3. Instalace závislostí
pip install -r requirements.txt

# 4. Spuštění Streamlit aplikace
streamlit run app.py
```

Aplikace se otevře v prohlížeči na adrese `http://localhost:8501`.

---

## ☁️ Deployment na Streamlit Community Cloud

Aplikace je plně připravena pro nasazení do bezplatného **Streamlit Community Cloud**:
1. Nahrajte tento kód do svého GitHub účtu.
2. Přejděte na [share.streamlit.io](https://share.streamlit.io).
3. Zvolte **New app** -> vyberte svůj repozitář `PoC_Blaze_Harmony` a hlavní soubor `app.py`.
4. Během 2 minut získáte veřejný/soukromý odkaz použitelný na mobilu, tabletu i notebooku.
