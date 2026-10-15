# Fin-Suraksha: AI-Assisted Financial Crime Attribution Console

**Host Organization:** Cyber Police Station, Sector-17, Rohini, Delhi-110089  
**Academic Affiliation:** Maharaja Agrasen Institute of Management Studies (MAIMS), Department of Computer Applications  
**Student Researcher / Developer:** Bhawna Vashisht (Enrolment No.: 35114702024)  
**Investigating Mentor:** ASI Jaswinder Joon (I.O.) | PIS: 28910482  
**Station House Officer:** Insp. Parveen Chauhan (S.H.O.)  

---

## 1. Overview & Motivation (Chapters 1 & 2)

Conventional fraud detection tools focus primarily on binary classification (fraud vs. legitimate) at the individual transaction level. However, cybercrime investigations at a police station require answering broader, correlation-centric questions:
- **Where did the money go?** Reconstructing multi-hop money trails across rapid layering accounts in real time.
- **Which accounts are mules versus coordinators?** Classifying entities under a 4-class taxonomy: `Normal`, `Suspicious`, `Mule`, and `Fraudster`.
- **What shared footprints link seemingly unrelated accounts?** Correlating digital footprints (shared IMEI, IP, SIM ICCID, browser fingerprint) and physical footprints (ATM CCTV camera feeds, branch footage retention, impossible travel speeds > 500 km/h).
- **How to preserve perishable evidence under Indian law?** Tracking ATM/branch CCTV footage countdowns (< 30 days) and automating formal notices under **Section 94 of Bharatiya Nagarik Suraksha Sanhita (BNSS), 2023**.

Fin-Suraksha is built around this exact ground-level investigative workflow for Delhi Police Cyber Cell.

---

## 2. Default Access Credentials

All sessions are cryptographically logged in the relational audit trail table (`audit_log`). Access requires authenticated role credentials:

| Role | Username | Password | Privileges |
|------|----------|----------|------------|
| **Tech Admin / Developer** | `BHAWNAVASHISHT` | `Maims@351` | Full administrative console, ecosystem reseed generator, database management |
| **Investigating Officer (I.O.)** | `Jaswinder` | `IO@351` | Case management, Officer Mode telemetry, Section 94 notice generation, PDF case dossiers |

---

## 3. Architecture & File Structure

```text
Summer Internship Project/
├── fin_suraksha_sample_dataset/
│   ├── accounts.csv           # 1,800 accounts with bank, UPI ID/app, IP, balance
│   ├── atms.csv               # 90 ATM terminals, CCTV camera ID, retention days
│   ├── branches.csv           # Bank branches, manager contacts, CCTV footage retention
│   ├── customers.csv          # 1,200 customers, registered phone, home location, SIM ICCID
│   ├── devices.csv            # 2,400 devices, IMEI numbers, fingerprints, shared flags
│   ├── labels.csv             # Ground-truth 4-class taxonomy & attribution reasons
│   ├── merchants.csv          # 120 merchants, settlement accounts, geo-coordinates
│   └── transactions.csv       # 8,973 multi-hop transactions across 20 fraud typologies
├── app.py                     # Streamlit Presentation Layer (12 investigator pages + 1 admin page)
├── intelligence.py            # Correlation Engines (Digital, Physical, Network, Ensemble Risk & BNSS Notices)
├── model.py                   # SQLite DatabaseEngine, Graph Construction, Feature Engineering, Classical ML & GNNs
├── fin_suraksha.db            # SQLite relational database (3NF relational schema)
├── requirements.txt           # Python dependencies (NetworkX, PyG, XGBoost, SHAP, ReportLab, etc.)
└── README.md                  # Project documentation & operational run guide
```

---

## 4. Multi-Layer System Architecture

1. **Relational Database & Data Layer (`model.py`)**:
   - SQLite 3NF relational schema with 8 entity tables (`accounts`, `transactions`, `customers`, `devices`, `branches`, `merchants`, `atms`, `labels`) and `audit_log`.
   - 20 realistic Indian cyber fraud typologies with genuine fund routes (UPI, IMPS, ATM Cash, NEFT, RTGS).
2. **Graph & Feature Engineering Layer (`model.py`)**:
   - Builds directed multi-edge transaction graph + shared hardware identifier linkage edges.
   - Extracts 11-dimensional node feature vectors (PageRank, betweenness centrality, in/out transaction velocity, amount burst ratio, shared-IMEI flags, VPN indicator, etc.).
3. **Correlation & Intelligence Layer (`intelligence.py`)**:
   - `DigitalFootprintEngine`: Correlates shared IMEIs (+30), shared IPs (+20), VPN routing (+20), SIM ICCID re-use (+15), and login bursts (+15).
   - `PhysicalFootprintEngine`: Haversine impossible travel speed (>500 km/h over >50 km), transaction radius anomaly (>250 km), and ATM CCTV retention countdown.
   - `NetworkAnalyticsEngine`: PageRank, betweenness centrality, and mastermind score (50% out-degree + 30% betweenness + 20% PageRank).
   - `HeuristicRiskEngine`: 6-component weighted ensemble score (Network 25%, Physical 25%, Rule 15%, Behaviour 15%, Temporal 10%, Geographic 10%).
   - `NLG & Legal Notice Module`: Generates formal notices under Section 94 BNSS, 2023 and case diary entries (Para 4 Fund Flow Reconstruction).
   - `ReportLab PDF Module`: Produces official Delhi Police case reports ready for judicial filing.
4. **Presentation Layer (`app.py`)**:
   - National Informatics Centre (NIC) and Government of India design aesthetic (Deep Navy `#003366`, Saffron `#FF6200`, Ashoka Chakra elements, formal typography).

---

## 5. Console Modules (12 Investigator Pages)

1. **Command Center Dashboard**: Live ecosystem KPIs, risk label distribution, risk tiers, and priority case queue.
2. **Load Data & SQL Console**: 3NF table browser, SQL query console with presets, and external CSV ingestion.
3. **Fraud Prediction**: Pre-trained 4-class classification using GraphSAGE with experimental performance benchmarks.
4. **SHAP Explainability**: Per-account SHAP waterfall showing exact feature impact (+/- risk drivers).
5. **Transaction Network Graph**: Interactive ego-network of money trails and shared IMEI/IP hardware edges with custom hop depth.
6. **India Crime Heatmap & Corridors**: Real interactive map (OpenStreetMap/Mapbox) with cybercrime hotspots and documented inter-state fund corridors.
7. **Fraud Timeline**: Chronological transaction stream with nocturnal 1–4 AM automated detection.
8. **Case Explorer**: Dossier lookup by Account ID, phone, or UPI handle with complete KYC, device history, and ledger breakdown.
9. **Investigation Mode**: Multi-hop fund trail reconstruction across all 20 real FIR cases with Officer Mode and CCTV countdowns.
10. **Fraud Ring Visualization**: Identification of all 20 active syndicate rings with coordinator mastermind scores and member rosters.
11. **Model Performance Report**: Actual experimental benchmarks from Chapter 4, Table 4.1.4 (Random Forest, XGBoost, GCN, GraphSAGE, GAT).
12. **Reports & Data Export**: Section 94 BNSS legal notices, downloadable PDF dossiers, CSV archive bundles, and audit trail logs.
13. *(Admin Only)* **Ecosystem Generator**: Interactive utility to reseed the banking ecosystem with configurable parameters.

---

## 6. How to Run Locally

### Prerequisites
- Python 3.10+ (Tested on Python 3.14)
- Pip

### Setup and Launch
```powershell
# Navigate to project directory
cd "C:\Users\JANMEJAY VASHISHT\Desktop\Summer Internship Project"

# Install required dependencies
pip install -r requirements.txt

# Run the Streamlit application
streamlit run app.py
```

Open your browser at `http://localhost:8501`.  
Log in with either:
- **Tech Admin**: `BHAWNAVASHISHT` / `Maims@351`
- **Investigating Officer**: `Jaswinder` / `IO@351`
