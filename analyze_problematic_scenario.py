#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análisis detallado del escenario con peor TMT después de la optimización
Scenario: scenario_2
"""

import json
import os
from pathlib import Path
from datetime import datetime
from collections import defaultdict

def load_data(file_path):
    """Load JSON data from file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def calculate_dt_values(pairs, cti=0.2):
    """Calculate DT values for all pairs."""
    dt_values = []
    pair_details = []
    
    for i, pair in enumerate(pairs):
        main_relay = pair.get('main_relay', {})
        backup_relay = pair.get('backup_relay', {})
        
        time_main = main_relay.get('Time_out', 0)
        time_backup = backup_relay.get('Time_out', 0)
        
        if isinstance(time_main, (int, float)) and isinstance(time_backup, (int, float)):
            dt = (time_backup - time_main) - cti
            dt_values.append(dt)
            
            pair_details.append({
                'pair_id': i + 1,
                'main_relay': main_relay.get('relay', 'Unknown'),
                'backup_relay': backup_relay.get('relay', 'Unknown'),
                'time_main': time_main,
                'time_backup': time_backup,
                'dt': dt,
                'coordinated': dt >= 0,
                'tds_main': main_relay.get('TDS', 0),
                'tds_backup': backup_relay.get('TDS', 0),
                'pickup_main': main_relay.get('pick_up', 0),
                'pickup_backup': backup_relay.get('pick_up', 0)
            })
    
    return dt_values, pair_details

def analyze_problematic_scenario():
    """Analyze scenario_2 in detail."""
    print("🔍 Analyzing problematic scenario: scenario_2")
    print("=" * 60)
    
    # Setup paths
    project_root = Path.cwd()
    original_file = project_root / "data" / "raw" / "automation_results.json"
    optimized_file = project_root / "data" / "processed" / "automation_results_scenario_2_optimized.json"
    results_dir = project_root / "results"
    reports_dir = results_dir / "reports"
    
    # Create directories
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    # Load data
    print("📊 Loading data...")
    original_data = load_data(original_file)
    optimized_data = load_data(optimized_file)
    
    # Filter for scenario_2
    original_pairs = [pair for pair in original_data if pair.get('scenario_id') == 'scenario_2']
    optimized_pairs = [pair for pair in optimized_data if pair.get('scenario_id') == 'scenario_2']
    
    print(f"✅ Found {len(original_pairs)} pairs in original data")
    print(f"✅ Found {len(optimized_pairs)} pairs in optimized data")
    
    # Calculate DT values
    print("\n📈 Calculating DT values...")
    original_dt, original_details = calculate_dt_values(original_pairs)
    optimized_dt, optimized_details = calculate_dt_values(optimized_pairs)
    
    # Calculate metrics
    original_tmt = sum(dt for dt in original_dt if dt < 0)
    optimized_tmt = sum(dt for dt in optimized_dt if dt < 0)
    tmt_improvement = optimized_tmt - original_tmt
    
    original_coord = sum(1 for dt in original_dt if dt >= 0) / len(original_dt) * 100
    optimized_coord = sum(1 for dt in optimized_dt if dt >= 0) / len(optimized_dt) * 100
    coord_improvement = optimized_coord - original_coord
    
    print(f"\n📊 METRICS SUMMARY:")
    print(f"  TMT Before: {original_tmt:.3f}s")
    print(f"  TMT After: {optimized_tmt:.3f}s")
    print(f"  TMT Improvement: {tmt_improvement:+.3f}s")
    print(f"  Coordination Before: {original_coord:.1f}%")
    print(f"  Coordination After: {optimized_coord:.1f}%")
    print(f"  Coordination Improvement: {coord_improvement:+.1f}%")
    
    # Find worst pairs after optimization
    print(f"\n🔍 WORST PAIRS AFTER OPTIMIZATION:")
    worst_pairs = sorted(optimized_details, key=lambda x: x['dt'])[:10]
    
    for i, pair in enumerate(worst_pairs, 1):
        print(f"  {i:2d}. {pair['main_relay']} → {pair['backup_relay']}")
        print(f"      DT: {pair['dt']:.3f}s (T_main: {pair['time_main']:.3f}s, T_backup: {pair['time_backup']:.3f}s)")
        print(f"      TDS: Main={pair['tds_main']:.3f}, Backup={pair['tds_backup']:.3f}")
        print(f"      Pickup: Main={pair['pickup_main']:.3f}A, Backup={pair['pickup_backup']:.3f}A")
        print()
    
    # Generate detailed report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = reports_dir / f"problematic_scenario_2_analysis_{timestamp}.txt"
    
    print(f"📝 Generating detailed report: {report_file}")
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("DETAILED ANALYSIS - PROBLEMATIC SCENARIO\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Scenario: scenario_2\n")
        f.write(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total Pairs: {len(original_pairs)}\n\n")
        
        f.write("METRICS COMPARISON\n")
        f.write("-" * 20 + "\n")
        f.write(f"TMT Before: {original_tmt:.3f}s\n")
        f.write(f"TMT After: {optimized_tmt:.3f}s\n")
        f.write(f"TMT Improvement: {tmt_improvement:+.3f}s\n")
        f.write(f"Coordination Before: {original_coord:.1f}%\n")
        f.write(f"Coordination After: {optimized_coord:.1f}%\n")
        f.write(f"Coordination Improvement: {coord_improvement:+.1f}%\n\n")
        
        f.write("DISTRIBUTION ANALYSIS\n")
        f.write("-" * 25 + "\n")
        f.write(f"Original DT Range: {min(original_dt):.3f}s to {max(original_dt):.3f}s\n")
        f.write(f"Optimized DT Range: {min(optimized_dt):.3f}s to {max(optimized_dt):.3f}s\n")
        f.write(f"Original Mean DT: {sum(original_dt)/len(original_dt):.3f}s\n")
        f.write(f"Optimized Mean DT: {sum(optimized_dt)/len(optimized_dt):.3f}s\n")
        f.write(f"Original Std DT: {(sum((dt - sum(original_dt)/len(original_dt))**2 for dt in original_dt)/len(original_dt))**0.5:.3f}s\n")
        f.write(f"Optimized Std DT: {(sum((dt - sum(optimized_dt)/len(optimized_dt))**2 for dt in optimized_dt)/len(optimized_dt))**0.5:.3f}s\n\n")
        
        f.write("WORST PAIRS AFTER OPTIMIZATION (Top 20)\n")
        f.write("-" * 45 + "\n")
        for i, pair in enumerate(worst_pairs, 1):
            f.write(f"{i:2d}. {pair['main_relay']} → {pair['backup_relay']}\n")
            f.write(f"    DT: {pair['dt']:.3f}s\n")
            f.write(f"    Times: Main={pair['time_main']:.3f}s, Backup={pair['time_backup']:.3f}s\n")
            f.write(f"    TDS: Main={pair['tds_main']:.3f}, Backup={pair['tds_backup']:.3f}\n")
            f.write(f"    Pickup: Main={pair['pickup_main']:.3f}A, Backup={pair['pickup_backup']:.3f}A\n")
            f.write(f"    Coordinated: {'Yes' if pair['coordinated'] else 'No'}\n\n")
        
        f.write("RELAY SETTINGS ANALYSIS\n")
        f.write("-" * 25 + "\n")
        
        # Analyze relay settings
        relay_settings = defaultdict(list)
        for pair in optimized_details:
            main_relay = pair['main_relay']
            backup_relay = pair['backup_relay']
            relay_settings[main_relay].append({
                'type': 'main',
                'tds': pair['tds_main'],
                'pickup': pair['pickup_main'],
                'dt': pair['dt']
            })
            relay_settings[backup_relay].append({
                'type': 'backup',
                'tds': pair['tds_backup'],
                'pickup': pair['pickup_backup'],
                'dt': pair['dt']
            })
        
        f.write("Relays with worst performance:\n")
        relay_performance = []
        for relay, settings in relay_settings.items():
            avg_dt = sum(s['dt'] for s in settings) / len(settings)
            relay_performance.append((relay, avg_dt, len(settings)))
        
        relay_performance.sort(key=lambda x: x[1])
        
        for i, (relay, avg_dt, count) in enumerate(relay_performance[:10], 1):
            f.write(f"{i:2d}. {relay}: Avg DT = {avg_dt:.3f}s ({count} pairs)\n")
        
        f.write("\nRECOMMENDATIONS\n")
        f.write("-" * 15 + "\n")
        f.write("1. Focus on relays with worst average DT performance\n")
        f.write("2. Consider adjusting TDS settings for problematic relays\n")
        f.write("3. Review pickup settings for better coordination\n")
        f.write("4. Consider additional optimization iterations\n")
        f.write("5. Analyze fault current levels for problematic pairs\n")
    
    print(f"✅ Detailed analysis completed!")
    print(f"📄 Report saved: {report_file}")
    
    return {
        'scenario': 'scenario_2',
        'original_tmt': original_tmt,
        'optimized_tmt': optimized_tmt,
        'tmt_improvement': tmt_improvement,
        'original_coord': original_coord,
        'optimized_coord': optimized_coord,
        'coord_improvement': coord_improvement,
        'worst_pairs': worst_pairs[:5],
        'report_file': report_file
    }

if __name__ == "__main__":
    results = analyze_problematic_scenario()
    
    print(f"\n🎯 SUMMARY:")
    print(f"  Scenario: {results['scenario']}")
    print(f"  TMT Improvement: {results['tmt_improvement']:+.3f}s")
    print(f"  Coordination Improvement: {results['coord_improvement']:+.1f}%")
    print(f"  Report: {results['report_file']}")
