# AGENTS.md - Antigravity Workspace Context for BLAZE HARMONY PoC

## Projekt: Blaze Core Hub (v2.0)
Tento workspace obsahuje procesní a diagnostický prototyp připravený pro **BLAZE HARMONY s.r.o.** na pozici **Transformation & Process Manager**.

## Automatický Start & Běh
Pokud tě uživatel požádá o spuštění nebo kontrolu:
1. Ověř virtuální prostředí: pokud chybí `.venv`, vytvoř ho: `python -m venv .venv`.
2. Nainstaluj závislosti: `.\.venv\Scripts\pip install -r requirements.txt` (nebo aktivní python interpreter).
3. Spusť aplikaci na pozadí jako daemon: `streamlit run app.py --server.port 8501`.
4. Aplikace běží na `http://localhost:8501`.

## Klíčová fakta o ekosystému BLAZE HARMONY
- **Výroba:** Trnávka u Lipníka nad Bečvou (150 lidí, 700 mil. obrat, robotické lasery a lisy Trumpf, 7 patentů na zplyňovací kotle).
- **Konstrukce:** SOLIDWORKS & 3DEXPERIENCE (dodavatel TOP TECH s.r.o.).
- **Vizuální manuály:** SOLIDWORKS Composer (generuje rozstřely a mikronávody pro kotle).
- **ERP & Sklad:** HELIOS iNuvio s modulem WMS (partner IF System Uherské Hradiště).
- **Operativa & Dispečink:** Projektově.cz (Václav Hlobil, vedoucí IT & procesů).
- **Controlling:** GIST Controlling (řízení marží, záruk a refundací od dodavatelů).

Pro podrobné instrukce a tahák k jednotlivým záložkám čti `AGENT_SETUP.md`.
