"""
Fin-Suraksha: Correlation and Intelligence Engines
Module: intelligence.py (Referenced in Chapters 2, 3, 4, 5 of Cyber Crime Investigation Report)

Host Organization: Cyber Police Station, Sector-17, Rohini, Delhi-110089
Academic Affiliation: Maharaja Agrasen Institute of Management Studies (MAIMS)
Student Researcher: Bhawna Vashisht (BCA)
Investigating Mentor: ASI Jaswinder Joon (I.O.)
Station House Officer: Parveen Chauhan (S.H.O.)
"""

import os
import math
import random
import datetime
from collections import defaultdict, deque

# Import Guards
try:
    import networkx as nx
    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False

try:
    import community as community_louvain
    HAS_LOUVAIN = True
except ImportError:
    HAS_LOUVAIN = False

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False


EARTH_RADIUS_KM = 6371.0


def haversine_distance(lat1, lon1, lat2, lon2):
    """Computes great-circle distance between two geographic coordinates in km (Chapter 2, Table 2.1)."""
    try:
        phi1, phi2 = math.radians(float(lat1)), math.radians(float(lat2))
        dphi = math.radians(float(lat2) - float(lat1))
        dlambda = math.radians(float(lon2) - float(lon1))
        a = math.sin(dphi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0) ** 2
        return 2.0 * EARTH_RADIUS_KM * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    except Exception:
        return 0.0


class DigitalFootprintEngine:
    """
    Correlates accounts sharing hardware device ID, IP, SIM ICCID, or browser fingerprint.
    Implements Chapter 2.2.2 & 3.5 scoring:
      - Shared hardware device IMEI: +30 pts
      - Shared IP address: +20 pts
      - VPN / proxy / TOR signature: +20 pts
      - SIM/ICCID reuse: +15 pts
      - Login-burst anomaly: +15 pts (>=5 txns within 60-second windows)
      Total capped at 100.
    """

    def __init__(self, devices=None, accounts=None, customers=None, transactions=None):
        self.devices = devices or []
        self.accounts = accounts or []
        self.customers = customers or []
        self.transactions = transactions or []
        self._build_indices()

    def _build_indices(self):
        self.dev_by_account = defaultdict(list)
        self.accs_by_device = defaultdict(set)
        self.accs_by_ip = defaultdict(set)
        self.accs_by_sim = defaultdict(set)
        self.vpn_by_account = defaultdict(bool)

        for d in self.devices:
            acc = d.get("account_id")
            did = d.get("device_id")
            vpn = str(d.get("vpn_detected", "0")) in ("1", "True", "true")
            if acc:
                self.dev_by_account[acc].append(d)
                if vpn:
                    self.vpn_by_account[acc] = True
            if did and acc:
                self.accs_by_device[did].add(acc)

        for a in self.accounts:
            aid = a.get("account_id")
            ip = a.get("ip_address")
            if aid and ip:
                self.accs_by_ip[ip].add(aid)

        cust_sim_map = {c.get("customer_id"): c.get("sim_iccid") for c in self.customers if "customer_id" in c}
        for a in self.accounts:
            aid = a.get("account_id")
            cid = a.get("customer_id")
            sim = cust_sim_map.get(cid)
            if aid and sim:
                self.accs_by_sim[sim].add(aid)

        self.txns_by_acc = defaultdict(list)
        for t in self.transactions:
            src = t.get("src_account")
            if src:
                self.txns_by_acc[src].append(t)

    def login_anomaly_flags(self, account_id):
        """Flags account when 5 or more consecutive transactions occur within 60-second windows."""
        txs = self.txns_by_acc.get(account_id, [])
        if len(txs) < 5:
            return False, 0

        parsed = []
        for t in txs:
            try:
                dt = datetime.datetime.strptime(t["timestamp"], "%Y-%m-%d %H:%M:%S")
                parsed.append(dt)
            except Exception:
                continue

        parsed.sort()
        burst_clusters = 0
        window = deque()

        for ts in parsed:
            window.append(ts)
            while window and (ts - window[0]).total_seconds() > 60:
                window.popleft()
            if len(window) >= 5:
                burst_clusters += 1

        return (burst_clusters > 0), burst_clusters

    def compute_digital_score(self, account_id):
        """Evaluates composite digital risk score (0-100) and forensic rationale."""
        score = 0
        evidence = []
        shared_devs = []

        for d in self.dev_by_account.get(account_id, []):
            did = d.get("device_id")
            if did and len(self.accs_by_device.get(did, set())) > 1:
                linked = self.accs_by_device[did] - {account_id}
                shared_devs.append((did, list(linked)))

        if shared_devs:
            score += 30
            dev_ids = ", ".join([sd[0] for sd in shared_devs[:2]])
            linked_count = sum(len(sd[1]) for sd in shared_devs)
            evidence.append(f"Shared device hardware [{dev_ids}] linked to {linked_count} other accounts (+30 pts)")

        user_acc = next((a for a in self.accounts if a.get("account_id") == account_id), None)
        if user_acc and user_acc.get("ip_address"):
            ip = user_acc["ip_address"]
            ip_linked = self.accs_by_ip.get(ip, set()) - {account_id}
            if ip_linked:
                score += 20
                evidence.append(f"Shared IP address [{ip}] co-accessed by {len(ip_linked)} other accounts (+20 pts)")

        if self.vpn_by_account.get(account_id, False):
            score += 20
            evidence.append("Active VPN / anonymized proxy connection signature detected (+20 pts)")

        if user_acc:
            cid = user_acc.get("customer_id")
            cust = next((c for c in self.customers if c.get("customer_id") == cid), None)
            if cust and cust.get("sim_iccid"):
                sim = cust["sim_iccid"]
                sim_linked = self.accs_by_sim.get(sim, set()) - {account_id}
                if sim_linked:
                    score += 15
                    evidence.append(f"SIM ICCID [{sim[:8]}...] reused across multiple banking accounts (+15 pts)")

        has_burst, burst_count = self.login_anomaly_flags(account_id)
        if has_burst:
            score += 15
            evidence.append(f"Automated login burst: {burst_count} clusters of >=5 transactions in <=60s (+15 pts)")

        return {
            "score": min(100, score),
            "evidence": evidence,
            "shared_devices": shared_devs,
            "has_vpn": self.vpn_by_account.get(account_id, False),
            "burst_anomaly": has_burst
        }


class PhysicalFootprintEngine:
    """
    Analyses offline and physical footprints (Chapter 1.3.2 & 2.2.2):
      - impossible_travel_check (>500 km/h over >50 km)
      - radius_anomaly (>250 km from registered home)
      - physical_score_and_evidence (Cheque layering +30, ATM cash-out +30, POS +10, multi-city +15)
      - cctv_footage_status (retention window tracking relative to reference date)
    """

    def __init__(self, customers=None, accounts=None, atms=None, branches=None, transactions=None):
        self.customers = customers or []
        self.accounts = accounts or []
        self.atms = atms or []
        self.branches = branches or []
        self.transactions = transactions or []

        # Reference investigation date: 2026-07-24 (Cyber Police Station Rohini report date)
        self.ref_date = datetime.datetime(2026, 7, 24, 0, 0, 0)
        self.cust_map = {c.get("customer_id"): c for c in self.customers}
        self.acc_cust_map = {a.get("account_id"): a.get("customer_id") for a in self.accounts}

    def impossible_travel_check(self, account_id):
        """Flags impossible travel speeds exceeding 500 km/h over > 50 km between consecutive events."""
        acc_txs = [t for t in self.transactions if t.get("src_account") == account_id or t.get("dst_account") == account_id]
        if len(acc_txs) < 2:
            return False, []

        parsed = []
        for t in acc_txs:
            try:
                dt = datetime.datetime.strptime(t["timestamp"], "%Y-%m-%d %H:%M:%S")
                city = t.get("city", "Delhi")
                lat, lon = 28.6139, 77.2090
                if "Jamtara" in city: lat, lon = 23.9632, 86.8029
                elif "Nuh" in city: lat, lon = 28.1067, 77.0057
                elif "Bharatpur" in city: lat, lon = 27.2152, 77.5030
                elif "Mumbai" in city: lat, lon = 19.0760, 72.8777
                elif "Rohini" in city: lat, lon = 28.7159, 77.1171
                elif "Bengaluru" in city: lat, lon = 12.9716, 77.5946
                elif "Kolkata" in city: lat, lon = 22.5726, 88.3639
                parsed.append({"time": dt, "city": city, "lat": lat, "lon": lon, "tx": t})
            except Exception:
                continue

        parsed.sort(key=lambda x: x["time"])
        violations = []

        for i in range(len(parsed) - 1):
            e1, e2 = parsed[i], parsed[i + 1]
            hours = (e2["time"] - e1["time"]).total_seconds() / 3600.0
            if hours <= 0:
                continue
            dist_km = haversine_distance(e1["lat"], e1["lon"], e2["lat"], e2["lon"])
            if dist_km > 50.0:
                speed = dist_km / hours
                if speed > 500.0:
                    violations.append({
                        "event1": f"{e1['city']} at {e1['time'].strftime('%H:%M:%S')}",
                        "event2": f"{e2['city']} at {e2['time'].strftime('%H:%M:%S')}",
                        "distance_km": round(dist_km, 1),
                        "hours": round(hours, 2),
                        "implied_speed_kmh": round(speed, 1)
                    })

        return len(violations) > 0, violations

    def radius_anomaly(self, account_id):
        """Flags transactions occurring beyond 250 km radius of registered customer home."""
        cid = self.acc_cust_map.get(account_id)
        cust = self.cust_map.get(cid)
        if not cust or not cust.get("latitude"):
            return False, []

        try:
            home_lat = float(cust.get("latitude", 28.6139))
            home_lon = float(cust.get("longitude", 77.2090))
        except (ValueError, TypeError):
            home_lat, home_lon = 28.6139, 77.2090
        home_city = cust.get("home_location", "Delhi")

        acc_txs = [t for t in self.transactions if t.get("src_account") == account_id or t.get("dst_account") == account_id]
        anomalies = []

        for t in acc_txs:
            city = t.get("city", home_city)
            c_lat, c_lon = home_lat, home_lon
            if "Jamtara" in city: c_lat, c_lon = 23.9632, 86.8029
            elif "Nuh" in city: c_lat, c_lon = 28.1067, 77.0057
            elif "Bharatpur" in city: c_lat, c_lon = 27.2152, 77.5030
            elif "Mumbai" in city: c_lat, c_lon = 19.0760, 72.8777
            elif "Rohini" in city: c_lat, c_lon = 28.7159, 77.1171

            dist = haversine_distance(home_lat, home_lon, c_lat, c_lon)
            if dist > 250.0:
                anomalies.append({
                    "tx_id": t.get("transaction_id"),
                    "city": city,
                    "distance_from_home_km": round(dist, 1),
                    "home_city": home_city
                })

        return len(anomalies) > 0, anomalies

    def cctv_footage_status(self, atm_or_branch_id, event_date_str):
        """Determines whether CCTV footage is within preservation window relative to reference date."""
        target = next((a for a in self.atms if a.get("atm_id") == atm_or_branch_id), None)
        if not target:
            target = next((b for b in self.branches if b.get("branch_id") == atm_or_branch_id), None)

        try:
            retention_days = int(target.get("footage_retention_days", 45)) if target else 45
        except Exception:
            retention_days = 45
        camera_id = target.get("cctv_camera_id", f"CAM_{atm_or_branch_id}") if target else "CAM_DEFAULT"

        try:
            event_dt = datetime.datetime.strptime(event_date_str.split(" ")[0], "%Y-%m-%d")
            elapsed = (self.ref_date - event_dt).days
            remaining = retention_days - elapsed
            is_available = remaining > 0
        except Exception:
            is_available = True
            remaining = retention_days
            elapsed = 0

        return {
            "camera_id": camera_id,
            "retention_days": retention_days,
            "days_elapsed": elapsed,
            "days_remaining": max(0, remaining),
            "status": "Available - Immediate Notice Required" if is_available else "Expired - Footage Overwritten",
            "urgency": "CRITICAL (<=5 days)" if 0 < remaining <= 5 else ("Active" if is_available else "Overwritten")
        }

    def compute_physical_score(self, account_id):
        """Computes physical footprint risk score (0-100) and evidence trails."""
        score = 0
        evidence = []

        acc_txs = [t for t in self.transactions if t.get("src_account") == account_id or t.get("dst_account") == account_id]
        channels = [t.get("channel", "") for t in acc_txs]

        if any("Cheque" in c for c in channels):
            score += 30
            evidence.append("Cheque clearing / kiting loop detected (+30 pts)")

        if any("ATM" in c for c in channels):
            score += 30
            evidence.append("Physical ATM cash-out dispersal executed (+30 pts)")

        if any("POS" in c for c in channels):
            score += 10
            evidence.append("Physical POS swipe Terminal authorization (+10 pts)")

        has_imp, imp_list = self.impossible_travel_check(account_id)
        if has_imp:
            score += 25
            evidence.append(f"Impossible travel violation: {imp_list[0]['implied_speed_kmh']} km/h speed across locations (+25 pts)")

        has_rad, rad_list = self.radius_anomaly(account_id)
        if has_rad:
            score += 15
            evidence.append(f"Radius anomaly: Transaction {rad_list[0]['distance_from_home_km']} km away from registered KYC address (+15 pts)")

        return {
            "score": min(100, score),
            "evidence": evidence,
            "impossible_travel": imp_list if has_imp else [],
            "radius_anomalies": rad_list if has_rad else []
        }


class NetworkAnalyticsEngine:
    """
    Graph Analytics Engine (Chapter 2, Table 2.1 & Chapter 3.5):
      - Approximate Betweenness Centrality
      - PageRank Centrality
      - Mastermind Coordinator Likelihood Score (betweenness 50%, PR 30%, in-degree 20%)
      - Fraud Ring Discovery (Louvain Communities & Connected Components)
      - Multi-hop Money Trail Reconstruction (BFS / Dijkstra)
    """

    def __init__(self, graph_data):
        self.nodes = graph_data["nodes"]
        self.adj_out = graph_data["adj_out"]
        self.adj_in = graph_data["adj_in"]
        self.node_stats = graph_data["node_stats"]
        self._compute_centralities()

    def _compute_centralities(self):
        N = len(self.nodes)
        if N == 0:
            self.pagerank = {}
            self.betweenness = {}
            return

        # 1. PageRank
        damping = 0.85
        pr = {node: 1.0 / N for node in self.nodes}
        for _ in range(25):
            next_pr = {node: (1.0 - damping) / N for node in self.nodes}
            for u in self.nodes:
                targets = self.adj_out.get(u, [])
                if targets:
                    share = (damping * pr[u]) / len(targets)
                    for edge in targets:
                        next_pr[edge["target"]] += share
                else:
                    for v in self.nodes:
                        next_pr[v] += (damping * pr[u]) / N
            pr = next_pr
        self.pagerank = pr

        # 2. Approximate Betweenness Centrality (Sampling)
        self.betweenness = defaultdict(float)
        k_samples = min(40, len(self.nodes))
        sampled_sources = random.sample(self.nodes, k_samples) if len(self.nodes) > 0 else []

        for s in sampled_sources:
            dist = {s: 0}
            sigma = defaultdict(int)
            sigma[s] = 1
            pred = defaultdict(list)
            q = deque([s])
            stack = []

            while q:
                v = q.popleft()
                stack.append(v)
                for edge in self.adj_out.get(v, []):
                    w = edge["target"]
                    if w not in dist:
                        dist[w] = dist[v] + 1
                        q.append(w)
                    if dist[w] == dist[v] + 1:
                        sigma[w] += sigma[v]
                        pred[w].append(v)

            delta = defaultdict(float)
            while stack:
                w = stack.pop()
                for v in pred[w]:
                    delta[v] += (sigma[v] / sigma[w]) * (1.0 + delta[w])
                if w != s:
                    self.betweenness[w] += delta[w]

        max_b = max(self.betweenness.values()) if self.betweenness else 1.0
        if max_b > 0:
            for n in self.nodes:
                self.betweenness[n] = self.betweenness[n] / max_b

    def compute_mastermind_score(self, account_id):
        """
        Combines betweenness (50%), PageRank (30%), and in-degree (20%, capped at 20)
        into a single 0-100 coordinator likelihood score (Chapter 2.2.3 & 5.6.3).
        """
        b_score = self.betweenness.get(account_id, 0.0)
        max_pr = max(self.pagerank.values()) if self.pagerank else 1.0
        pr_norm = min(1.0, (self.pagerank.get(account_id, 0.0) / max_pr) if max_pr > 0 else 0.0)

        in_deg = self.node_stats.get(account_id, {}).get("in_degree", 0)
        in_norm = min(1.0, in_deg / 20.0)

        raw = (0.50 * b_score) + (0.30 * pr_norm) + (0.20 * in_norm)
        return round(raw * 100.0, 1)

    def detect_fraud_rings(self, min_size=3, max_size=25):
        """
        Discovers candidate suspicious transaction clusters (candidate syndicates)
        from transaction flow topology and rapid pass-through layering (Chapters 2.2.2 & 3.5).
        
        CRITICAL ARCHITECTURAL GUARANTEE (Phase 6):
        - Does NOT treat weakly connected components of the retail graph as fraud rings.
        - Isolates accounts connected by rapid pass-through layering (<60 min turnaround with
          >65% fund preservation) or structuring transaction amounts.
        - Enforces cluster bounds (3 <= size <= 25 nodes).
        - Results are explicitly documented as 'Candidate Suspicious Transaction Clusters'
          (academic hypothesis aid, not proven syndicate).
        """
        # 1. Identify suspicious rapid pass-through layering edges
        susp_adj = defaultdict(set)
        
        # Build in-bound and out-bound transaction index with timestamps
        in_txs = defaultdict(list)
        out_txs = defaultdict(list)
        for u in self.nodes:
            for e in self.adj_out.get(u, []):
                e_full = {
                    "source": u,
                    "target": e["target"],
                    "amount": float(e.get("amount", 0.0)),
                    "channel": e.get("channel", "UPI"),
                    "timestamp": e.get("timestamp", "")
                }
                out_txs[u].append(e_full)
                in_txs[e["target"]].append(e_full)

        def _parse_ts(ts_str):
            try:
                return datetime.datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
            except Exception:
                return None

        # Detect rapid layering: A -> B then B -> C within 60 mins where amounts are comparable
        for b_acc, in_edges in in_txs.items():
            if b_acc not in out_txs:
                continue
            for ei in in_edges:
                amt_i = float(ei.get("amount", 0.0))
                if amt_i < 15000.0:  # ignore micro retail transactions
                    continue
                dti = _parse_ts(ei.get("timestamp", ""))
                if not dti:
                    continue
                for eo in out_txs[b_acc]:
                    amt_o = float(eo.get("amount", 0.0))
                    dto = _parse_ts(eo.get("timestamp", ""))
                    if not dto:
                        continue
                    delta = (dto - dti).total_seconds()
                    # Layering condition: out within 3600s, amount preserved between 65% and 105%
                    if 0 < delta <= 3600 and 0.65 * amt_i <= amt_o <= 1.05 * amt_i:
                        a_acc = ei.get("source") or ei.get("src")
                        c_acc = eo.get("target") or eo.get("dst")
                        if a_acc and c_acc and a_acc != b_acc and b_acc != c_acc:
                            susp_adj[a_acc].add(b_acc)
                            susp_adj[b_acc].add(a_acc)
                            susp_adj[b_acc].add(c_acc)
                            susp_adj[c_acc].add(b_acc)

        # 2. Extract connected components on suspicious layering edges only
        visited = set()
        rings = []
        ring_idx = 101

        for start in list(susp_adj.keys()):
            if start in visited:
                continue
            comp = set()
            q = deque([start])
            visited.add(start)

            while q:
                curr = q.popleft()
                comp.add(curr)
                for nbr in susp_adj.get(curr, []):
                    if nbr not in visited:
                        visited.add(nbr)
                        q.append(nbr)

            # Bounded candidate clusters (between min_size and max_size)
            if min_size <= len(comp) <= max_size:
                ranked = sorted(list(comp), key=lambda x: self.compute_mastermind_score(x), reverse=True)
                coordinator = ranked[0]
                mules = ranked[1:]
                rings.append({
                    "ring_id": f"CANDIDATE_CLUSTER_{ring_idx}",
                    "size": len(comp),
                    "members": list(comp),
                    "coordinator": coordinator,
                    "mules": mules,
                    "coordinator_score": self.compute_mastermind_score(coordinator),
                    "detection_method": "Rapid Pass-Through Layering & Temporal Analysis",
                    "confidence": "Hypothesis (Academic Prototype)",
                    "disclaimer": "Synthetic candidate cluster — requires human investigative corroboration."
                })
                ring_idx += 1

        # Sort candidate clusters by mastermind coordinator score
        rings.sort(key=lambda r: (r["coordinator_score"], r["size"]), reverse=True)
        return rings

    def find_money_trail(self, start_acc, target_acc, max_hops=10):
        """Reconstructs shortest directed money-trail path using BFS with cycle protection."""
        if start_acc == target_acc:
            return [start_acc]

        visited = {start_acc}
        parent = {}
        depth = {start_acc: 0}
        q = deque([start_acc])

        found = False
        while q and not found:
            curr = q.popleft()
            if depth[curr] >= max_hops:
                continue
            for edge in self.adj_out.get(curr, []):
                tgt = edge["target"]
                if tgt not in visited:
                    visited.add(tgt)
                    depth[tgt] = depth[curr] + 1
                    parent[tgt] = (curr, edge)
                    if tgt == target_acc:
                        found = True
                        break
                    q.append(tgt)

        if not found:
            return []

        path = [target_acc]
        curr = target_acc
        while curr in parent:
            prev, _ = parent[curr]
            path.append(prev)
            curr = prev

        path.reverse()
        return path

    def find_money_trail_edges(self, start_acc, target_acc, max_hops=10):
        """Reconstructs full sequence of directed transaction edge dicts along shortest trail."""
        node_path = self.find_money_trail(start_acc, target_acc, max_hops=max_hops)
        if len(node_path) < 2:
            return []

        edges_in_trail = []
        for i in range(len(node_path) - 1):
            src, dst = node_path[i], node_path[i + 1]
            # Find best matching edge from src to dst in adj_out
            matching = [e for e in self.adj_out.get(src, []) if e.get("target") == dst]
            if matching:
                best_edge = max(matching, key=lambda e: float(e.get("amount", 0.0)))
                edges_in_trail.append({
                    "hop": i + 1,
                    "src": src,
                    "dst": dst,
                    "amount": float(best_edge.get("amount", 0.0)),
                    "channel": best_edge.get("channel", "UPI"),
                    "timestamp": best_edge.get("timestamp", ""),
                })
        return edges_in_trail


class HeuristicRiskEngine:
    """
    Ensemble Risk Engine combining 6 sub-scores per Figure 2.10:
      - Network (25%)
      - Physical (25%)
      - Rule-based (15%)
      - Behavioural (15%)
      - Temporal (10%)
      - Geographic (10%)
    Risk Tiers: Critical (>=80), High (60-79), Medium (35-59), Low (<35).
    """

    def __init__(self, digital_engine, physical_engine, network_engine, accounts, transactions):
        self.digital_engine = digital_engine
        self.physical_engine = physical_engine
        self.network_engine = network_engine
        self.accounts = accounts
        self.transactions = transactions

        self.rings = self.network_engine.detect_fraud_rings()
        self.ring_lookup = {}
        for r in self.rings:
            for m in r["members"]:
                self.ring_lookup[m] = r

    def evaluate_account(self, account_id):
        """Computes composite 0-100 ensemble score and natural-language justifications."""
        stats = self.network_engine.node_stats.get(account_id, {
            "in_degree": 0, "out_degree": 0, "total_in_amount": 0.0,
            "total_out_amount": 0.0, "amounts": [], "counterparties": set(), "timestamps": []
        })

        # 1. Rule-based Sub-score (15%)
        rule_score = 0
        rule_evidence = []
        amounts = stats["amounts"]
        if any(95000 <= amt < 100000 for amt in amounts):
            rule_score += 45
            rule_evidence.append("Structuring: Transaction amount just below ₹1,00,000 regulatory reporting threshold")

        velocity = stats["in_degree"] + stats["out_degree"]
        if velocity > 15:
            rule_score += 35
            rule_evidence.append(f"Excessive transaction velocity ({velocity} operations)")

        net_flow = stats["total_in_amount"] - stats["total_out_amount"]
        if net_flow < -50000:
            rule_score += 20
            rule_evidence.append("Heavy net cash drain (net outflow exceeding -₹50,000)")
        rule_score = min(100, rule_score)

        # 2. Behavioural Sub-score (15%)
        beh_score = 0
        beh_evidence = []
        if amounts:
            avg_amt = sum(amounts) / len(amounts)
            max_amt = max(amounts)
            if max_amt > 3 * avg_amt:
                beh_score += 50
                beh_evidence.append(f"Spike anomaly: Single transaction (₹{max_amt:,.2f}) > 3x mean (₹{avg_amt:,.2f})")
            if max_amt > 5 * avg_amt:
                beh_score += 30
                beh_evidence.append("Severe volume outlier exceeding 5x baseline profile")
        beh_score = min(100, beh_score)

        # 3. Network Sub-score (25%)
        dig_res = self.digital_engine.compute_digital_score(account_id)
        dig_score = dig_res["score"]
        mm_score = self.network_engine.compute_mastermind_score(account_id)
        is_ring_member = account_id in self.ring_lookup

        # Bounded network score: weighted digital footprint + mastermind centrality + cluster presence
        net_score = min(100.0, 0.55 * dig_score + 0.35 * mm_score + (10.0 if is_ring_member else 0.0))

        # 4. Temporal Sub-score (10%)
        temp_score = 0
        temp_evidence = []
        timestamps = stats["timestamps"]
        night_txns = 0
        for ts in timestamps:
            try:
                dt = datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
                if 1 <= dt.hour <= 4:
                    night_txns += 1
            except Exception:
                continue

        if night_txns > 0:
            temp_score += 50
            temp_evidence.append(f"Nocturnal financial activity ({night_txns} transactions between 01:00 and 04:00 AM)")
        if dig_res.get("burst_anomaly", False):
            temp_score += 50
            temp_evidence.append("Rapid burst clustering (<60s intervals)")
        temp_score = min(100, temp_score)

        # 5. Geographic Sub-score (10%)
        geo_score = 0
        geo_evidence = []
        acc_txs = [t for t in self.transactions if t.get("src_account") == account_id or t.get("dst_account") == account_id]
        hotspots = {"Jamtara", "Nuh", "Bharatpur", "Alwar", "Mathura"}
        for t in acc_txs:
            city = t.get("city", "")
            if any(h in city for h in hotspots):
                geo_score = 80
                geo_evidence.append(f"High-risk cybercrime hotspot transaction origin ({city})")
                break

        # 6. Physical Footprint Sub-score (25%)
        phys_res = self.physical_engine.compute_physical_score(account_id)
        phys_score = phys_res["score"]

        # Composite Ensemble Formula (Figure 2.10)
        # Network (25%) + Physical (25%) + Rule (15%) + Behavioural (15%) + Temporal (10%) + Geographic (10%)
        composite = (
            0.25 * net_score +
            0.25 * phys_score +
            0.15 * rule_score +
            0.15 * beh_score +
            0.10 * temp_score +
            0.10 * geo_score
        )
        composite = round(min(100.0, max(0.0, composite)), 1)

        # Risk Tiers (Chapter 2.2.3)
        if composite >= 80.0:
            tier = "Critical"
        elif composite >= 60.0:
            tier = "High"
        elif composite >= 35.0:
            tier = "Medium"
        else:
            tier = "Low"

        # 4-Class Taxonomy Mapping (Ground-Truth Independent)
        # Structural roles: Fraudster (sink/high score), Mule (pass-through layering),
        # Suspicious (moderate anomaly), Normal (baseline KYC)
        in_deg = stats.get("in_degree", 0)
        out_deg = stats.get("out_degree", 0)

        if composite >= 75.0 or (composite >= 60.0 and mm_score >= 50.0):
            tax_label = "Fraudster"
        elif composite >= 45.0 and (in_deg >= 1 and out_deg >= 1):
            tax_label = "Mule"
        elif composite >= 30.0 or is_ring_member or len(rule_evidence) > 0 or dig_res.get("burst_anomaly", False):
            tax_label = "Suspicious"
        else:
            tax_label = "Normal"

        all_evidence = dig_res["evidence"] + phys_res["evidence"] + rule_evidence + beh_evidence + temp_evidence + geo_evidence

        return {
            "account_id": account_id,
            "ensemble_score": composite,
            "risk_tier": tier,
            "taxonomy_label": tax_label,
            "sub_scores": {
                "network": round(net_score, 1),
                "physical": round(phys_score, 1),
                "rule_based": round(rule_score, 1),
                "behavioural": round(beh_score, 1),
                "temporal": round(temp_score, 1),
                "geographic": round(geo_score, 1)
            },
            "mastermind_score": mm_score,
            "detected_ring": self.ring_lookup.get(account_id, {}).get("ring_id", "NONE"),
            "evidence": all_evidence
        }


def build_money_trail_case(victim_acc, suspect_acc, data_context=None):
    """
    Reconstructs the full laundering chain: victim -> mules -> layering -> exit (Chapter 2, 3, 4).
    Overlays digital evidence, physical evidence, CCTV status, and running mastermind probability.
    """
    preset_cases = {
        "ACC00012": {
            "case_id": "CPS-RH/2026/07-FIR-281",
            "gd_entry": "GD No. 14A / PS Rohini Sec-17",
            "complainant": "Aarav Sharma",
            "phone": "+91-98112-40192",
            "typology_name": "Digital Arrest Scam with Hawala & ATM Exit",
            "total_incurred_loss": 94500.0,
            "hops": [
                {
                    "hop_index": 1,
                    "stage": "Victim Inception Drain",
                    "src": "ACC00012",
                    "dst": "ACC00142",
                    "amount": 94500.0,
                    "channel": "UPI (PhonePe)",
                    "utr": "UTR882910482019",
                    "timestamp": "2026-07-02 14:18:22",
                    "time_elapsed": "00:00:00 (Incident Trigger)",
                    "city": "Rohini Sector-17, Delhi",
                    "digital_overlap": "IP subnet 103.112.44.x; Browser FP match",
                    "physical_evidence": "Digital App Initiation (Rohini Branch jurisdiction)",
                    "cctv_status": "N/A (Pure Digital Rail)",
                    "cctv_days_left": None,
                    "coordinator_prob": 14.2,
                    "forensic_summary": "Direct social engineering transfer under coercion of fake law enforcement arrest warrant."
                },
                {
                    "hop_index": 2,
                    "stage": "Rapid Mule Layering (Smurfing)",
                    "src": "ACC00142",
                    "dst": "ACC00215",
                    "amount": 91200.0,
                    "channel": "IMPS",
                    "utr": "UTR994018274102",
                    "timestamp": "2026-07-02 14:20:07",
                    "time_elapsed": "+00:01:45 (Automated Layering)",
                    "city": "Nuh (Mewat), Haryana",
                    "digital_overlap": "Shared Hardware IMEI DEV_SHARED_004 (Linked to 6 mule accounts)",
                    "physical_evidence": "Cell Tower BTS: HR-NUH-088; Distance 118 km from Delhi",
                    "cctv_status": "N/A (IMPS Network)",
                    "cctv_days_left": None,
                    "coordinator_prob": 58.6,
                    "forensic_summary": "Zero balance retained; funds routed within 105 seconds to bypass automated fraud filters."
                },
                {
                    "hop_index": 3,
                    "stage": "Secondary Layering / Hawala Buffer",
                    "src": "ACC00215",
                    "dst": "ACC00310",
                    "amount": 87500.0,
                    "channel": "UPI (Paytm)",
                    "utr": "UTR104928374910",
                    "timestamp": "2026-07-02 14:23:40",
                    "time_elapsed": "+00:05:18",
                    "city": "Bharatpur, Rajasthan",
                    "digital_overlap": "Co-located IP cluster 103.22.18.99 (VPN Exit Node detected)",
                    "physical_evidence": "Cell Tower: RJ-BHP-102; Multiple SIM ICCID bindings",
                    "cctv_status": "N/A (UPI Network)",
                    "cctv_days_left": None,
                    "coordinator_prob": 72.1,
                    "forensic_summary": "Cheque kiting buffer account; customer KYC forged under deceased individual identity."
                },
                {
                    "hop_index": 4,
                    "stage": "Cash-Out Sink & ATM Dispersal",
                    "src": "ACC00310",
                    "dst": "ACC00148",
                    "amount": 84000.0,
                    "channel": "ATM Cash Withdrawal",
                    "utr": "ATM_TXN_0049182",
                    "timestamp": "2026-07-02 14:31:15",
                    "time_elapsed": "+00:12:53 (Physical Exit)",
                    "city": "Rohini Sector-17, Delhi",
                    "digital_overlap": "Shared Mastermind Control Node; Top Betweenness Centrality",
                    "physical_evidence": "ATM_0012 (Bank of Baroda, Sec-17 Rohini); Camera ID CAM_ATM_0012_01",
                    "cctv_status": "CRITICAL: Available - 18 Days Retention Left",
                    "cctv_days_left": 18,
                    "coordinator_prob": 88.5,
                    "forensic_summary": "Physical cash-out executed; CCTV footage preservation required under Section 94 BNSS immediately."
                }
            ]
        }
    }

    case = preset_cases.get(victim_acc)
    if not case:
        # Check if real path can be constructed from data_context
        net_engine = data_context.get("net_engine") if data_context else None
        real_hops = []
        if net_engine:
            trail_edges = net_engine.find_money_trail_edges(victim_acc, suspect_acc)
            for idx, edge in enumerate(trail_edges):
                dst_acc = edge["dst"]
                mm_sc = round(net_engine.compute_mastermind_score(dst_acc), 1)
                real_hops.append({
                    "hop_index": idx + 1,
                    "stage": f"Hop {idx + 1} Layering Flow",
                    "src": edge["src"],
                    "dst": dst_acc,
                    "amount": edge["amount"],
                    "channel": edge["channel"],
                    "utr": f"UTR_SYNTH_{edge['src'][-4:]}_{edge['dst'][-4:]}",
                    "timestamp": edge["timestamp"],
                    "time_elapsed": f"+00:{idx*2:02d}:00",
                    "city": "Synthetic Location",
                    "digital_overlap": "Extracted from transaction graph",
                    "physical_evidence": "Digital rail transfer",
                    "cctv_status": "N/A (Digital Transfer)",
                    "cctv_days_left": None,
                    "coordinator_prob": mm_sc,
                    "forensic_summary": f"Transaction trail hop {idx+1} from {edge['src']} to {dst_acc}."
                })

        total_loss = real_hops[0]["amount"] if real_hops else 0.0
        case = {
            "case_id": "SYNTH-DEMO/2026/CASE-001",
            "gd_entry": "Synthetic GD Entry (Demo)",
            "complainant": "Synthetic Complainant (Fictional)",
            "phone": "+91-00000-00000",
            "typology_name": "Multi-Hop Layering Chain (Discovered)",
            "total_incurred_loss": total_loss,
            "is_synthetic_demo": True,
            "disclaimer": "SYNTHETIC DEMO — NOT AN OFFICIAL POLICE RECORD",
            "hops": real_hops
        }

    case["victim_account"] = victim_acc
    case["sink_account"] = suspect_acc
    case["is_synthetic_demo"] = True
    case["disclaimer"] = "SYNTHETIC DEMO — NOT AN OFFICIAL POLICE RECORD"
    case["narrative"] = generate_investigation_narrative(case)
    return case


def generate_investigation_narrative(case):
    """Generates synthetic police case diary entry (Para 4 Fund Flow Analysis)."""
    hops = case.get("hops", [])
    victim = case.get("victim_account", "N/A")
    sink = case.get("sink_account", "N/A")
    total_amount = case.get("total_incurred_loss", 0.0)
    typology = case.get("typology_name", "Synthetic Cyber Crime Scenario")

    hop_summaries = []
    for h in hops:
        hop_summaries.append(
            f"Hop {h['hop_index']} ({h['src']} ➔ {h['dst']}): Amount ₹{h['amount']:,.2f} via {h['channel']} "
            f"[{h.get('time_elapsed', 'N/A')} elapsed]. Forensic note: {h.get('forensic_summary', 'N/A')}"
        )

    narrative = (
        f"*** SYNTHETIC DEMO — NOT AN OFFICIAL CASE RECORD ***\n"
        f"ACADEMIC RESEARCH PROTOTYPE // CASE DIARY ENTRY (Para 4 - Fund Flow Analysis)\n"
        f"----------------------------------------------------------------------------------------\n"
        f"Simulated complaint regarding fund movement totaling ₹{total_amount:,.2f} originating "
        f"from account {victim}. Network graph analysis traces the transaction path across {len(hops)} hops "
        f"terminating at candidate sink {sink}.\n\n"
        f"Scenario Typology: {typology}\n"
        f"Reconstructed Path:\n" + ("\n".join(hop_summaries) if hop_summaries else "  (No multi-hop path reconstructed)") + "\n\n"
        f"Forensic Conclusion: Flow exhibits rapid sequential money movement. "
        f"This is an automated software analysis of synthetic data for academic evaluation."
    )
    return narrative


def generate_legal_notice(case):
    """
    Generates Section 94 Bharatiya Nagarik Suraksha Sanhita (BNSS), 2023
    requisition notice template for banks and telecom providers.
    WATERMARKED AS SYNTHETIC DEMO.
    """
    cid = case.get("case_id", "SYNTH-DEMO/2026/07-FIR-281")
    gd = case.get("gd_entry", "Synthetic GD Reference")
    victim = case.get("victim_account", "ACC00012")
    complainant = case.get("complainant", "Synthetic Complainant")
    loss = case.get("total_incurred_loss", 94500.0)
    hops = case.get("hops", [])

    mule_accs = [h["dst"] for h in hops]
    utrs = [h.get("utr", "N/A") for h in hops]

    text = f"""========================================================================================
[SYNTHETIC DEMONSTRATION TEMPLATE — NOT AN OFFICIAL STATUTORY NOTICE]
ACADEMIC RESEARCH PROTOTYPE // FOR DEMONSTRATION AND EVALUATION PURPOSES ONLY
========================================================================================

Case / Requisition Ref: {cid}
Daily Diary (GD) Reference: {gd}
Date of Notice: Generated on System Evaluation Date

To:
  1. Nodal Officer / Fraud Risk Management (Simulated Commercial Banks)
  2. Nodal Officer, National Payments Corporation of India (Simulated)
  3. Telecom Nodal Officer (Simulated Service Providers)

Subject: Mandatory Production of Documents, Transaction Account Freezing, and Preservation
         of Digital/Physical CCTV Evidence in Simulated Cyber Financial Investigation.

WHEREAS, an analytical study into cyber financial fraud attribution has been conducted
using the Fin-Suraksha academic prototype pursuant to simulated complaint regarding
unauthorized debit amounting to Rs. {loss:,.2f} from Account No. {victim}.

AND WHEREAS, algorithmic network tracing through the Fin-Suraksha Console reveals that the
simulated fund flow was routed through the following beneficiary nodes:
  • Beneficiary Accounts: {', '.join(mule_accs) if mule_accs else 'N/A'}
  • Transaction Reference UTRs: {', '.join(utrs) if utrs else 'N/A'}

THEREFORE, under the statutory provisions of Section 94 BNSS, 2023:
  1. FREEZE / LIEN-MARK the entire credit balances in the above-mentioned accounts.
  2. PROVIDE complete Account Opening Forms (AOF), KYC documents, and account statements.
  3. PRESERVE AND PROVIDE IPDR / NAT logs showing port forwarding details.
  4. PRESERVE AND DISPATCH CCTV video footage from all referenced ATM terminals.

========================================================================================
[ACADEMIC DEMONSTRATION RECORD — NOT AN OFFICIAL POLICE DOCUMENT]
System-generated analytical template for educational evaluation.
Developer: Bhawna Vashisht | MAIMS (BCA Internship Project)
Host Organization: Cyber Police Station, Sector-17, Rohini, Delhi-110089 (Internship Host)
========================================================================================"""
    return text


def generate_case_pdf_report(case, output_path="fin_suraksha_case_report.pdf"):
    """
    Generates PDF Case Dossier using ReportLab (Chapter 2, Table 2.1 & 3.4).
    WATERMARKED AS SYNTHETIC DEMONSTRATION DOCUMENT.
    """
    if not HAS_REPORTLAB:
        return None

    doc = SimpleDocTemplate(output_path, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=13,
        textColor=colors.HexColor('#0f172a'),
        alignment=1,
        spaceAfter=4
    )
    watermark_style = ParagraphStyle(
        'Watermark',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#dc2626'),
        alignment=1,
        spaceAfter=6
    )
    subtitle_style = ParagraphStyle(
        'DocSub',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#475569'),
        alignment=1,
        spaceAfter=12
    )
    heading_style = ParagraphStyle(
        'SecHead',
        parent=styles['Heading2'],
        fontSize=10,
        textColor=colors.HexColor('#1e3a8a'),
        spaceBefore=8,
        spaceAfter=4
    )
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#1e293b')
    )

    story = []

    # Watermark Banner
    story.append(Paragraph("<b>*** SYNTHETIC DEMO — NOT AN OFFICIAL DOCUMENT ***</b>", watermark_style))
    story.append(Paragraph("<b>FIN-SURAKSHA: AI-ASSISTED FINANCIAL CRIME ATTRIBUTION CONSOLE</b>", title_style))
    story.append(Paragraph("Academic Research Prototype // Case Dossier // For Evaluation Only", subtitle_style))
    story.append(Spacer(1, 4))

    # Meta table
    meta_data = [
        [Paragraph("<b>Case Reference:</b>", body_style), Paragraph(str(case.get("case_id", "DEMO-CASE-001")), body_style),
         Paragraph("<b>GD Reference:</b>", body_style), Paragraph(str(case.get("gd_entry", "GD-DEMO")), body_style)],
        [Paragraph("<b>Complainant:</b>", body_style), Paragraph(str(case.get("complainant", "Synthetic Record")), body_style),
         Paragraph("<b>Incurred Loss:</b>", body_style), Paragraph(f"Rs. {case.get('total_incurred_loss', 0):,.2f}", body_style)],
        [Paragraph("<b>Typology:</b>", body_style), Paragraph(str(case.get("typology_name", "Synthetic Fraud")), body_style),
         Paragraph("<b>Project Scope:</b>", body_style), Paragraph("BCA Internship Project (MAIMS)", body_style)]
    ]
    meta_table = Table(meta_data, colWidths=[100, 170, 100, 170])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 10))

    # Money Trail Section
    story.append(Paragraph("<b>1. Multi-Hop Forensic Money Trail</b>", heading_style))
    hops = case.get("hops", [])
    trail_data = [["Hop", "Stage", "Source", "Destination", "Amount", "Channel", "Elapsed", "CCTV Status"]]
    for h in hops:
        trail_data.append([
            str(h.get("hop_index", "")),
            str(h.get("stage", ""))[:18],
            str(h.get("src", "")),
            str(h.get("dst", "")),
            f"Rs. {h.get('amount', 0):,.2f}",
            str(h.get("channel", ""))[:12],
            str(h.get("time_elapsed", ""))[:12],
            str(h.get("cctv_status", "N/A"))[:16]
        ])

    trail_table = Table(trail_data, colWidths=[25, 85, 70, 70, 65, 70, 70, 85])
    trail_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e3a8a')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTSIZE', (0,0), (-1,-1), 7),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(trail_table)
    story.append(Spacer(1, 10))

    # Case Diary Narrative
    story.append(Paragraph("<b>2. Analytical Narrative (Para 4 - Fund Flow Reconstruction)</b>", heading_style))
    story.append(Paragraph(case.get("narrative", "").replace("\n", "<br/>"), body_style))
    story.append(Spacer(1, 10))

    # System Disclaimer Notice (replacing fake officer signatures)
    story.append(Spacer(1, 10))
    disclaimer_data = [
        [Paragraph(
            "<b>SOFTWARE GENERATION NOTICE & DISCLAIMER:</b><br/>"
            "This document is an automated analytical output generated by the Fin-Suraksha Academic Prototype.<br/>"
            "All entities, transactions, and identifiers are synthetic. This dossier is prepared exclusively for "
            "academic evaluation and is <b>NOT</b> an official police document or legally admissible evidence.<br/>"
            "Developer: Bhawna Vashisht | Department of Computer Applications, MAIMS (Enrolment: 35114702024)",
            body_style
        )]
    ]
    disclaimer_table = Table(disclaimer_data, colWidths=[540])
    disclaimer_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#fef2f2')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#f87171')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(disclaimer_table)

    doc.build(story)
    return output_path
