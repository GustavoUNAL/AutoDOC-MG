#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análisis de causas raíz para el scenario_2 - escenario con peor TMT después de optimización
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

def analyze_root_causes():
    """Analyze root causes for scenario_2 problems."""
    print("🔍 ANALYZING ROOT CAUSES - SCENARIO_2")
    print("=" * 50)
    
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
    
    print(f"✅ Analyzing {len(original_pairs)} relay pairs")
    
    # Analyze problematic patterns
    problematic_patterns = {
        'zero_backup_time': [],
        'extreme_dt_values': [],
        'tds_pickup_issues': [],
        'fault_current_issues': []
    }
    
    print("\n🔍 IDENTIFYING PROBLEMATIC PATTERNS...")
    
    for i, pair in enumerate(optimized_pairs):
        main_relay = pair.get('main_relay', {})
        backup_relay = pair.get('backup_relay', {})
        
        time_main = main_relay.get('Time_out', 0)
        time_backup = backup_relay.get('Time_out', 0)
        tds_main = main_relay.get('TDS', 0)
        tds_backup = backup_relay.get('TDS', 0)
        pickup_main = main_relay.get('pick_up', 0)
        pickup_backup = backup_relay.get('pick_up', 0)
        ishc_main = main_relay.get('Ishc', 0)
        ishc_backup = backup_relay.get('Ishc', 0)
        
        dt = (time_backup - time_main) - 0.2  # CTI = 0.2
        
        # Pattern 1: Zero backup time
        if time_backup == 0:
            problematic_patterns['zero_backup_time'].append({
                'pair_id': i + 1,
                'main_relay': main_relay.get('relay', 'Unknown'),
                'backup_relay': backup_relay.get('relay', 'Unknown'),
                'time_main': time_main,
                'time_backup': time_backup,
                'dt': dt,
                'tds_backup': tds_backup,
                'pickup_backup': pickup_backup,
                'ishc_backup': ishc_backup
            })
        
        # Pattern 2: Extreme DT values
        if dt < -1.0 or dt > 5.0:
            problematic_patterns['extreme_dt_values'].append({
                'pair_id': i + 1,
                'main_relay': main_relay.get('relay', 'Unknown'),
                'backup_relay': backup_relay.get('relay', 'Unknown'),
                'time_main': time_main,
                'time_backup': time_backup,
                'dt': dt,
                'tds_main': tds_main,
                'tds_backup': tds_backup
            })
        
        # Pattern 3: TDS/Pickup issues
        if tds_backup == 0.05 or pickup_backup == 0:
            problematic_patterns['tds_pickup_issues'].append({
                'pair_id': i + 1,
                'main_relay': main_relay.get('relay', 'Unknown'),
                'backup_relay': backup_relay.get('relay', 'Unknown'),
                'tds_backup': tds_backup,
                'pickup_backup': pickup_backup,
                'time_backup': time_backup,
                'dt': dt
            })
        
        # Pattern 4: Fault current issues
        if ishc_backup <= 0 or ishc_main <= 0:
            problematic_patterns['fault_current_issues'].append({
                'pair_id': i + 1,
                'main_relay': main_relay.get('relay', 'Unknown'),
                'backup_relay': backup_relay.get('relay', 'Unknown'),
                'ishc_main': ishc_main,
                'ishc_backup': ishc_backup,
                'dt': dt
            })
    
    # Print findings
    print(f"\n📊 PROBLEMATIC PATTERNS FOUND:")
    print(f"  Zero backup time: {len(problematic_patterns['zero_backup_time'])} pairs")
    print(f"  Extreme DT values: {len(problematic_patterns['extreme_dt_values'])} pairs")
    print(f"  TDS/Pickup issues: {len(problematic_patterns['tds_pickup_issues'])} pairs")
    print(f"  Fault current issues: {len(problematic_patterns['fault_current_issues'])} pairs")
    
    # Detailed analysis of zero backup time (most critical)
    if problematic_patterns['zero_backup_time']:
        print(f"\n🚨 CRITICAL ISSUE: ZERO BACKUP TIME")
        print(f"Found {len(problematic_patterns['zero_backup_time'])} pairs with backup time = 0")
        
        for pattern in problematic_patterns['zero_backup_time'][:5]:
            print(f"  • {pattern['main_relay']} → {pattern['backup_relay']}")
            print(f"    Backup TDS: {pattern['tds_backup']:.3f}")
            print(f"    Backup Pickup: {pattern['pickup_backup']:.3f}A")
            print(f"    Backup Isc: {pattern['ishc_backup']:.3f}A")
            print(f"    DT: {pattern['dt']:.3f}s")
    
    # Generate root cause analysis report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = reports_dir / f"scenario_2_root_causes_{timestamp}.txt"
    
    print(f"\n📝 Generating root cause analysis: {report_file}")
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("ROOT CAUSE ANALYSIS - SCENARIO_2\n")
        f.write("=" * 40 + "\n\n")
        f.write(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Scenario: scenario_2 (Worst TMT after optimization)\n")
        f.write(f"Total Pairs Analyzed: {len(optimized_pairs)}\n\n")
        
        f.write("PROBLEMATIC PATTERNS SUMMARY\n")
        f.write("-" * 30 + "\n")
        f.write(f"Zero backup time: {len(problematic_patterns['zero_backup_time'])} pairs\n")
        f.write(f"Extreme DT values: {len(problematic_patterns['extreme_dt_values'])} pairs\n")
        f.write(f"TDS/Pickup issues: {len(problematic_patterns['tds_pickup_issues'])} pairs\n")
        f.write(f"Fault current issues: {len(problematic_patterns['fault_current_issues'])} pairs\n\n")
        
        # Zero backup time analysis
        if problematic_patterns['zero_backup_time']:
            f.write("CRITICAL ISSUE: ZERO BACKUP TIME\n")
            f.write("-" * 35 + "\n")
            f.write("This is the primary cause of poor coordination.\n")
            f.write("When backup time = 0, the backup relay cannot provide protection.\n\n")
            
            f.write("Affected pairs:\n")
            for pattern in problematic_patterns['zero_backup_time']:
                f.write(f"• {pattern['main_relay']} → {pattern['backup_relay']}\n")
                f.write(f"  Backup TDS: {pattern['tds_backup']:.3f}\n")
                f.write(f"  Backup Pickup: {pattern['pickup_backup']:.3f}A\n")
                f.write(f"  Backup Isc: {pattern['ishc_backup']:.3f}A\n")
                f.write(f"  DT: {pattern['dt']:.3f}s\n\n")
            
            f.write("ROOT CAUSES FOR ZERO BACKUP TIME:\n")
            f.write("1. Backup pickup current = 0A (invalid setting)\n")
            f.write("2. Backup TDS at minimum value (0.05) with low pickup\n")
            f.write("3. Fault current too low relative to pickup setting\n")
            f.write("4. GA optimization hit constraint boundaries\n\n")
        
        # Extreme DT values
        if problematic_patterns['extreme_dt_values']:
            f.write("EXTREME DT VALUES\n")
            f.write("-" * 18 + "\n")
            for pattern in problematic_patterns['extreme_dt_values'][:10]:
                f.write(f"• {pattern['main_relay']} → {pattern['backup_relay']}\n")
                f.write(f"  DT: {pattern['dt']:.3f}s\n")
                f.write(f"  T_main: {pattern['time_main']:.3f}s\n")
                f.write(f"  T_backup: {pattern['time_backup']:.3f}s\n\n")
        
        f.write("RECOMMENDATIONS FOR IMPROVEMENT\n")
        f.write("-" * 35 + "\n")
        f.write("1. Fix zero pickup currents in backup relays\n")
        f.write("2. Adjust GA constraints for pickup current bounds\n")
        f.write("3. Add penalty for zero backup times in fitness function\n")
        f.write("4. Implement minimum pickup current constraints\n")
        f.write("5. Review fault current data quality\n")
        f.write("6. Consider additional optimization iterations\n")
        f.write("7. Implement relay setting validation\n")
    
    print(f"✅ Root cause analysis completed!")
    print(f"📄 Report saved: {report_file}")
    
    return {
        'zero_backup_time': len(problematic_patterns['zero_backup_time']),
        'extreme_dt_values': len(problematic_patterns['extreme_dt_values']),
        'tds_pickup_issues': len(problematic_patterns['tds_pickup_issues']),
        'fault_current_issues': len(problematic_patterns['fault_current_issues']),
        'report_file': report_file
    }

if __name__ == "__main__":
    results = analyze_root_causes()
    
    print(f"\n🎯 ROOT CAUSE SUMMARY:")
    print(f"  Zero backup time pairs: {results['zero_backup_time']}")
    print(f"  Extreme DT pairs: {results['extreme_dt_values']}")
    print(f"  TDS/Pickup issues: {results['tds_pickup_issues']}")
    print(f"  Fault current issues: {results['fault_current_issues']}")
    print(f"  Report: {results['report_file']}")
