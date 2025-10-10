# Notebooks Organization - AutoDOC-MG Analysis

## 📋 **Sequential Workflow Overview**

The notebooks have been reorganized to follow a logical progression for relay optimization analysis:

### **1️⃣ 01.tmt_analysis_automation_all_scenarios.ipynb**
**📊 TMT Analysis Automation - All Scenarios**
- **Purpose**: Initial analysis of all 68 scenarios using original automation data
- **Input**: `data/raw/automation_results.json`
- **Output**: TMT computation, scenario ranking, problem identification
- **Key Features**: 
  - Loads original data from automation results
  - Computes TMT from scratch for each scenario
  - Identifies problematic scenarios (TMT > 0)
  - Generates comprehensive statistics and visualizations

### **2️⃣ 02.ga_optimization_all_scenarios.ipynb**
**🧬 GA Optimization - All Scenarios**
- **Purpose**: Genetic Algorithm optimization for relay coordination across all scenarios
- **Input**: Results from notebook 01 + raw automation data
- **Output**: Optimized relay settings for all scenarios
- **Key Features**:
  - Batch processing of all scenarios (1-68)
  - GA optimization for each scenario independently
  - Comprehensive reporting and visualizations
  - Organized data storage with proper naming

### **3️⃣ 03.transformer_training.ipynb**
**🤖 Transformer Training for Relay Optimization**
- **Purpose**: Train transformer network to learn from GA optimization data
- **Input**: GA optimization results from notebook 02
- **Output**: Trained transformer model with optimal hyperparameters
- **Key Features**:
  - Uses Optuna for hyperparameter optimization
  - Predicts optimal TDS and pickup values
  - Generalizes optimization for new scenarios
  - Saves trained model and scalers

### **4️⃣ 04.transformer_validation.ipynb**
**✅ Transformer Model Validation and Testing**
- **Purpose**: Validate trained transformer and test generalization capabilities
- **Input**: Trained transformer from notebook 03
- **Output**: Validation metrics, generalization test results
- **Key Features**:
  - Model performance evaluation on validation data
  - Generalization testing on new scenarios
  - Comparison with GA optimization results
  - Performance metrics and visualizations

### **5️⃣ 05.tmt_analysis_ga_specific_scenario.ipynb**
**🔍 Detailed Analysis - Specific Scenario with GA**
- **Purpose**: Deep analysis of specific scenario with best GA results
- **Input**: GA optimization results from notebook 02
- **Output**: Detailed scenario analysis and comparisons
- **Key Features**:
  - Automatic selection of best scenario
  - Detailed coordination analysis (before vs after)
  - Advanced visualizations and parameter comparisons
  - Specific TMT analysis and performance metrics

## 🔄 **Data Flow**

```
Raw Data (automation_results.json)
    ↓
01. TMT Analysis → Identifies problematic scenarios
    ↓
02. GA Optimization → Generates optimized relay settings
    ↓
03. Transformer Training → Learns from GA data
    ↓
04. Transformer Validation → Tests model generalization
    ↓
05. Specific Analysis → Deep dive into best results
```

## 📁 **Output Structure**

- **Results/Plots**: Visualizations and charts
- **Results/Tables**: Statistical tables and metrics
- **Results/Reports**: Detailed analysis reports
- **Models/**: Trained transformer models and scalers
- **Data/Processed**: Processed optimization data

## 🚀 **Execution Order**

Execute notebooks sequentially from 01 to 05 to ensure proper data flow and dependencies are met. Each notebook builds upon the results of the previous ones.

## 📊 **Key Metrics Tracked**

- **TMT (Total Miscoordination Time)**: Primary optimization metric
- **TDS & Pickup Values**: Relay coordination parameters
- **Model Performance**: RMSE, MAE, R² for transformer validation
- **Optimization Statistics**: GA convergence and performance metrics
