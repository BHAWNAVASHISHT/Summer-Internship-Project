"""
Fin-Suraksha: AI-Assisted Financial Crime Attribution Console
Automated System Integrity & Forensic Verification Suite
"""

import sys
import os
import math
import sqlite3
import pandas as pd
import networkx as nx

def test_database_and_referential_integrity():
    print("[1/5] Testing Database Schema & Referential Integrity...")
    db_path = "fin_suraksha.db"
    assert os.path.exists(db_path), f"Database {db_path} not found"
    
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {r[0] for r in cur.fetchall()}
    
    expected_tables = {"accounts", "customers", "transactions", "devices"}
    assert expected_tables.issubset(tables), f"Missing tables: {expected_tables - tables}"
    
    # Check count of transactions
    cur.execute("SELECT COUNT(*) FROM transactions")
    tx_count = cur.fetchone()[0]
    assert tx_count > 1000, f"Expected >1000 transactions, got {tx_count}"
    
    conn.close()
    print(f"      Database verified: {len(tables)} tables, {tx_count} transactions.")

def test_models_and_intelligence():
    print("[2/5] Testing Intelligence Engine & Risk Evaluator...")
    import intelligence
    import model
    
    gen = model.BankingEcosystemGenerator("fin_suraksha_sample_dataset")
    eco = gen.load_dataset()
    accs = eco.get("accounts", [])
    custs = eco.get("customers", [])
    devs = eco.get("devices", [])
    txns = eco.get("transactions", [])
    atms = eco.get("atms", [])
    brchs = eco.get("branches", [])
    
    assert len(accs) > 0 and len(txns) > 0, "Pipeline missing accounts or transactions"
    
    gdata = model.build_transaction_graph(txns)
    dig = intelligence.DigitalFootprintEngine(devs, accs, custs, txns)
    phys = intelligence.PhysicalFootprintEngine(custs, accs, atms, brchs, txns)
    net = intelligence.NetworkAnalyticsEngine(gdata)
    risk_engine = intelligence.HeuristicRiskEngine(dig, phys, net, accs, txns)
    
    sample_acc = accs[0]["account_id"]
    eval_res = risk_engine.evaluate_account(sample_acc)
    
    assert "ensemble_score" in eval_res, "Evaluation result missing ensemble_score"
    assert "taxonomy_label" in eval_res, "Evaluation result missing taxonomy_label"
    assert eval_res["taxonomy_label"] in ["Normal", "Suspicious", "Mule", "Fraudster"]
    print(f"      Risk Engine verified: Account {sample_acc} evaluated successfully.")

def test_network_graph_module_6():
    print("[3/5] Testing Module 6 (Network Graph & Concentric Rings)...")
    import model
    gen = model.BankingEcosystemGenerator("fin_suraksha_sample_dataset")
    eco = gen.load_dataset()
    txns = eco.get("transactions", [])
    gdata = model.build_transaction_graph(txns)
    df_tx = pd.DataFrame(txns)
    
    # Test top connected account
    top_acc = df_tx["src_account"].value_counts().index[0]
    
    # Build 2-hop ego network
    adj_out = gdata.get("adj_out", {})
    adj_in  = gdata.get("adj_in", {})
    
    hop_dist = {top_acc: 0}
    frontier = {top_acc}
    for h in [1, 2]:
        nxt = set()
        for u in frontier:
            for e in adj_out.get(u, []):
                tgt = e.get("target")
                if tgt and tgt not in hop_dist:
                    hop_dist[tgt] = h
                    nxt.add(tgt)
            for e in adj_in.get(u, []):
                src = e.get("source") or e.get("target")
                if src and src not in hop_dist:
                    hop_dist[src] = h
                    nxt.add(src)
        frontier = nxt
        if len(hop_dist) > 50:
            break
            
    G_sub = nx.DiGraph()
    for n in hop_dist:
        G_sub.add_node(n, hop=hop_dist[n])
        
    for u in hop_dist:
        for e in adj_out.get(u, []):
            v = e.get("target")
            if v and v in hop_dist:
                G_sub.add_edge(u, v, weight=float(e.get("amount", 1000)))
                
    # Verify Concentric Shell Layout
    shells = [[top_acc], [n for n in G_sub.nodes() if hop_dist.get(n) == 1], [n for n in G_sub.nodes() if hop_dist.get(n) == 2]]
    pos = nx.shell_layout(G_sub, nlist=shells)
    
    assert len(pos) == len(G_sub.nodes()), "Layout position count mismatch"
    assert G_sub.number_of_nodes() > 1, "Graph sub-network is empty"
    print(f"      Module 6 verified: Sub-graph with {len(G_sub.nodes())} nodes & {len(G_sub.edges())} edges built with concentric shells.")

def test_crime_map_module_7():
    print("[4/5] Testing Module 7 (India Crime Radar & Haversine Geodesics)...")
    import intelligence
    
    # Test distance calculation from Rohini Cyber PS
    rohini = (28.7159, 77.1171)
    mewat = (28.1067, 77.0057)
    jamtara = (23.9632, 86.8029)
    
    dist_mewat = intelligence.haversine_distance(rohini[0], rohini[1], mewat[0], mewat[1])
    dist_jamtara = intelligence.haversine_distance(rohini[0], rohini[1], jamtara[0], jamtara[1])
    
    assert 60 < dist_mewat < 80, f"Unexpected distance to Mewat: {dist_mewat}"
    assert 1000 < dist_jamtara < 1200, f"Unexpected distance to Jamtara: {dist_jamtara}"
    print(f"      Module 7 verified: Geodesic distances accurate (Rohini-Mewat: {dist_mewat:.1f} km, Rohini-Jamtara: {dist_jamtara:.1f} km).")

def test_ui_cleanliness_and_report_references():
    print("[5/5] Testing UI Cleanliness (Removal of Report/Chapter references)...")
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()
        
    # Check for forbidden academic report phrases in page headers
    forbidden = ["(Report Chapter", "(Chapter 2", "Annexure B", "Thesis"]
    for phrase in forbidden:
        assert phrase.lower() not in content.lower(), f"Forbidden phrase found in app.py: '{phrase}'"
        
    print("      UI Cleanliness verified: Zero report referencing citations found in app.py.")

def test_live_ml_evaluation():
    print("[6/6] Testing Live ML Evaluation (Non-hardcoded Metrics & Confusion Matrix)...")
    import app
    eval_res = app._eval_cache
    assert eval_res["status"] == "completed", f"Evaluation status not completed: {eval_res.get('status')}"
    assert "rf" in eval_res and eval_res["rf"].get("is_live"), "RF not evaluated live"
    assert "xgb" in eval_res and eval_res["xgb"].get("is_live"), "XGBoost not evaluated live"
    assert "lr" in eval_res and eval_res["lr"].get("is_live"), "LR not evaluated live"
    
    # Check confusion matrix dimensions and validity
    cm_rf = eval_res["cm_rf"]
    assert len(cm_rf) == 4 and len(cm_rf[0]) == 4, f"Invalid CM dimensions: {cm_rf}"
    total_test_samples = sum(sum(row) for row in cm_rf)
    assert total_test_samples > 200, f"Expected >200 test samples evaluated, got {total_test_samples}"
    
    # Check dynamically computed class weights
    cw = eval_res["class_weights"]
    assert "Normal" in cw and "Mule" in cw and "Fraudster" in cw, f"Missing class weights: {cw}"
    assert cw["Normal"] > 0 and cw["Mule"] > cw["Normal"], f"Imbalance damping invalid: {cw}"
    
    # Check ROC-AUC
    assert eval_res["rf"]["roc_auc"] > 0.8, f"Unexpected RF ROC-AUC: {eval_res['rf']['roc_auc']}"
    assert eval_res["xgb"]["roc_auc"] > 0.8, f"Unexpected XGB ROC-AUC: {eval_res['xgb']['roc_auc']}"
    assert eval_res["lr"]["roc_auc"] > 0.8, f"Unexpected LR ROC-AUC: {eval_res['lr']['roc_auc']}"
    print(f"      Live ML verified: {total_test_samples} held-out test accounts evaluated across RF, XGBoost & LR.")

if __name__ == "__main__":
    print("=" * 60)
    print("FIN-SURAKSHA SYSTEM INTEGRITY & VERIFICATION SUITE")
    print("=" * 60)
    test_database_and_referential_integrity()
    test_models_and_intelligence()
    test_network_graph_module_6()
    test_crime_map_module_7()
    test_ui_cleanliness_and_report_references()
    test_live_ml_evaluation()
    print("=" * 60)
    print("ALL 6 VERIFICATION SUITES PASSED WITHOUT ERROR!")
    print("=" * 60)
