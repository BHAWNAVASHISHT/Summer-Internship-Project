# Fin-Suraksha — Baseline Audit Report
**Generated:** 2026-10-09
**Auditor:** Antigravity AI Audit Engine

---

## 1. Environment

| Item | Value |
|------|-------|
| Python | 3.14.4 |
| Streamlit | 1.56.0 |
| Plotly | 6.8.0 |
| pandas | 3.0.2 |
| scikit-learn | 1.9.0 |
| XGBoost | 3.4.1 |
| SHAP | 0.52.0 |
| PyTorch | 2.13.0 |
| PyTorch Geometric | 2.8.0.post1 |
| NetworkX | 3.6.1 |
| python-louvain | installed |
| reportlab | installed |
| fpdf / fpdf2 | NOT INSTALLED |

---

## 2. File Inventory

| File | Size (bytes) | Lines |
|------|-------------|-------|
| app.py | 105,760 | 2,207 |
| model.py | 43,867 | 1,142 |
| intelligence.py | 43,544 | ~900 |
| logo_helper.py | 275 | ~10 |
| requirements.txt | 367 | 17 |
| README.md | 7,706 | ~200 |
| fin_suraksha.db | 2,441,216 | SQLite |

---

## 3. Dataset Statistics

| Table | Rows | Notes |
|-------|------|-------|
| accounts | 1,800 | Format: ACC00001 (CSV) vs ACC_00001_0 (generator) — MISMATCH |
| transactions | 8,973 | Contains `scenario_label` and `fraud_label` columns — LEAKAGE RISK |
| labels | 1,800 | Derived from generator assignments — NOT model predictions |
| customers | 1,200 | |
| devices | 1,500 | |
| branches | 60 | |
| ATMs | 80 | |
| merchants | 120 | |

### Label Distribution (labels.csv)
| Class | Count | % |
|-------|-------|---|
| Normal | 1,305 | 72.5% |
| Mule | 288 | 16.0% |
| Fraudster | 114 | 6.3% |
| Suspicious | 93 | 5.2% |

### Critical Issue: 216 Non-Normal Accounts Have Zero Transactions
- Mule accounts missing from transactions: 101
- Suspicious accounts missing: 93
- Fraudster accounts missing: 22
- These accounts would appear Normal to any ML model — evaluation is invalid

---

## 4. Critical Defects Found

### DEF-001: `rng.exponential` — Method Does Not Exist
- **Location:** `model.py` line 467
- **Code:** `amt = round(rng.exponential(2500) + 150, 2)`
- **Issue:** `random.Random` has no `.exponential()` method — this fails at runtime
- **Fix:** Replace with `rng.expovariate(1/2500)` or use `numpy.random.default_rng(seed).exponential(2500)`

### DEF-002: Ground-Truth Label Leakage in Transactions
- **Location:** `transactions.csv`, columns `scenario_label` and `fraud_label`
- **Issue:** The transaction table exposes the ground-truth fraud class label per transaction
- **Fix:** Remove `fraud_label` from feature-building. Keep it only in a separate evaluation table.

### DEF-003: Labels Table Contains Generator-Assigned Labels, Not Model Predictions
- **Location:** `labels.csv`, app.py all modules
- **Issue:** `labels.csv` is the generator's ground truth, but displayed as "flagged accounts" implying ML discovery
- **Fix:** Rename to `ground_truth_labels.csv`; predictions must come from an actual model run

### DEF-004: Hardcoded Benchmark Metrics in `get_benchmark_comparison()`
- **Location:** `model.py` lines 1041–1084
- **Issue:** Returns static dict — not computed from actual model evaluation
- **Fix:** Implement `run_evaluation_pipeline()` that trains, evaluates, and saves real metrics to JSON

### DEF-005: Fake SHAP in `compute_shap_values()`
- **Location:** `model.py` lines 1106–1128
- **Issue:** Uses hardcoded per-class weight vectors, not SHAP library. Labeled misleadingly.
- **Fix:** Use `shap.TreeExplainer` on actual fitted RF/XGBoost; label rule-based explanations honestly

### DEF-006: Plaintext Passwords in source code
- **Location:** `app.py` (USERS dict)
- **Issue:** Credentials `BHAWNAVASHISHT/Maims@351` in plaintext
- **Fix:** Use `werkzeug.security.check_password_hash` or similar

### DEF-007: Unrestricted SQL Console
- **Location:** `app.py` Module 10 (SQL Query Tool)
- **Issue:** `db.execute_script(sql)` is called with raw user input — allows DROP/DELETE/UPDATE
- **Fix:** Enforce read-only connection; block dangerous SQL patterns

### DEF-008: Audit Log Not Cryptographic
- **Location:** SQLite `audit_log` table
- **Issue:** Described as tamper-proof but has no cryptographic integrity
- **Fix:** Add honest description; optionally add hash chain

### DEF-009: All Non-Normal Accounts Grouped in One "Fraud Ring"
- **Location:** app.py fraud ring detection
- **Issue:** Using weakly connected components on ALL edges (txn + shared device + shared IP) creates one mega-ring
- **Fix:** Use directed financial paths only for ring detection; apply minimum-size and pattern criteria

### DEF-010: India Crime Map Blank
- **Location:** Module 7 (India Crime Statistics Map)
- **Issue:** `go.Scattermapbox` deprecated/incompatible with Plotly 6.x
- **Fix:** Use `go.Scattermap` or `px.scatter_map` (Plotly 6+ API)

### DEF-011: PDF Reports Lack "SYNTHETIC DEMO" Watermark
- **Location:** Module 13 (Legal Notices & Reports)
- **Issue:** Generated documents look official without disclaimer
- **Fix:** Add mandatory watermark text on all generated documents

### DEF-012: Generated Account IDs Don't Match Shipped CSVs
- **Location:** Generator uses `ACC_00001_0`; CSV has `ACC00001`
- **Issue:** If generator is run, it creates incompatible IDs
- **Fix:** Standardize ID format across generator and CSVs

---

## 5. Features Genuinely Working

| Feature | Status |
|---------|--------|
| Database (SQLite) CRUD | ✅ Working |
| CSV import | ✅ Working |
| Transaction graph construction | ✅ Working (BFS/adjacency dict) |
| PageRank computation | ✅ Working (custom implementation) |
| Clustering coefficient | ✅ Working |
| Feature engineering (11-dim) | ✅ Working |
| RF training code | ✅ Working (sklearn installed) |
| XGBoost training code | ✅ Working |
| GNN training code (GCN/SAGE/GAT) | ✅ Code present (PyG installed) |
| Heuristic risk engine | ✅ Working (rules-based) |
| Money trail (BFS) | ✅ Working |
| Login/session | ✅ Working (but plaintext passwords) |
| Audit logging | ✅ Basic logging works |

## 6. Features Broken/Fake

| Feature | Status |
|---------|--------|
| `rng.exponential()` | ❌ AttributeError at runtime |
| SHAP explanations | ❌ Fake — uses hardcoded weights |
| Benchmark metrics | ❌ Hardcoded from report |
| Confusion matrix | ❌ Hardcoded from report |
| Fraud ring detection | ❌ One mega-ring (1,584 accounts) |
| India Crime Map | ❌ Blank (Plotly API change) |
| Password security | ❌ Plaintext in source code |
| SQL console safety | ❌ Unrestricted |
| Audit tamper-proof claim | ❌ Not cryptographic |
| PDF disclaimer | ❌ Missing |
| Non-normal account transactions | ❌ 216 accounts have no transactions |

---

## 7. Next Steps (Priority Order)

1. Fix `rng.exponential` bug (DEF-001)
2. Fix 216 missing transactions (DEF-003)
3. Remove label leakage from features (DEF-002)
4. Implement real model evaluation pipeline (DEF-004)
5. Implement real SHAP (DEF-005)
6. Fix fraud ring detection (DEF-009)
7. Fix India Crime Map (DEF-010)
8. Fix password security (DEF-006)
9. Fix SQL console (DEF-007)
10. Add PDF disclaimer (DEF-011)
11. Create automated test suite
12. Update documentation
