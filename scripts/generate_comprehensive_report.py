#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to generate comprehensive report for all 68 scenarios
Avoids NumPy compatibility issues by using basic Python libraries
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

def calculate_tmt_metrics(pairs, cti=0.2):
    """Calculate TMT metrics for a set of pairs."""
    if not pairs:
        return {
            'total_pairs': 0,
            'tmt_signed': 0.0,
            'tmt_magnitude': 0.0,
            'coordination_percentage': 0.0,
            'mean_dt': 0.0,
            'std_dt': 0.0,
            'min_dt': 0.0,
            'max_dt': 0.0
        }
    
    dt_values = []
    coordinated_pairs = 0
    
    for pair in pairs:
        main_relay = pair.get('main_relay', {})
        backup_relay = pair.get('backup_relay', {})
        
        time_main = main_relay.get('Time_out', 0)
        time_backup = backup_relay.get('Time_out', 0)
        
        if isinstance(time_main, (int, float)) and isinstance(time_backup, (int, float)):
            dt = (time_backup - time_main) - cti
            dt_values.append(dt)
            
            if dt >= 0:
                coordinated_pairs += 1
    
    if not dt_values:
        return {
            'total_pairs': len(pairs),
            'tmt_signed': 0.0,
            'tmt_magnitude': 0.0,
            'coordination_percentage': 0.0,
            'mean_dt': 0.0,
            'std_dt': 0.0,
            'min_dt': 0.0,
            'max_dt': 0.0
        }
    
    # Calculate TMT (signed and magnitude)
    tmt_signed = sum(dt for dt in dt_values if dt < 0)
    tmt_magnitude = sum(abs(dt) for dt in dt_values if dt < 0)
    
    # Calculate coordination percentage
    coordination_percentage = (coordinated_pairs / len(dt_values)) * 100 if dt_values else 0
    
    # Calculate statistics
    mean_dt = sum(dt_values) / len(dt_values)
    variance = sum((dt - mean_dt) ** 2 for dt in dt_values) / len(dt_values)
    std_dt = variance ** 0.5
    min_dt = min(dt_values)
    max_dt = max(dt_values)
    
    return {
        'total_pairs': len(pairs),
        'tmt_signed': tmt_signed,
        'tmt_magnitude': tmt_magnitude,
        'coordination_percentage': coordination_percentage,
        'mean_dt': mean_dt,
        'std_dt': std_dt,
        'min_dt': min_dt,
        'max_dt': max_dt
    }

def extract_scenarios(data):
    """Extract unique scenario IDs from data."""
    scenarios = set()
    for pair in data:
        if 'scenario_id' in pair:
            scenarios.add(pair['scenario_id'])
    return sorted(list(scenarios))

def generate_comprehensive_report():
    """Generate comprehensive report for all 68 scenarios."""
    print("🚀 Starting comprehensive analysis of all 68 scenarios...")
    
    # Setup paths
    project_root = Path.cwd()
    data_file = project_root / "data" / "raw" / "automation_results.json"
    processed_dir = project_root / "data" / "processed"
    results_dir = project_root / "results"
    reports_dir = results_dir / "reports"
    tables_dir = results_dir / "tables"
    
    # Create directories
    for dir_path in [reports_dir, tables_dir]:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    # Load original data
    print("📊 Loading original data...")
    original_data = load_data(data_file)
    original_scenarios = extract_scenarios(original_data)
    print(f"✅ Found {len(original_scenarios)} scenarios in original data")
    
    # Analyze all scenarios
    all_scenario_results = {}
    scenarios_with_optimization = []
    scenarios_without_optimization = []
    
    print("\n🔍 Analyzing all scenarios...")
    
    for i, scenario in enumerate(original_scenarios, 1):
        print(f"  {i:2d}/68: Analyzing {scenario}...")
        
        # Get original data for this scenario
        original_pairs = [pair for pair in original_data if pair.get('scenario_id') == scenario]
        original_metrics = calculate_tmt_metrics(original_pairs)
        
        # Check if optimized data exists
        optimized_file = processed_dir / f"automation_results_{scenario}_optimized.json"
        
        if optimized_file.exists():
            try:
                optimized_data = load_data(optimized_file)
                optimized_pairs = [pair for pair in optimized_data if pair.get('scenario_id') == scenario]
                optimized_metrics = calculate_tmt_metrics(optimized_pairs)
                
                # Calculate improvements
                tmt_improvement = optimized_metrics['tmt_signed'] - original_metrics['tmt_signed']
                coord_improvement = optimized_metrics['coordination_percentage'] - original_metrics['coordination_percentage']
                
                all_scenario_results[scenario] = {
                    'has_optimization': True,
                    'before': original_metrics,
                    'after': optimized_metrics,
                    'improvements': {
                        'tmt_improvement': tmt_improvement,
                        'coord_improvement': coord_improvement,
                        'tmt_improvement_pct': (tmt_improvement / abs(original_metrics['tmt_signed']) * 100) if original_metrics['tmt_signed'] != 0 else 0,
                        'coord_improvement_pct': coord_improvement
                    }
                }
                scenarios_with_optimization.append(scenario)
                
            except Exception as e:
                print(f"    ⚠️  Error loading optimized data: {e}")
                all_scenario_results[scenario] = {
                    'has_optimization': False,
                    'before': original_metrics,
                    'after': None,
                    'improvements': None
                }
                scenarios_without_optimization.append(scenario)
        else:
            all_scenario_results[scenario] = {
                'has_optimization': False,
                'before': original_metrics,
                'after': None,
                'improvements': None
            }
            scenarios_without_optimization.append(scenario)
    
    print(f"\n📊 Analysis Summary:")
    print(f"  Total scenarios: {len(original_scenarios)}")
    print(f"  With optimization: {len(scenarios_with_optimization)}")
    print(f"  Without optimization: {len(scenarios_without_optimization)}")
    
    # Generate comprehensive report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = reports_dir / f"comprehensive_68_scenarios_report_{timestamp}.txt"
    
    print(f"\n📝 Generating comprehensive report: {report_file}")
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("COMPREHENSIVE ANALYSIS REPORT - ALL 68 SCENARIOS\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Data Source: {data_file.name}\n")
        f.write(f"CTI Threshold: 0.2 seconds\n")
        f.write(f"Total Scenarios Analyzed: {len(all_scenario_results)}\n")
        f.write(f"Scenarios with Optimization: {len(scenarios_with_optimization)}\n")
        f.write(f"Scenarios without Optimization: {len(scenarios_without_optimization)}\n\n")
        
        # Overall statistics
        f.write("OVERALL STATISTICS\n")
        f.write("-" * 30 + "\n")
        
        all_tmt_before = [v['before']['tmt_signed'] for v in all_scenario_results.values()]
        all_coord_before = [v['before']['coordination_percentage'] for v in all_scenario_results.values()]
        
        f.write(f"Mean TMT (All Scenarios): {sum(all_tmt_before)/len(all_tmt_before):.3f} seconds\n")
        f.write(f"TMT Range: {min(all_tmt_before):.3f} to {max(all_tmt_before):.3f} seconds\n")
        f.write(f"Mean Coordination (All Scenarios): {sum(all_coord_before)/len(all_coord_before):.1f}%\n")
        f.write(f"Coordination Range: {min(all_coord_before):.1f}% to {max(all_coord_before):.1f}%\n\n")
        
        # Scenarios with optimization
        if scenarios_with_optimization:
            f.write("SCENARIOS WITH OPTIMIZATION\n")
            f.write("-" * 40 + "\n")
            
            opt_tmt_improvements = [v['improvements']['tmt_improvement'] for v in all_scenario_results.values() if v['has_optimization']]
            opt_coord_improvements = [v['improvements']['coord_improvement'] for v in all_scenario_results.values() if v['has_optimization']]
            
            f.write(f"Mean TMT Improvement: {sum(opt_tmt_improvements)/len(opt_tmt_improvements):+.3f} seconds\n")
            f.write(f"Mean Coordination Improvement: {sum(opt_coord_improvements)/len(opt_coord_improvements):+.1f}%\n")
            f.write(f"Scenarios with Positive TMT Improvement: {sum(1 for x in opt_tmt_improvements if x > 0)}\n")
            f.write(f"Scenarios with Positive Coord Improvement: {sum(1 for x in opt_coord_improvements if x > 0)}\n\n")
            
            # Best and worst improvements
            best_tmt_improvement = max(scenarios_with_optimization, key=lambda s: all_scenario_results[s]['improvements']['tmt_improvement'])
            worst_tmt_improvement = min(scenarios_with_optimization, key=lambda s: all_scenario_results[s]['improvements']['tmt_improvement'])
            
            f.write(f"Best TMT Improvement: {best_tmt_improvement} ({all_scenario_results[best_tmt_improvement]['improvements']['tmt_improvement']:+.3f}s)\n")
            f.write(f"Worst TMT Improvement: {worst_tmt_improvement} ({all_scenario_results[worst_tmt_improvement]['improvements']['tmt_improvement']:+.3f}s)\n\n")
        
        # Detailed scenario analysis
        f.write("DETAILED SCENARIO ANALYSIS\n")
        f.write("-" * 40 + "\n")
        
        # Sort scenarios by TMT (worst first)
        sorted_scenarios = sorted(all_scenario_results.items(), key=lambda x: x[1]['before']['tmt_signed'])
        
        for i, (scenario, data) in enumerate(sorted_scenarios, 1):
            f.write(f"\n{i:2d}. Scenario: {scenario}\n")
            f.write(f"    TMT: {data['before']['tmt_signed']:+.3f}s\n")
            f.write(f"    Coordination: {data['before']['coordination_percentage']:.1f}%\n")
            f.write(f"    Total Pairs: {data['before']['total_pairs']}\n")
            
            if data['has_optimization']:
                f.write(f"    Status: OPTIMIZED\n")
                f.write(f"    TMT Improvement: {data['improvements']['tmt_improvement']:+.3f}s\n")
                f.write(f"    Coord Improvement: {data['improvements']['coord_improvement']:+.1f}%\n")
            else:
                f.write(f"    Status: NOT OPTIMIZED\n")
        
        # Recommendations
        f.write("\n\nRECOMMENDATIONS\n")
        f.write("-" * 20 + "\n")
        
        # Find worst performing scenarios
        worst_scenarios = sorted_scenarios[:10]  # Top 10 worst
        f.write("Priority Scenarios for Optimization:\n")
        for i, (scenario, data) in enumerate(worst_scenarios, 1):
            f.write(f"{i:2d}. {scenario}: TMT={data['before']['tmt_signed']:+.3f}s, Coord={data['before']['coordination_percentage']:.1f}%\n")
        
        f.write(f"\nTotal scenarios requiring optimization: {len([s for s in all_scenario_results.values() if s['before']['tmt_signed'] < -0.5])}\n")
        f.write(f"Scenarios with good performance: {len([s for s in all_scenario_results.values() if s['before']['tmt_signed'] >= -0.1])}\n")
    
    # Generate CSV summary
    csv_file = tables_dir / f"all_68_scenarios_summary_{timestamp}.csv"
    print(f"📊 Generating CSV summary: {csv_file}")
    
    with open(csv_file, 'w', encoding='utf-8') as f:
        # Write header
        f.write("Scenario,Has_Optimization,Total_Pairs,TMT,Coordination_Percentage,Mean_DT,Std_DT,Min_DT,Max_DT")
        f.write(",TMT_After,Coord_After,TMT_Improvement,Coord_Improvement\n")
        
        # Write data
        for scenario, data in all_scenario_results.items():
            before = data['before']
            f.write(f"{scenario},{data['has_optimization']},{before['total_pairs']},{before['tmt_signed']:.6f}")
            f.write(f",{before['coordination_percentage']:.2f},{before['mean_dt']:.6f},{before['std_dt']:.6f}")
            f.write(f",{before['min_dt']:.6f},{before['max_dt']:.6f}")
            
            if data['has_optimization']:
                after = data['after']
                improvements = data['improvements']
                f.write(f",{after['tmt_signed']:.6f},{after['coordination_percentage']:.2f}")
                f.write(f",{improvements['tmt_improvement']:.6f},{improvements['coord_improvement']:.2f}")
            else:
                f.write(",,,,")
            f.write("\n")
    
    print(f"\n🎉 Comprehensive analysis completed!")
    print(f"📁 Generated files:")
    print(f"  📄 Report: {report_file}")
    print(f"  📊 CSV: {csv_file}")
    
    # Print summary statistics
    print(f"\n📈 Summary Statistics:")
    print(f"  Total Scenarios: {len(all_scenario_results)}")
    print(f"  With Optimization: {len(scenarios_with_optimization)}")
    print(f"  Without Optimization: {len(scenarios_without_optimization)}")
    print(f"  Mean TMT: {sum(all_tmt_before)/len(all_tmt_before):.3f}s")
    print(f"  Mean Coordination: {sum(all_coord_before)/len(all_coord_before):.1f}%")
    
    if scenarios_with_optimization:
        print(f"  Mean TMT Improvement: {sum(opt_tmt_improvements)/len(opt_tmt_improvements):+.3f}s")
        print(f"  Mean Coord Improvement: {sum(opt_coord_improvements)/len(opt_coord_improvements):+.1f}%")

if __name__ == "__main__":
    generate_comprehensive_report()
