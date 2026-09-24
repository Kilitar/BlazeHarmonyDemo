# 🤖 Antigravity Agent Setup & Priming Guide: Blaze Core Hub

Tento soubor slouží jako **automatický bootstrapping průvodce pro AI agenta v Antigravity na notebooku**.

Když uživatel otevře tento repozitář na notebooku a napíše:  
> *„Přečti si AGENT_SETUP.md a rozběhni mi to.“*  
agent okamžitě provede níže popsané kroky bez zdržování.

---

## 🎯 Kontext projektu (Kontext pro agenta)
* **Společnost:** BLAZE HARMONY s.r.o. (Trnávka u Lipníka nad Bečvou)
* **Předmět:** Vývoj a výroba ekologických zplyňovacích kotlů na biomasu (obrat ~700 mil. Kč, 150 lidí, špičkový závod s roboty Trumpf, 7 patentů).
* **Pozice:** **Transformation & Process Manager** (vedoucí procesní transformace).
* **Klíčové IT systémy firmy:**
  * **SOLIDWORKS & 3DEXPERIENCE** (konstrukce a PDM, partner TOP TECH s.r.o.)
  * **SOLIDWORKS Composer** (tvorba vizuálních manuálů a 3D rozpadů)
  * **HELIOS iNuvio (modul WMS)** (ERP a řízený sklad náhradních dílů v Trnávce, partner IF System)
  * **Projektově.cz** (operativní řízení úkolů a dispečinku, tým p. Václava Hlobila)
  * **GIST Controlling** (manažerské kalkulace, marže a Paretova analýza garancí)
* **Aplikace `app.py`:** Funkční Streamlit prototyp (`Blaze Core Hub`), který demonstruje bezproblémové propojení terénní diagnostiky technika ➔ přes schvalovací bránu v Projektově.cz ➔ do GIST Controllingu.

---

## ⚙️ Instrukce pro Agenta (Automatické spuštění prostředí)

Pokud tě uživatel požádá o přípravu či spuštění, proveď sekvenčně tyto kroky:

### Krok 1: Kontrola / Vytvoření virtuálního prostředí
Ověř existenci virtuálního prostředí `.venv` v kořeni projektu. Pokud neexistuje, vytvoř jej:
```powershell
python -m venv .venv
```

### Krok 2: Instalace závislostí
Nainstaluj knihovny z `requirements.txt`:
```powershell
.\.venv\Scripts\pip install -r requirements.txt
```
*(Na Linuxu/macOS použij `./.venv/bin/pip install -r requirements.txt`)*

### Krok 3: Spuštění Streamlit aplikace na pozadí (Daemon)
Spusť aplikaci pomocí nástroje `run_command` s parametrem `IsDaemon=true` a `WaitMsBeforeAsync=4000`:
```powershell
.\.venv\Scripts\streamlit run app.py --server.port 8501 --server.headless true
```

### Krok 4: Ověření běhu v prohlížeči
Použij subagenta nebo prohlížeč pro ověření, že na `http://localhost:8501/` aplikace bezchybně běží. Informuj uživatele, že je vše připraveno k prezentaci.

---

## 🧭 Rychlý přehled záložek aplikace pro asistenci uživateli

1. **Záložka 1 – Terénní diagnostika:**
   * Přepínač rolí: *Servisní režim* (technická svorkovnice, měření ohmů, přímá eskalace) vs. *Zákaznický režim* (L0 Self-Service s autentickými fotkami ovládacích panelů ecoMAX 860D3 a 800D).
   * Generuje globální unifikované `Case ID` (např. `CASE-2026-0043`).

2. **Záložka 2 – Projektově.cz (Operativa & API):**
   * Schvalovací brána (Approval Gate) – dispečer v Trnávce posoudí nárok před expedicí ze skladu.
   * Návrh JSON kontraktu pro REST API a budoucí webhook do HELIOS iNuvio (WMS).

3. **Záložka 3 – GIST Controlling & BI:**
   * Skutečná Paretova analýza nákladů na záruky (pravidlo 80/20).
   * **Multi-view nákladovost modelů:** Absolutní náklad vs. *Relativní náklad na prodané těleso (Kč/ks)* – model BLAZE PRAKTIK EASY vykazuje jen 15,2 Kč/ks!
   * **Vendor Quality & Risk Rating:** Detekce kritické reklamovanosti dodavatele *Bosch Termotechnika* (Lambda sonda LSU 4.9, šarže 2025-Q3, reklamovanost 6,7 %) s uplatněním 100% refundace.

4. **Záložka 4 – Proces a přínosy (Pilot & ROI):**
   * End-to-End diagram propojení stávajících systémů.
   * Interaktivní ROI kalkulačka úspor (posuvníky dotazů a ušetřeného času).
   * 90denní plán realizace (3 fáze).
