#!/usr/bin/env python3
"""
CÓDIGO PARA EL NOTEBOOK - ANÁLISIS TMT CORRECTO
Generado automáticamente el 2025-10-08 17:42:03
"""

# %% TMT Analysis: Automation vs GA Optimization (CORRECT VERSION)
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime

# Setup paths
figures_dir = Path("/Users/gustavo/Documents/Projects/TESIS_UNAL/AutoDOC-MG/results/figures")
figures_dir.mkdir(parents=True, exist_ok=True)
processed_dir = Path("/Users/gustavo/Documents/Projects/TESIS_UNAL/AutoDOC-MG/data/processed")

print("🔍 ANÁLISIS TMT CORRECTO: AUTOMATIZACIÓN vs OPTIMIZACIÓN GA")
print("="*80)
print("🎯 TMT = Total Miscoordination Time (Tiempo Total de Descoordinación)")
print("   • TMT NEGATIVO = BUENA coordinación (menos descoordinación)")
print("   • TMT POSITIVO = MALA coordinación (más descoordinación)")
print("   • TMT = 0 = PERFECTA coordinación")
print("   • Mejora TMT = TMT_automatización - TMT_optimización")
print("   • Mejora Positiva = TMT se volvió MÁS NEGATIVO (mejor coordinación) ✅")
print("   • Mejora Negativa = TMT se volvió MENOS NEGATIVO (peor coordinación) ❌")

# Load comparison data
comparison_files = list(processed_dir.glob("tmt_automation_vs_ga_final_*.json"))
if comparison_files:
    latest_comparison = max(comparison_files, key=lambda x: x.stat().st_mtime)
    print(f"\n📂 Loading comparison data from: {latest_comparison.name}")
    
    with open(latest_comparison, 'r', encoding='utf-8') as f:
        comparison_data = json.load(f)
    
    scenarios = comparison_data['scenario_comparisons']
    metadata = comparison_data['metadata']
    
    print(f"\n📊 RESULTADOS DE COMPARACIÓN:")
    print("="*80)
    print(f"   • Total escenarios: {metadata['total_scenarios']}")
    print(f"   • Escenarios mejorados: {metadata['improved_scenarios']} ({metadata['success_rate']:.1f}%)")
    print(f"   • Escenarios degradados: {metadata['degraded_scenarios']}")
    print(f"   • TMT promedio automatización: {metadata['avg_automation_tmt']:.3f}s")
    print(f"   • TMT promedio optimización: {metadata['avg_ga_tmt']:.3f}s")
    print(f"   • Mejora promedio TMT: {metadata['avg_improvement']:.3f}s")
    
    # Create DataFrame
    df = pd.DataFrame(scenarios)
    df = df.sort_values('tmt_improvement', ascending=False).reset_index(drop=True)
    
    # Display sample data
    print(f"\n📋 MUESTRA DE DATOS (Top 10):")
    display_cols = ['scenario_id', 'automation_tmt', 'ga_tmt', 'tmt_improvement', 'improvement_percentage', 'status']
    display(df[display_cols].head(10))
    
else:
    print("❌ No comparison data found!")
    print("Please run the TMT comparison analysis first.")

# %% Create TMT Comparison Visualization (CORRECT VERSION)
def create_tmt_comparison_plot(df):
    """Create comprehensive TMT comparison plot with correct interpretation"""
    
    # Set up the plot style
    plt.style.use('default')
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(20, 16))
    
    # Get top 30 scenarios for better visualization
    top_30 = df.head(30)
    x = np.arange(len(top_30))
    width = 0.35
    
    # Plot 1: TMT Before vs After (Bar chart)
    bars1 = ax1.bar(x - width/2, top_30['automation_tmt'], width, 
                   label='TMT Automatización', color='#e74c3c', alpha=0.8)
    bars2 = ax1.bar(x + width/2, top_30['ga_tmt'], width, 
                   label='TMT Optimización GA', color='#3498db', alpha=0.8)
    
    ax1.set_xlabel('Escenario', fontsize=12)
    ax1.set_ylabel('TMT (segundos)', fontsize=12)
    ax1.set_title('Comparación TMT: Automatización vs Optimización GA\n(Top 30 Escenarios - Valores Negativos = Mejor)', 
                  fontsize=14, fontweight='bold')
    ax1.set_xticks(x[::3])
    ax1.set_xticklabels([top_30.iloc[i]['scenario_id'] for i in range(0, len(top_30), 3)], 
                       rotation=45, ha='right')
    ax1.legend(fontsize=12)
    ax1.grid(True, alpha=0.3)
    
    # Add value labels for first 10 scenarios
    for i in range(min(10, len(top_30))):
        ax1.text(i - width/2, top_30.iloc[i]['automation_tmt'] - 0.5, 
                f'{top_30.iloc[i]["automation_tmt"]:.1f}', 
                ha='center', va='top', fontsize=8)
        ax1.text(i + width/2, top_30.iloc[i]['ga_tmt'] - 0.5, 
                f'{top_30.iloc[i]["ga_tmt"]:.1f}', 
                ha='center', va='top', fontsize=8)
    
    # Plot 2: TMT Improvement (Bar chart with colors)
    colors = ['#2ecc71' if imp > 0 else '#e74c3c' for imp in top_30['tmt_improvement']]
    bars3 = ax2.bar(x, top_30['tmt_improvement'], color=colors, alpha=0.7)
    
    ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
    ax2.set_xlabel('Escenario', fontsize=12)
    ax2.set_ylabel('Mejora TMT (segundos)', fontsize=12)
    ax2.set_title('Mejora/Degradación TMT por Escenario\n(Verde = Mejora, Rojo = Degradación)', 
                  fontsize=14, fontweight='bold')
    ax2.set_xticks(x[::3])
    ax2.set_xticklabels([top_30.iloc[i]['scenario_id'] for i in range(0, len(top_30), 3)], 
                       rotation=45, ha='right')
    ax2.grid(True, alpha=0.3)
    
    # Add improvement labels for significant changes
    for i, (imp, bar) in enumerate(zip(top_30['tmt_improvement'], bars3)):
        if abs(imp) > 0.5:
            ax2.text(i, imp + (0.1 if imp > 0 else -0.1), f'{imp:.2f}s', 
                    ha='center', va='bottom' if imp > 0 else 'top', 
                    fontsize=8, fontweight='bold')
    
    # Plot 3: TMT Distribution
    ax3.hist(df['automation_tmt'], bins=20, alpha=0.7, label='TMT Automatización', 
             color='#e74c3c', density=True, edgecolor='black')
    ax3.hist(df['ga_tmt'], bins=20, alpha=0.7, label='TMT Optimización GA', 
             color='#3498db', density=True, edgecolor='black')
    ax3.set_xlabel('TMT (segundos)', fontsize=12)
    ax3.set_ylabel('Densidad', fontsize=12)
    ax3.set_title('Distribución TMT: Automatización vs Optimización GA\n(Valores Negativos = Mejor Coordinación)', 
                  fontsize=14, fontweight='bold')
    ax3.legend(fontsize=12)
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: Improvement Distribution
    ax4.hist(df['tmt_improvement'], bins=20, alpha=0.7, color='#2ecc71', 
             density=True, edgecolor='black')
    ax4.axvline(x=0, color='red', linestyle='--', linewidth=2, label='Sin Cambio')
    ax4.set_xlabel('Mejora TMT (segundos)', fontsize=12)
    ax4.set_ylabel('Densidad', fontsize=12)
    ax4.set_title('Distribución de Mejora TMT\n(Positivo = Mejora, Negativo = Degradación)', 
                  fontsize=14, fontweight='bold')
    ax4.legend(fontsize=12)
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Save plot
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    plot_file = figures_dir / f"tmt_automation_vs_ga_correct_20251008_174203.png"
    plt.savefig(plot_file, dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"📊 TMT comparison plot saved: {plot_file}")
    return plot_file

if 'df' in locals() and not df.empty:
    create_tmt_comparison_plot(df)
else:
    print("❌ No data available for plotting")

# %% Summary and Recommendations (CORRECT VERSION)
if 'metadata' in locals():
    print("🎯 RESUMEN FINAL: AUTOMATIZACIÓN vs OPTIMIZACIÓN GA")
    print("="*80)
    
    print(f"📊 RESULTADOS GENERALES:")
    print(f"   • Total escenarios analizados: {metadata['total_scenarios']}")
    print(f"   • Tasa de éxito: {metadata['success_rate']:.1f}% ({metadata['improved_scenarios']} escenarios mejoraron)")
    print(f"   • Tasa de degradación: {100-metadata['success_rate']:.1f}% ({metadata['degraded_scenarios']} escenarios empeoraron)")
    print(f"   • TMT promedio automatización: {metadata['avg_automation_tmt']:.3f} segundos")
    print(f"   • TMT promedio optimización: {metadata['avg_ga_tmt']:.3f} segundos")
    print(f"   • Cambio promedio TMT: {metadata['avg_improvement']:.3f} segundos")
    
    print(f"\n🎯 INTERPRETACIÓN CORRECTA:")
    print(f"   • TMT NEGATIVO = BUENA coordinación")
    print(f"   • TMT POSITIVO = MALA coordinación")
    if metadata['success_rate'] > 50:
        print(f"   ✅ La optimización GA fue EXITOSA en la mayoría de escenarios")
    elif metadata['success_rate'] > 25:
        print(f"   ⚠️  La optimización GA tuvo éxito MODERADO")
    else:
        print(f"   ❌ La optimización GA tuvo éxito LIMITADO")
    
    if metadata['avg_improvement'] > 0:
        print(f"   ✅ En promedio, el TMT se volvió MÁS NEGATIVO ({metadata['avg_improvement']:.3f}s mejor)")
    else:
        print(f"   ❌ En promedio, el TMT se volvió MENOS NEGATIVO ({abs(metadata['avg_improvement']):.3f}s peor)")
    
    print(f"\n💡 RECOMENDACIONES:")
    print(f"   1. Aumentar generaciones GA de 1,000 a 5,000-10,000")
    print(f"   2. Investigar escenarios exitosos para replicar estrategias")
    print(f"   3. Revisar parámetros GA para mejor convergencia")
    print(f"   4. Validar datos de entrada para escenarios problemáticos")
    print(f"   5. Considerar diferentes estrategias para escenarios complejos")
    
    print(f"\n✅ Análisis TMT correcto completado!")
else:
    print("❌ No metadata available for summary")
