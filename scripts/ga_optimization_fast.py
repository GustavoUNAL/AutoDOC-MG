#!/usr/bin/env python3
"""
Fast GA Optimization Script for All Scenarios
Configured for 1,000 generations for faster execution
"""

import os
import json
import math
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any

# Set random seeds for reproducibility
random.seed(42)

# =============== CONSTANTS (aligned with MATLAB) ===============
K = 0.14
N = 0.02

CTI = 0.20
MIN_TDS = 0.05
MAX_TDS = 0.8
MIN_PICKUP = 0.05
MAX_PICKUP_FACTOR = 0.6
MAX_TIME = 10.0

# GA (Chu & Beasley) — Fast configuration for testing
GA_Ni = 80
GA_iterno = 1000  # Reduced for faster execution
GA_maxGen = 1000  # Reduced for faster execution
GA_nMut = 2

print("🚀 FAST GA OPTIMIZATION - 1,000 GENERATIONS")
print("="*60)
print(f"📊 GA Parameters: Population={GA_Ni}, Max Generations={GA_maxGen} (FAST MODE)")
print(f"⚙️  Coordination: CTI={CTI}s, MIN_TDS={MIN_TDS}, MAX_TDS={MAX_TDS}")

def setup_paths():
    """Setup all necessary paths for the project"""
    project_root = Path(__file__).parent.parent
    
    paths = {
        'project_root': project_root,
        'data_raw': project_root / "data" / "raw",
        'data_processed': project_root / "data" / "processed",
        'results': project_root / "results",
        'figures': project_root / "results" / "figures",
        'reports': project_root / "results" / "reports",
        'tables': project_root / "results" / "tables",
        'input_file': project_root / "data" / "raw" / "automation_results.json"
    }
    
    # Create directories if they don't exist
    for path_name, path in paths.items():
        if path_name not in ['input_file']:
            path.mkdir(parents=True, exist_ok=True)
    
    return paths

def get_numeric_field(dct: Dict, names: List[str]) -> Optional[float]:
    """Extract numeric field from dictionary with multiple possible keys"""
    for n in names:
        if n in dct:
            try:
                return float(dct[n])
            except (ValueError, TypeError):
                pass
    return None

def time_iec(I: float, PU: float, TDS: float) -> float:
    """Calculate IEC relay operating time"""
    if I is None or PU is None or TDS is None:
        return float("nan")
    try:
        M = I / PU
        denom = (M**N) - 1.0
        if denom <= 0:
            return float("inf")
        return (K * TDS) / denom
    except (ZeroDivisionError, OverflowError):
        return float("nan")

def store_initial_setting(initial: Dict, relay_info: Dict) -> None:
    """Store initial relay settings for comparison"""
    name = str(relay_info.get("relay", "")).strip()
    if not name or name in initial:
        return
    tds = get_numeric_field(relay_info, ["TDS", "tds"])
    pu = get_numeric_field(relay_info, ["pick_up", "pickup"])
    if tds is not None or pu is not None:
        initial[name] = {"TDS_initial": tds, "pickup_initial": pu}

def group_data_by_scenario(data_array: List[Dict]) -> Dict[str, Dict]:
    """Group relay pairs by scenario and validate data"""
    scenario_map = {}
    
    for entry in data_array:
        sid = entry.get("scenario_id")
        main_relay = entry.get("main_relay")
        backup_relay = entry.get("backup_relay")
        
        if not sid or not main_relay or not backup_relay:
            continue
            
        mname = str(main_relay.get("relay", "")).strip()
        bname = str(backup_relay.get("relay", "")).strip()
        
        if not mname or not bname:
            continue
            
        # Extract fault currents
        im = get_numeric_field(main_relay, ["Ishc", "I_shc", "Isc", "fault_current"])
        ib = get_numeric_field(backup_relay, ["Ishc", "I_shc", "Isc", "fault_current"])
        
        if not im or not ib or im <= 0 or ib <= 0:
            continue
            
        # Initialize scenario if not exists
        if sid not in scenario_map:
            scenario_map[sid] = {
                "pairs": [],
                "relays": [],
                "initial_settings": {},
                "fault_types": set()
            }
            
        # Add pair information
        scenario_map[sid]["pairs"].append({
            "main_relay": mname,
            "backup_relay": bname,
            "Ishc_main": im,
            "Ishc_backup": ib,
            "fault": entry.get("fault", "unknown")
        })
        
        # Track unique relays
        if mname not in scenario_map[sid]["relays"]:
            scenario_map[sid]["relays"].append(mname)
        if bname not in scenario_map[sid]["relays"]:
            scenario_map[sid]["relays"].append(bname)
            
        # Store initial settings
        store_initial_setting(scenario_map[sid]["initial_settings"], main_relay)
        store_initial_setting(scenario_map[sid]["initial_settings"], backup_relay)
        
        # Track fault types
        scenario_map[sid]["fault_types"].add(entry.get("fault", "unknown"))
    
    # Convert sets to lists for JSON serialization
    for sid in scenario_map:
        scenario_map[sid]["fault_types"] = list(scenario_map[sid]["fault_types"])
    
    return scenario_map

def validate_scenario_data(scenario_data: Dict) -> Tuple[bool, List[str]]:
    """Validate scenario data and return issues"""
    issues = []
    
    if not scenario_data.get("pairs"):
        issues.append("No valid pairs found")
        return False, issues
        
    if not scenario_data.get("relays"):
        issues.append("No relays identified")
        return False, issues
        
    # Check for minimum data requirements
    if len(scenario_data["pairs"]) < 5:
        issues.append(f"Too few pairs ({len(scenario_data['pairs'])})")
        
    if len(scenario_data["relays"]) < 3:
        issues.append(f"Too few relays ({len(scenario_data['relays'])})")
        
    return len(issues) == 0, issues

def genetic_algorithm_optimization(scenario_id: str, scenario_data: Dict) -> Dict[str, Dict]:
    """Genetic Algorithm optimization for relay coordination"""
    pairs = scenario_data["pairs"]
    relays = [r for r in scenario_data["relays"] if str(r).strip()]
    nR = len(relays)
    
    if nR == 0:
        print(f'    ❌ Scenario "{scenario_id}" has no valid relays.')
        return {}

    # Create relay index mapping
    idx = {relays[i]: i for i in range(nR)}

    # Calculate minimum Isc per relay for bounds
    IscMin = [float("inf")] * nR
    for p in pairs:
        main_idx = idx[p["main_relay"]]
        backup_idx = idx[p["backup_relay"]]
        IscMin[main_idx] = min(IscMin[main_idx], p["Ishc_main"])
        IscMin[backup_idx] = min(IscMin[backup_idx], p["Ishc_backup"])

    # Define bounds
    xmin = ([MIN_TDS] * nR) + ([MIN_PICKUP] * nR)
    xmax = ([MAX_TDS] * nR) + ([MAX_PICKUP_FACTOR * IscMin[i] for i in range(nR)])
    Nv = 2 * nR  # Number of variables (TDS + pickup for each relay)

    def relay_time(I: float, PU: float, TDS: float) -> float:
        """Calculate relay operating time with penalty for invalid conditions"""
        if I <= PU:
            return MAX_TIME * 10.0  # penalty
        try:
            t = TDS * (K / ((I / PU) ** N - 1.0))
            return min(max(t, 0.0), MAX_TIME * 10.0)
        except (ZeroDivisionError, OverflowError):
            return MAX_TIME * 10.0

    def fitness(individual: List[float]) -> float:
        """Calculate fitness function (TMT - Total Miscoordination Time)"""
        tds = individual[:nR]
        pu = individual[nR:]
        tmt = 0.0
        
        for p in pairs:
            mi = idx[p["main_relay"]]
            bi = idx[p["backup_relay"]]
            
            tM = relay_time(p["Ishc_main"], pu[mi], tds[mi])
            tB = relay_time(p["Ishc_backup"], pu[bi], tds[bi])
            
            # CTI violation penalty
            if (tB - tM) < CTI:
                tmt += (CTI - (tB - tM))
            
            # Time limit penalty
            if tM > MAX_TIME:
                tmt += (tM - MAX_TIME)
                
        return tmt

    # Initialize population
    X = []
    for _ in range(GA_Ni):
        individual = [xmin[j] + random.random() * (xmax[j] - xmin[j]) for j in range(Nv)]
        X.append(individual + [fitness(individual)])
    
    X.sort(key=lambda r: r[Nv])  # Sort by fitness
    X_best = X[0][:]
    
    print(f'    🔄 GA: generation 0  – TMT = {X_best[Nv]:.6f}')

    # Evolution loop
    stall = 0
    for gen in range(1, GA_maxGen + 1):
        # Selection and crossover
        s1, s2 = random.sample(range(GA_Ni), 2)
        P1 = X[s1][:Nv]
        P2 = X[s2][:Nv]
        cp = random.randint(1, Nv - 1)
        H1 = P1[:cp] + P2[cp:]
        H2 = P2[:cp] + P1[cp:]

        def mutate(child: List[float]) -> List[float]:
            """Apply mutation to child"""
            for m in random.sample(range(Nv), GA_nMut):
                child[m] = xmin[m] + random.random() * (xmax[m] - xmin[m])
            return child

        H1 = mutate(H1)
        H2 = mutate(H2)
        f1 = fitness(H1)
        f2 = fitness(H2)

        # Replacement strategy
        candidates = [(H1, f1), (H2, f2)]
        candidates.sort(key=lambda t: t[1])
        child, fchild = candidates[0]
        
        if fchild < X[-1][Nv]:
            # Check for duplicates
            duplicate = any(
                all(abs(child[j] - X[k][j]) < 1e-12 for j in range(Nv))
                for k in range(GA_Ni)
            )
            if not duplicate:
                X[-1] = child + [fchild]

        X.sort(key=lambda r: r[Nv])
        
        # Update best solution
        if X[0][Nv] < X_best[Nv]:
            X_best = X[0][:]
            stall = 0
        else:
            stall += 1

        # Progress reporting (every 100 generations for fast mode)
        if gen % 100 == 0:
            print(f'    🔄 GA: generation {gen} – TMT = {X_best[Nv]:.6f}')
            
        # Stopping criteria
        if X_best[Nv] == 0.0:
            print(f'    ✅ Perfect solution found at generation {gen}')
            break
        if stall >= GA_iterno:
            print(f'    ⚠️  Stagnation ({GA_iterno} generations without improvement)')
            break

    print(f'    🏁 GA finished. Generations: {gen}  – Best TMT = {X_best[Nv]:.6f}')
    
    # Extract optimized values
    best = X_best[:Nv]
    TDSbest = best[:nR]
    PUbest = best[nR:]
    
    optimized = {
        relays[r]: {
            "TDS": round(TDSbest[r], 5),
            "pickup": round(PUbest[r], 5)
        }
        for r in range(nR)
    }
    
    return optimized

def optimize_all_scenarios(paths: Dict) -> Dict[str, Any]:
    """Optimize all scenarios using GA and return comprehensive results"""
    print("🚀 Starting comprehensive GA optimization for all scenarios...")
    
    # Load input data
    print(f"📂 Loading data from: {paths['input_file']}")
    with open(paths['input_file'], "r", encoding="utf-8") as f:
        raw_data = json.load(f)
    
    if not isinstance(raw_data, list):
        raise TypeError("Input JSON must be a list of relay pairs")
    
    print(f"📊 Loaded {len(raw_data)} relay pairs from JSON")
    
    # Group data by scenario
    print("🔄 Grouping data by scenario...")
    scenario_map = group_data_by_scenario(raw_data)
    scenario_ids = sorted(scenario_map.keys(), key=lambda x: int(x.split('_')[1]) if x.split('_')[1].isdigit() else 999)
    
    print(f"📋 Found {len(scenario_ids)} scenarios: {', '.join(scenario_ids)}")
    
    # Initialize results tracking
    results = {
        'optimization_results': {},
        'scenario_statistics': {},
        'optimization_summary': {
            'total_scenarios': len(scenario_ids),
            'successful_optimizations': 0,
            'failed_optimizations': 0,
            'skipped_scenarios': 0,
            'processing_time': 0
        },
        'timestamp': datetime.now(timezone.utc).isoformat()
    }
    
    start_time = datetime.now()
    
    # Process each scenario
    for i, sid in enumerate(scenario_ids, 1):
        data = scenario_map[sid]
        print(f"\n{'='*60}")
        print(f"🎯 Scenario {i}/{len(scenario_ids)}: {sid}")
        print(f"   📊 Pairs: {len(data['pairs'])}, Relays: {len(data['relays'])}")
        print(f"   🔧 Fault types: {data['fault_types']}")
        
        # Validate scenario data
        is_valid, issues = validate_scenario_data(data)
        if not is_valid:
            print(f"   ❌ Skipping scenario {sid}: {', '.join(issues)}")
            results['optimization_summary']['skipped_scenarios'] += 1
            results['scenario_statistics'][sid] = {
                'status': 'skipped',
                'issues': issues,
                'pairs_count': len(data['pairs']),
                'relays_count': len(data['relays'])
            }
            continue
        
        try:
            # Run GA optimization
            print(f"   🔬 Running GA optimization...")
            optimized_values = genetic_algorithm_optimization(sid, data)
            
            if optimized_values:
                results['optimization_results'][sid] = {
                    'scenario_id': sid,
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'relay_values': optimized_values,
                    'initial_settings': data['initial_settings'],
                    'pairs_count': len(data['pairs']),
                    'relays_count': len(data['relays']),
                    'fault_types': data['fault_types']
                }
                
                results['optimization_summary']['successful_optimizations'] += 1
                results['scenario_statistics'][sid] = {
                    'status': 'success',
                    'pairs_count': len(data['pairs']),
                    'relays_count': len(data['relays']),
                    'optimized_relays': len(optimized_values)
                }
                
                print(f"   ✅ Optimization successful: {len(optimized_values)} relays optimized")
            else:
                print(f"   ❌ Optimization failed: No results produced")
                results['optimization_summary']['failed_optimizations'] += 1
                results['scenario_statistics'][sid] = {
                    'status': 'failed',
                    'pairs_count': len(data['pairs']),
                    'relays_count': len(data['relays']),
                    'error': 'No optimization results'
                }
                
        except Exception as e:
            print(f"   ❌ Optimization failed with error: {str(e)}")
            results['optimization_summary']['failed_optimizations'] += 1
            results['scenario_statistics'][sid] = {
                'status': 'error',
                'pairs_count': len(data['pairs']),
                'relays_count': len(data['relays']),
                'error': str(e)
            }
    
    # Calculate processing time
    end_time = datetime.now()
    processing_time = (end_time - start_time).total_seconds()
    results['optimization_summary']['processing_time'] = processing_time
    
    print(f"\n{'='*60}")
    print("🏁 OPTIMIZATION SUMMARY")
    print(f"   ⏱️  Total processing time: {processing_time:.2f} seconds")
    print(f"   ✅ Successful optimizations: {results['optimization_summary']['successful_optimizations']}")
    print(f"   ❌ Failed optimizations: {results['optimization_summary']['failed_optimizations']}")
    print(f"   ⏭️  Skipped scenarios: {results['optimization_summary']['skipped_scenarios']}")
    print(f"   📊 Success rate: {results['optimization_summary']['successful_optimizations']/len(scenario_ids)*100:.1f}%")
    
    return results

def save_optimization_results(results: Dict[str, Any], paths: Dict) -> Dict[str, str]:
    """Save optimization results in organized structure"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    saved_files = {}
    
    print("💾 Saving optimization results...")
    
    # 1. Save comprehensive results file
    comprehensive_file = paths['data_processed'] / f"ga_optimization_all_scenarios_comprehensive_{timestamp}.json"
    with open(comprehensive_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    saved_files['comprehensive_results'] = str(comprehensive_file)
    print(f"   📄 Comprehensive results: {comprehensive_file}")
    
    # 2. Save individual scenario optimization files
    for scenario_id, scenario_result in results['optimization_results'].items():
        scenario_file = paths['data_processed'] / f"optimized_relay_values_{scenario_id}_GA_{timestamp}.json"
        with open(scenario_file, "w", encoding="utf-8") as f:
            json.dump([scenario_result], f, indent=2, ensure_ascii=False)
        saved_files[f'scenario_{scenario_id}'] = str(scenario_file)
    
    print(f"   📄 Individual scenario files: {len(results['optimization_results'])} files saved")
    
    # 3. Save optimization summary as JSON
    summary_file = paths['tables'] / f"ga_optimization_summary_{timestamp}.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(results['optimization_summary'], f, indent=2, ensure_ascii=False)
    saved_files['summary_json'] = str(summary_file)
    print(f"   📊 Summary JSON: {summary_file}")
    
    return saved_files

def update_relay_pairs_with_optimization(raw_data: List[Dict], results: Dict[str, Any], paths: Dict) -> Dict[str, str]:
    """Update relay pairs with optimized settings and save organized files"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    saved_files = {}
    
    print("🔄 Updating relay pairs with optimized settings...")
    
    # Create optimization mapping by scenario
    opt_mapping = {}
    for scenario_id, scenario_result in results['optimization_results'].items():
        opt_mapping[scenario_id] = {
            name: (vals["pickup"], vals["TDS"])
            for name, vals in scenario_result['relay_values'].items()
        }
    
    # Group data by scenario for processing
    scenario_groups = {}
    for entry in raw_data:
        sid = entry.get("scenario_id")
        if sid not in scenario_groups:
            scenario_groups[sid] = []
        scenario_groups[sid].append(entry)
    
    # Update each scenario's pairs
    for scenario_id, scenario_pairs in scenario_groups.items():
        if scenario_id not in opt_mapping:
            print(f"   ⚠️  No optimization results for {scenario_id}, skipping...")
            continue
            
        opt_map = opt_mapping[scenario_id]
        updated_pairs = []
        
        for pair in scenario_pairs:
            # Update main relay
            main_relay = pair.get("main_relay", {})
            main_name = main_relay.get("relay")
            if main_name in opt_map:
                pu, tds = opt_map[main_name]
                main_relay["pick_up"] = pu
                main_relay["TDS"] = tds
                ishc_m = get_numeric_field(main_relay, ["Ishc", "I_shc", "Isc", "fault_current"])
                if ishc_m:
                    main_relay["Time_out"] = time_iec(ishc_m, pu, tds)
            
            # Update backup relay
            backup_relay = pair.get("backup_relay", {})
            backup_name = backup_relay.get("relay")
            if backup_name in opt_map:
                pu, tds = opt_map[backup_name]
                backup_relay["pick_up"] = pu
                backup_relay["TDS"] = tds
                ishc_b = get_numeric_field(backup_relay, ["Ishc", "I_shc", "Isc", "fault_current"])
                if ishc_b:
                    backup_relay["Time_out"] = time_iec(ishc_b, pu, tds)
            
            updated_pairs.append(pair)
        
        # Save updated pairs for this scenario
        scenario_file = paths['data_processed'] / f"automation_results_{scenario_id}_optimized_{timestamp}.json"
        with open(scenario_file, "w", encoding="utf-8") as f:
            json.dump(updated_pairs, f, indent=2, ensure_ascii=False)
        saved_files[f'optimized_pairs_{scenario_id}'] = str(scenario_file)
        
        print(f"   ✅ Updated {len(updated_pairs)} pairs for {scenario_id}")
    
    print(f"   📄 Saved {len(saved_files)} optimized pair files")
    return saved_files

def main():
    """Main execution function"""
    print("🚀 INITIALIZING FAST GA OPTIMIZATION")
    print("="*60)
    
    paths = setup_paths()
    print(f"📁 Project root: {paths['project_root']}")
    print(f"📂 Input file: {paths['input_file']}")
    print(f"💾 Output directory: {paths['data_processed']}")
    print(f"📊 Results directory: {paths['results']}")
    
    # Check if input file exists
    if not paths['input_file'].exists():
        raise FileNotFoundError(f"Input file not found: {paths['input_file']}")
    
    print(f"\n✅ All paths validated successfully")
    print("="*60)
    
    try:
        # Perform batch optimization
        optimization_results = optimize_all_scenarios(paths)
        
        # Save optimization results
        print(f"\n{'='*60}")
        print("💾 SAVING OPTIMIZATION RESULTS")
        print("="*60)
        
        saved_files = save_optimization_results(optimization_results, paths)
        
        # Update relay pairs with optimized settings
        print(f"\n{'='*60}")
        print("🔄 UPDATING RELAY PAIRS")
        print("="*60)
        
        # Load raw data for updating pairs
        with open(paths['input_file'], "r", encoding="utf-8") as f:
            raw_data = json.load(f)
        
        updated_files = update_relay_pairs_with_optimization(raw_data, optimization_results, paths)
        
        # Final summary
        print(f"\n{'='*60}")
        print("🎉 OPTIMIZATION COMPLETED SUCCESSFULLY!")
        print("="*60)
        
        summary = optimization_results['optimization_summary']
        print(f"📊 FINAL STATISTICS:")
        print(f"   • Total scenarios processed: {summary['total_scenarios']}")
        print(f"   • Successful optimizations: {summary['successful_optimizations']}")
        print(f"   • Failed optimizations: {summary['failed_optimizations']}")
        print(f"   • Skipped scenarios: {summary['skipped_scenarios']}")
        print(f"   • Success rate: {summary['successful_optimizations']/summary['total_scenarios']*100:.1f}%")
        print(f"   • Processing time: {summary['processing_time']:.2f} seconds")
        print(f"   • Files generated: {len(saved_files) + len(updated_files)}")
        
        print(f"\n📁 GENERATED FILES:")
        all_files = {**saved_files, **updated_files}
        for file_type, file_path in all_files.items():
            print(f"   • {file_type}: {file_path}")
        
        print(f"\n✅ All operations completed successfully!")
        
    except Exception as e:
        print(f"\n❌ ERROR during optimization: {str(e)}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    main()
