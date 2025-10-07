#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to optimize ALL 68 scenarios using Genetic Algorithm
This script will generate optimized relay settings for each scenario
"""

import os
import json
import math
import random
from datetime import datetime, timezone
from pathlib import Path
import numpy as np

# ================== CONSTANTS (IEC / GA) ==================
K = 0.14
N = 0.02
CTI = 0.20
MIN_TDS = 0.05
MAX_TDS = 0.8
MIN_PICKUP = 0.05
MAX_PICKUP_FACTOR = 0.6
MAX_TIME = 10.0

# GA (Chu & Beasley style)
GA_Ni = 80
GA_iterno = 50000
GA_maxGen = 50000
GA_nMut = 2

def get_numeric_field(dct, names):
    """Extract numeric field from dictionary."""
    for n in names:
        if n in dct:
            try:
                return float(dct[n])
            except:
                pass
    return None

def time_iec(I, PU, TDS):
    """IEC time calculation."""
    if I is None or PU is None or TDS is None:
        return float("nan")
    try:
        M = I/PU
        denom = (M**N) - 1.0
        if denom <= 0:
            return float("inf")
        return (K*TDS)/denom
    except Exception:
        return float("nan")

def group_data_by_scenario(data_array):
    """Group data by scenario."""
    scenario_map = {}
    for entry in data_array:
        sid = entry.get("scenario_id")
        m = entry.get("main_relay")
        b = entry.get("backup_relay")
        if not sid or not m or not b:
            continue
        
        mname = str(m.get("relay","")).strip()
        bname = str(b.get("relay","")).strip()
        if not mname or not bname:
            continue
        
        im = get_numeric_field(m, ["Ishc","I_shc","Isc","fault_current"])
        ib = get_numeric_field(b, ["Ishc","I_shc","Isc","fault_current"])
        if not im or not ib or im<=0 or ib<=0:
            continue
        
        if sid not in scenario_map:
            scenario_map[sid] = {"pairs": [], "relays": [], "initial_settings": {}}
        
        scenario_map[sid]["pairs"].append({
            "main_relay": mname,
            "backup_relay": bname,
            "Ishc_main": im,
            "Ishc_backup": ib
        })
        
        if mname not in scenario_map[sid]["relays"]:
            scenario_map[sid]["relays"].append(mname)
        if bname not in scenario_map[sid]["relays"]:
            scenario_map[sid]["relays"].append(bname)
    
    return scenario_map

def genetic_algorithm(scenarioID, scenarioData):
    """Genetic Algorithm optimization for a single scenario."""
    pairs = scenarioData["pairs"]
    relays = [r for r in scenarioData["relays"] if str(r).strip()]
    nR = len(relays)
    
    if nR == 0:
        print(f'Scenario "{scenarioID}" has no valid relays.')
        return {}
    
    idx = {relays[i]: i for i in range(nR)}
    
    # Calculate minimum Isc for each relay
    IscMin = [float("inf")]*nR
    for p in pairs:
        IscMin[idx[p["main_relay"]]] = min(IscMin[idx[p["main_relay"]]], p["Ishc_main"])
        IscMin[idx[p["backup_relay"]]] = min(IscMin[idx[p["backup_relay"]]], p["Ishc_backup"])
    
    # Define bounds
    xmin = ([MIN_TDS]*nR) + ([MIN_PICKUP]*nR)
    xmax = ([MAX_TDS]*nR) + ([MAX_PICKUP_FACTOR*IscMin[i] for i in range(nR)])
    Nv = 2*nR
    
    def relay_time(I, PU, TDS):
        if I <= PU:
            return MAX_TIME*10.0
        t = TDS * (K / ((I/PU)**N - 1.0))
        return min(max(t,0.0), MAX_TIME*10.0)
    
    def fitness(ind):
        tds = ind[:nR]
        pu = ind[nR:]
        tmt = 0.0
        
        for p in pairs:
            mi = idx[p["main_relay"]]
            bi = idx[p["backup_relay"]]
            tM = relay_time(p["Ishc_main"], pu[mi], tds[mi])
            tB = relay_time(p["Ishc_backup"], pu[bi], tds[bi])
            
            if (tB - tM) < CTI:
                tmt += (CTI - (tB - tM))
            if tM > MAX_TIME:
                tmt += (tM - MAX_TIME)
        
        return tmt
    
    # Initial population
    X = []
    for _ in range(GA_Ni):
        ind = [xmin[j] + random.random()*(xmax[j]-xmin[j]) for j in range(Nv)]
        X.append(ind + [fitness(ind)])
    
    X.sort(key=lambda r: r[Nv])
    X_best = X[0][:]
    
    print(f'  GA: Generation 0 - TMT = {X_best[Nv]:.6f}')
    stall = 0
    
    for gen in range(1, GA_maxGen+1):
        # Selection and crossover
        s1, s2 = random.sample(range(GA_Ni), 2)
        P1 = X[s1][:Nv]
        P2 = X[s2][:Nv]
        cp = random.randint(1, Nv-1)
        H1 = P1[:cp] + P2[cp:]
        H2 = P2[:cp] + P1[cp:]
        
        # Mutation
        def mutate(ch):
            for m in random.sample(range(Nv), GA_nMut):
                ch[m] = xmin[m] + random.random()*(xmax[m]-xmin[m])
            return ch
        
        H1 = mutate(H1)
        H2 = mutate(H2)
        f1 = fitness(H1)
        f2 = fitness(H2)
        
        # Replacement
        cand = [(H1,f1),(H2,f2)]
        cand.sort(key=lambda t: t[1])
        child, fchild = cand[0]
        
        if fchild < X[-1][Nv]:
            duplicate = any(all(abs(child[j]-X[k][j]) < 1e-12 for j in range(Nv)) for k in range(GA_Ni))
            if not duplicate:
                X[-1] = child + [fchild]
                X.sort(key=lambda r: r[Nv])
                
                if X[0][Nv] < X_best[Nv]:
                    X_best = X[0][:]
                    stall = 0
                else:
                    stall += 1
        
        if gen % 100 == 0:
            print(f'  GA: Generation {gen} - TMT = {X_best[Nv]:.6f}')
        
        if X_best[Nv] == 0.0:
            break
        
        if stall >= GA_iterno:
            print(f'  GA: Stagnation ({GA_iterno} generations without improvement).')
            break
    
    print(f'  GA completed. Generations: {gen} - Best TMT = {X_best[Nv]:.6f}')
    
    best = X_best[:Nv]
    TDSbest = best[:nR]
    PUbest = best[nR:]
    
    optimized = {
        relays[r]: {
            "TDS": round(TDSbest[r], 5),
            "pickup": round(PUbest[r], 5)
        } for r in range(nR)
    }
    
    return optimized

def optimize_all_scenarios():
    """Optimize all scenarios and save results."""
    print("🚀 Starting optimization of ALL 68 scenarios...")
    
    # Load data
    data_file = Path("data/raw/automation_results.json")
    with open(data_file, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
    
    print(f"✅ Loaded {len(raw_data)} relay pairs")
    
    # Group by scenario
    scenario_map = group_data_by_scenario(raw_data)
    scenario_ids = sorted(list(scenario_map.keys()))
    
    print(f"📊 Found {len(scenario_ids)} scenarios: {scenario_ids}")
    
    # Create output directories
    processed_dir = Path("data/processed")
    processed_dir.mkdir(parents=True, exist_ok=True)
    
    # Optimize each scenario
    all_optimized = {}
    successful_optimizations = 0
    
    for i, scenario_id in enumerate(scenario_ids, 1):
        print(f"\n{'='*60}")
        print(f"🔧 Optimizing scenario {i}/{len(scenario_ids)}: {scenario_id}")
        print(f"{'='*60}")
        
        scenario_data = scenario_map[scenario_id]
        print(f"  Pairs: {len(scenario_data['pairs'])}")
        print(f"  Relays: {len(scenario_data['relays'])}")
        
        if not scenario_data["pairs"]:
            print(f"  ⚠️  No valid pairs for {scenario_id}. Skipping...")
            continue
        
        try:
            # Run genetic algorithm
            optimized_values = genetic_algorithm(scenario_id, scenario_data)
            
            if optimized_values:
                all_optimized[scenario_id] = optimized_values
                successful_optimizations += 1
                print(f"  ✅ {scenario_id} optimized successfully. {len(optimized_values)} relays optimized.")
                
                # Save individual scenario optimization
                opt_file = processed_dir / f"optimized_relay_values_{scenario_id}_GA.json"
                with open(opt_file, 'w', encoding='utf-8') as f:
                    json.dump([{
                        "scenario_id": scenario_id,
                        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                        "relay_values": optimized_values
                    }], f, indent=2, ensure_ascii=False)
                
                # Update pairs with optimized values
                updated_pairs = []
                for pair in raw_data:
                    if pair.get('scenario_id') == scenario_id:
                        # Update main relay
                        main_name = pair['main_relay'].get('relay')
                        if main_name in optimized_values:
                            pair['main_relay']['TDS'] = optimized_values[main_name]['TDS']
                            pair['main_relay']['pick_up'] = optimized_values[main_name]['pickup']
                            ishc_m = get_numeric_field(pair['main_relay'], ["Ishc","I_shc","Isc","fault_current"])
                            pair['main_relay']['Time_out'] = time_iec(ishc_m, optimized_values[main_name]['pickup'], optimized_values[main_name]['TDS'])
                        
                        # Update backup relay
                        backup_name = pair['backup_relay'].get('relay')
                        if backup_name in optimized_values:
                            pair['backup_relay']['TDS'] = optimized_values[backup_name]['TDS']
                            pair['backup_relay']['pick_up'] = optimized_values[backup_name]['pickup']
                            ishc_b = get_numeric_field(pair['backup_relay'], ["Ishc","I_shc","Isc","fault_current"])
                            pair['backup_relay']['Time_out'] = time_iec(ishc_b, optimized_values[backup_name]['pickup'], optimized_values[backup_name]['TDS'])
                        
                        updated_pairs.append(pair)
                
                # Save optimized pairs for this scenario
                pairs_file = processed_dir / f"automation_results_{scenario_id}_optimized.json"
                with open(pairs_file, 'w', encoding='utf-8') as f:
                    json.dump(updated_pairs, f, indent=2, ensure_ascii=False)
                
                print(f"  💾 Saved: {opt_file.name} and {pairs_file.name}")
            else:
                print(f"  ❌ Optimization failed for {scenario_id}")
        
        except Exception as e:
            print(f"  ❌ Error optimizing {scenario_id}: {e}")
    
    # Save comprehensive results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    comprehensive_file = processed_dir / f"all_scenarios_optimization_results_{timestamp}.json"
    
    comprehensive_results = []
    for scenario_id, relay_values in all_optimized.items():
        comprehensive_results.append({
            "scenario_id": scenario_id,
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "relay_values": relay_values
        })
    
    with open(comprehensive_file, 'w', encoding='utf-8') as f:
        json.dump(comprehensive_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n🎉 Optimization completed!")
    print(f"📊 Summary:")
    print(f"  Total scenarios: {len(scenario_ids)}")
    print(f"  Successfully optimized: {successful_optimizations}")
    print(f"  Failed optimizations: {len(scenario_ids) - successful_optimizations}")
    print(f"  Success rate: {successful_optimizations/len(scenario_ids)*100:.1f}%")
    print(f"📁 Results saved in: {processed_dir}")
    print(f"📄 Comprehensive results: {comprehensive_file.name}")
    
    return all_optimized

if __name__ == "__main__":
    # Set random seed for reproducibility
    random.seed(42)
    np.random.seed(42)
    
    # Run optimization
    optimized_results = optimize_all_scenarios()
