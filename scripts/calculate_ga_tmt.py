#!/usr/bin/env python3
"""
Calculate TMT from GA optimization results using optimized relay settings
"""

import json
from pathlib import Path
from datetime import datetime

def calculate_tmt_from_optimized_settings(scenario_id, optimized_relays, raw_pairs_data):
    """Calculate TMT using optimized relay settings"""
    
    # Constants
    CTI = 0.20
    K = 0.14
    N = 0.02
    
    total_tmt = 0
    
    # Filter pairs for this scenario
    scenario_pairs = [pair for pair in raw_pairs_data if pair['scenario_id'] == scenario_id]
    
    for pair in scenario_pairs:
        main_relay_id = pair['main_relay']['relay']
        backup_relay_id = pair['backup_relay']['relay']
        
        # Get optimized settings
        main_tds = optimized_relays.get(main_relay_id, {}).get('TDS', 0.05)
        main_pickup = optimized_relays.get(main_relay_id, {}).get('pickup', 0.1)
        backup_tds = optimized_relays.get(backup_relay_id, {}).get('TDS', 0.05)
        backup_pickup = optimized_relays.get(backup_relay_id, {}).get('pickup', 0.1)
        
        # Get fault current (using Ishc from main relay)
        fault_current = pair['main_relay']['Ishc']
        
        # Calculate operating times using IEC standard formula
        # T = K * TDS / ((I/Ipickup)^N - 1)
        
        if fault_current > main_pickup:
            main_time = K * main_tds / ((fault_current / main_pickup) ** N - 1)
        else:
            main_time = 10.0  # Maximum time
        
        if fault_current > backup_pickup:
            backup_time = K * backup_tds / ((fault_current / backup_pickup) ** N - 1)
        else:
            backup_time = 10.0  # Maximum time
        
        # Check coordination
        if main_time > 0 and backup_time > 0:
            dt = (backup_time - main_time) - CTI
            if dt < 0:  # Descoordinado
                penalty = -dt  # Penalty is positive
                total_tmt += penalty
    
    return -total_tmt  # Return negative TMT (good coordination)

def create_correct_tmt_comparison():
    """Create correct TMT comparison with calculated GA TMT values"""
    
    print("🔍 ANÁLISIS TMT CORRECTO: AUTOMATIZACIÓN vs OPTIMIZACIÓN GA")
    print("="*80)
    print("🎯 Calculando TMT real de la optimización GA...")
    
    # Load automation TMT data (negative values)
    processed_dir = Path("/Users/gustavo/Documents/Projects/TESIS_UNAL/AutoDOC-MG/data/processed")
    
    # Load automation data
    automation_file = processed_dir / "automation_tmt_data.json"
    with open(automation_file, 'r') as f:
        automation_data = json.load(f)
    
    automation_tmt = automation_data['automation_tmt']
    print(f"📊 Automation TMT data loaded: {len(automation_tmt)} scenarios")
    
    # Load raw pairs data for TMT calculation
    raw_file = Path("/Users/gustavo/Documents/Projects/TESIS_UNAL/AutoDOC-MG/data/raw/automation_results.json")
    with open(raw_file, 'r') as f:
        raw_pairs_data = json.load(f)
    
    print(f"📂 Raw pairs data loaded: {len(raw_pairs_data)} pairs")
    
    # Load latest GA optimization results
    ga_files = list(processed_dir.glob("ga_optimization_all_scenarios_comprehensive_*.json"))
    latest_ga_file = max(ga_files, key=lambda x: x.stat().st_mtime)
    print(f"📂 Loading GA results from: {latest_ga_file.name}")
    
    with open(latest_ga_file, 'r') as f:
        ga_data = json.load(f)
    
    # Create comparison data
    comparison_data = []
    improved_count = 0
    degraded_count = 0
    unchanged_count = 0
    
    print(f"\n🔍 COMPARACIÓN TMT: AUTOMATIZACIÓN vs OPTIMIZACIÓN GA")
    print("="*80)
    
    for scenario_id in automation_tmt.keys():
        automation_tmt_value = automation_tmt[scenario_id]
        
        # Get GA result for this scenario
        ga_result = ga_data.get('optimization_results', {}).get(scenario_id)
        
        if ga_result:
            # Calculate TMT using optimized relay settings
            optimized_relays = ga_result.get('relay_values', {})
            ga_tmt = calculate_tmt_from_optimized_settings(scenario_id, optimized_relays, raw_pairs_data)
            
            # TMT improvement = automation_tmt - ga_tmt
            # Positive improvement = TMT became more negative (better)
            tmt_improvement = automation_tmt_value - ga_tmt
            improvement_percentage = (tmt_improvement / abs(automation_tmt_value)) * 100 if automation_tmt_value != 0 else 0
            
            if tmt_improvement > 0.001:
                improved_count += 1
                status = "✅ MEJORÓ"
            elif tmt_improvement < -0.001:
                degraded_count += 1
                status = "❌ EMPEORÓ"
            else:
                unchanged_count += 1
                status = "➖ SIN CAMBIO"
            
            comparison_data.append({
                'scenario_id': scenario_id,
                'automation_tmt': automation_tmt_value,
                'ga_tmt': ga_tmt,
                'tmt_improvement': tmt_improvement,
                'improvement_percentage': improvement_percentage,
                'status': status
            })
            
            print(f"{scenario_id}: {automation_tmt_value:.3f}s → {ga_tmt:.3f}s (Mejora: {tmt_improvement:+.3f}s) {status}")
        else:
            print(f"⚠️  No GA result found for {scenario_id}")
    
    # Sort by improvement (best first)
    comparison_data.sort(key=lambda x: x['tmt_improvement'], reverse=True)
    
    total_scenarios = len(comparison_data)
    success_rate = (improved_count / total_scenarios) * 100 if total_scenarios > 0 else 0
    
    print(f"\n📊 RESUMEN FINAL:")
    print("="*80)
    print(f"   • Total escenarios comparados: {total_scenarios}")
    print(f"   • Escenarios mejorados: {improved_count} ({success_rate:.1f}%)")
    print(f"   • Escenarios degradados: {degraded_count} ({100-success_rate:.1f}%)")
    print(f"   • Escenarios sin cambio: {unchanged_count}")
    
    if total_scenarios > 0:
        # Calculate averages
        avg_automation = sum(item['automation_tmt'] for item in comparison_data) / len(comparison_data)
        avg_ga = sum(item['ga_tmt'] for item in comparison_data) / len(comparison_data)
        avg_improvement = sum(item['tmt_improvement'] for item in comparison_data) / len(comparison_data)
        
        print(f"   • TMT promedio automatización: {avg_automation:.3f}s")
        print(f"   • TMT promedio optimización: {avg_ga:.3f}s")
        print(f"   • Mejora promedio TMT: {avg_improvement:.3f}s")
        
        print(f"\n🏆 TOP 10 MEJORES MEJORAS (TMT MÁS NEGATIVO DESPUÉS DE GA):")
        print("-" * 80)
        for i, item in enumerate(comparison_data[:10], 1):
            print(f"{i:2d}. {item['scenario_id']}: {item['automation_tmt']:.3f}s → {item['ga_tmt']:.3f}s "
                  f"(Mejora: {item['tmt_improvement']:+.3f}s, {item['improvement_percentage']:+.1f}%) {item['status']}")
        
        print(f"\n📉 TOP 10 PEORES DEGRADACIONES (TMT MENOS NEGATIVO DESPUÉS DE GA):")
        print("-" * 80)
        for i, item in enumerate(comparison_data[-10:], 1):
            print(f"{i:2d}. {item['scenario_id']}: {item['automation_tmt']:.3f}s → {item['ga_tmt']:.3f}s "
                  f"(Cambio: {item['tmt_improvement']:+.3f}s, {item['improvement_percentage']:+.1f}%) {item['status']}")
        
        # Save comparison data
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        comparison_file = processed_dir / f"tmt_automation_vs_ga_correct_{timestamp}.json"
        
        comparison_output = {
            'metadata': {
                'timestamp': timestamp,
                'total_scenarios': total_scenarios,
                'improved_scenarios': improved_count,
                'degraded_scenarios': degraded_count,
                'unchanged_scenarios': unchanged_count,
                'success_rate': success_rate,
                'avg_automation_tmt': avg_automation,
                'avg_ga_tmt': avg_ga,
                'avg_improvement': avg_improvement
            },
            'scenario_comparisons': comparison_data
        }
        
        with open(comparison_file, 'w', encoding='utf-8') as f:
            json.dump(comparison_output, f, indent=2)
        
        print(f"\n💾 Comparación correcta guardada en: {comparison_file.name}")
        
    else:
        print("❌ No matching scenarios found between automation and GA data")
    
    return comparison_data

if __name__ == "__main__":
    comparison_data = create_correct_tmt_comparison()
    print("\n✅ Análisis TMT correcto completado!")
