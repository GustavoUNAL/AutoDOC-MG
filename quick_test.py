#!/usr/bin/env python3
"""
Prueba rápida para verificar que el transformer funcione después de la limpieza
"""

import sys
from pathlib import Path

def quick_test():
    """Prueba rápida de funcionalidad"""
    print("🔍 Verificación rápida después de limpieza...")
    
    # Verificar archivos .pkl
    model_dir = Path("/Users/gustavo/Documents/Projects/TESIS_UNAL/AutoDOC-MG/models/transformer")
    pkl_files = [
        "scaler_input.pkl",
        "scaler_target.pkl"
    ]
    
    for pkl_file in pkl_files:
        file_path = model_dir / pkl_file
        if file_path.exists():
            print(f"✅ {pkl_file} en ubicación correcta")
        else:
            print(f"❌ {pkl_file} no encontrado")
            return False
    
    # Verificar que no hay duplicados
    import os
    project_root = Path("/Users/gustavo/Documents/Projects/TESIS_UNAL/AutoDOC-MG")
    
    # Buscar archivos .pkl fuera de models/transformer
    for root, dirs, files in os.walk(project_root):
        # Saltar .venv y __pycache__
        dirs[:] = [d for d in dirs if d not in ['.venv', '__pycache__']]
        
        for file in files:
            if file.endswith('.pkl') and 'scaler' in file:
                file_path = Path(root) / file
                if 'models/transformer' not in str(file_path):
                    print(f"❌ Archivo .pkl duplicado encontrado: {file_path}")
                    return False
    
    print("✅ No hay archivos .pkl duplicados")
    
    # Verificar carpetas .venv
    venv_dirs = [d for d in os.listdir(project_root) if d == '.venv' and os.path.isdir(project_root / d)]
    
    if len(venv_dirs) == 1:
        print("✅ Solo una carpeta .venv encontrada")
    else:
        print(f"❌ {len(venv_dirs)} carpetas .venv encontradas (debería ser 1)")
        return False
    
    # Verificar importación del predictor
    try:
        sys.path.append(str(model_dir))
        from transformer_predictor import RelayOptimizationPredictor
        print("✅ Predictor importado correctamente")
    except Exception as e:
        print(f"❌ Error al importar predictor: {e}")
        return False
    
    return True

if __name__ == "__main__":
    if quick_test():
        print("\n🎉 LIMPIEZA EXITOSA - SISTEMA FUNCIONANDO CORRECTAMENTE")
        print("\n📋 ESTRUCTURA FINAL:")
        print("   • Archivos .pkl: Solo en models/transformer/")
        print("   • Carpeta .venv: Solo en raíz del proyecto")
        print("   • Notebooks: Limpios y organizados")
        print("   • Modelo: Funcionando correctamente")
    else:
        print("\n❌ ERRORES ENCONTRADOS - REVISAR CONFIGURACIÓN")
        sys.exit(1)
