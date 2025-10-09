#!/usr/bin/env python3
"""
Simple analysis script for GA optimization results
"""

import json
import os
from pathlib import Path

def analyze_results():
    """Analyze GA optimization results"""
    
    # Load comprehensive results
    processed_dir = Path("/Users/gustavo/Documents/Projects/TESIS_UNAL/AutoDOC-MG/data/processed")
    results_file = processed_dir / "ga_optimization_all_scenarios_comprehensive_20251008_114243.json"
    
    if not results_file.exists():
        print("❌ Results file not found!")
        return
    
    print("🔍 ANALYZING GA OPTIMIZATION RESULTS")
    print("="*60)
    
    with open(results_file, 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    # Extract summary
    summary = results['optimization_summary']
    print(f"📊 SUMMARY:")
    print(f"   • Total scenarios: {summary['total_scenarios']}")
    print(f"   • Successful optimizations: {summary['successful_optimizations']}")
    print(f"   • Failed optimizations: {summary['failed_optimizations']}")
    print(f"   • Skipped scenarios: {summary['skipped_scenarios']}")
    print(f"   • Success rate: {summary['successful_optimizations']/summary['total_scenarios']*100:.1f}%")
    print(f"   • Processing time: {summary['processing_time']:.2f} seconds")
    print(f"   • Average time per scenario: {summary['processing_time']/summary['total_scenarios']:.2f} seconds")
    
    # Analyze TMT improvements
    print(f"\n🎯 TMT ANALYSIS:")
    print("-" * 40)
    
    # Load original data to compare
    raw_file = Path("/Users/gustavo/Documents/Projects/TESIS_UNAL/AutoDOC-MG/data/raw/automation_results.json")
    with open(raw_file, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
    
    # Calculate initial TMT for each scenario
    scenario_tmt_before = {}
    scenario_tmt_after = {}
    
    for scenario_id, scenario_result in results['optimization_results'].items():
        # Get scenario pairs from raw data
        scenario_pairs = [p for p in raw_data if p.get('scenario_id') == scenario_id]
        
        # Calculate TMT before optimization
        tmt_before = 0.0
        for pair in scenario_pairs:
            main_time = pair.get('main_relay', {}).get('Time_out', 0)
            backup_time = pair.get('backup_relay', {}).get('Time_out', 0)
            if main_time > 0 and backup_time > 0:
                dt = (backup_time - main_time) - 0.20  # CTI = 0.20
                if dt < 0:
                    tmt_before += -dt
        
        # Calculate TMT after optimization using optimized pairs
        optimized_pairs_file = processed_dir / f"automation_results_{scenario_id}_optimized_20251008_114243.json"
        tmt_after = 0.0
        if optimized_pairs_file.exists():
            with open(optimized_pairs_file, 'r', encoding='utf-8') as f:
                opt_pairs = json.load(f)
            
            for pair in opt_pairs:
                main_time = pair.get('main_relay', {}).get('Time_out', 0)
                backup_time = pair.get('backup_relay', {}).get('Time_out', 0)
                if main_time > 0 and backup_time > 0:
                    dt = (backup_time - main_time) - 0.20  # CTI = 0.20
                    if dt < 0:
                        tmt_after += -dt
        
        scenario_tmt_before[scenario_id] = tmt_before
        scenario_tmt_after[scenario_id] = tmt_after
    
    # Calculate statistics
    total_tmt_before = sum(scenario_tmt_before.values())
    total_tmt_after = sum(scenario_tmt_after.values())
    improvement = total_tmt_before - total_tmt_after
    improvement_pct = (improvement / total_tmt_before * 100) if total_tmt_before > 0 else 0
    
    print(f"   • Total TMT before optimization: {total_tmt_before:.6f} seconds")
    print(f"   • Total TMT after optimization: {total_tmt_after:.6f} seconds")
    print(f"   • TMT improvement: {improvement:.6f} seconds ({improvement_pct:.1f}%)")
    
    # Find best and worst improvements
    improvements = []
    for scenario_id in scenario_tmt_before:
        imp = scenario_tmt_before[scenario_id] - scenario_tmt_after[scenario_id]
        improvements.append((scenario_id, imp))
    
    improvements.sort(key=lambda x: x[1], reverse=True)
    
    print(f"\n🏆 TOP 5 BEST IMPROVEMENTS:")
    print("-" * 40)
    for i, (scenario_id, imp) in enumerate(improvements[:5], 1):
        print(f"   {i}. {scenario_id}: {imp:.6f}s improvement")
    
    print(f"\n📉 BOTTOM 5 IMPROVEMENTS:")
    print("-" * 40)
    for i, (scenario_id, imp) in enumerate(improvements[-5:], 1):
        print(f"   {i}. {scenario_id}: {imp:.6f}s improvement")
    
    # Relay settings analysis
    print(f"\n⚙️  RELAY SETTINGS ANALYSIS:")
    print("-" * 40)
    
    all_tds_values = []
    all_pickup_values = []
    
    for scenario_id, scenario_result in results['optimization_results'].items():
        relay_values = scenario_result['relay_values']
        for relay_name, settings in relay_values.items():
            all_tds_values.append(settings['TDS'])
            all_pickup_values.append(settings['pickup'])
    
    if all_tds_values:
        print(f"   • Total relays optimized: {len(all_tds_values)}")
        print(f"   • TDS range: {min(all_tds_values):.3f} - {max(all_tds_values):.3f}")
        print(f"   • TDS average: {sum(all_tds_values)/len(all_tds_values):.3f}")
        print(f"   • Pickup range: {min(all_pickup_values):.3f} - {max(all_pickup_values):.3f}")
        print(f"   • Pickup average: {sum(all_pickup_values)/len(all_pickup_values):.3f}")
    
    # Save analysis results
    analysis_results = {
        'summary': summary,
        'tmt_analysis': {
            'total_tmt_before': total_tmt_before,
            'total_tmt_after': total_tmt_after,
            'improvement': improvement,
            'improvement_percentage': improvement_pct,
            'scenario_improvements': dict(improvements)
        },
        'relay_analysis': {
            'total_relays': len(all_tds_values),
            'tds_range': [min(all_tds_values), max(all_tds_values)] if all_tds_values else [0, 0],
            'tds_average': sum(all_tds_values)/len(all_tds_values) if all_tds_values else 0,
            'pickup_range': [min(all_pickup_values), max(all_pickup_values)] if all_pickup_values else [0, 0],
            'pickup_average': sum(all_pickup_values)/len(all_pickup_values) if all_pickup_values else 0
        }
    }
    
    # Save analysis to file
    analysis_file = processed_dir / "ga_optimization_analysis_20251008_114243.json"
    with open(analysis_file, 'w', encoding='utf-8') as f:
        json.dump(analysis_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Analysis saved to: {analysis_file}")
    print(f"\n✅ Analysis completed successfully!")

if __name__ == "__main__":
    analyze_results()
