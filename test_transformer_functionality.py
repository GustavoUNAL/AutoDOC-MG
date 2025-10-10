#!/usr/bin/env python3
"""
Script de prueba para verificar que el transformer funcione correctamente
"""

import sys
import os
import json
from pathlib import Path

def test_data_files():
    """Verifica que los archivos de datos estén disponibles"""
    print("🔍 Verificando archivos de datos...")
    
    project_root = Path("/Users/gustavo/Documents/Projects/TESIS_UNAL/AutoDOC-MG")
    
    # Verificar archivo de datos originales
    raw_data_path = project_root / "data" / "raw" / "automation_results.json"
    if raw_data_path.exists():
        print(f"✅ Datos originales encontrados: {raw_data_path}")
        with open(raw_data_path, 'r') as f:
            raw_data = json.load(f)
        print(f"   📊 {len(raw_data)} pares de relés encontrados")
    else:
        print(f"❌ Datos originales no encontrados: {raw_data_path}")
        return False
    
    # Verificar archivo de resultados GA
    ga_files = list((project_root / "data" / "processed").glob("*ga_optimization_all_scenarios_comprehensive*.json"))
    if ga_files:
        latest_ga = max(ga_files, key=os.path.getctime)
        print(f"✅ Resultados GA encontrados: {latest_ga}")
        with open(latest_ga, 'r') as f:
            ga_data = json.load(f)
        print(f"   📊 {len(ga_data['optimization_results'])} escenarios optimizados")
    else:
        print("❌ Resultados GA no encontrados")
        return False
    
    return True

def test_model_files():
    """Verifica que los archivos del modelo estén disponibles"""
    print("\n🔍 Verificando archivos del modelo...")
    
    project_root = Path("/Users/gustavo/Documents/Projects/TESIS_UNAL/AutoDOC-MG")
    model_dir = project_root / "models" / "transformer"
    
    required_files = [
        "best_relay_optimization_transformer.pth",
        "scaler_input.pkl", 
        "scaler_target.pkl",
        "best_params.json",
        "training_summary.json",
        "transformer_predictor.py"
    ]
    
    all_present = True
    for file_name in required_files:
        file_path = model_dir / file_name
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"✅ {file_name} ({size:,} bytes)")
        else:
            print(f"❌ {file_name} no encontrado")
            all_present = False
    
    return all_present

def test_predictor_import():
    """Verifica que se pueda importar la clase predictor"""
    print("\n🔍 Verificando importación del predictor...")
    
    try:
        sys.path.append("/Users/gustavo/Documents/Projects/TESIS_UNAL/AutoDOC-MG/models/transformer")
        from transformer_predictor import RelayOptimizationPredictor
        print("✅ Clase RelayOptimizationPredictor importada correctamente")
        return True
    except ImportError as e:
        print(f"❌ Error al importar predictor: {e}")
        return False

def test_notebooks():
    """Verifica que los notebooks estén disponibles"""
    print("\n🔍 Verificando notebooks...")
    
    project_root = Path("/Users/gustavo/Documents/Projects/TESIS_UNAL/AutoDOC-MG")
    notebooks_dir = project_root / "analysis" / "notebooks"
    
    required_notebooks = [
        "01.transformer_training.ipynb",
        "02.transformer_validation.ipynb"
    ]
    
    all_present = True
    for notebook_name in required_notebooks:
        notebook_path = notebooks_dir / notebook_name
        if notebook_path.exists():
            size = notebook_path.stat().st_size
            print(f"✅ {notebook_name} ({size:,} bytes)")
        else:
            print(f"❌ {notebook_name} no encontrado")
            all_present = False
    
    return all_present

def main():
    """Función principal de prueba"""
    print("🚀 PRUEBA DE FUNCIONALIDAD DEL TRANSFORMER")
    print("=" * 50)
    
    tests = [
        ("Archivos de datos", test_data_files),
        ("Archivos del modelo", test_model_files),
        ("Importación del predictor", test_predictor_import),
        ("Notebooks", test_notebooks)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Error en {test_name}: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 50)
    
    all_passed = True
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 TODAS LAS PRUEBAS PASARON - SISTEMA LISTO")
        print("\n📋 PRÓXIMOS PASOS:")
        print("1. Ejecutar notebook de entrenamiento: 01.transformer_training.ipynb")
        print("2. Ejecutar notebook de validación: 02.transformer_validation.ipynb")
        print("3. Usar el predictor para nuevas optimizaciones")
    else:
        print("⚠️  ALGUNAS PRUEBAS FALLARON - REVISAR CONFIGURACIÓN")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
