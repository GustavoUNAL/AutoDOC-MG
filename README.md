# AutoDOC-MG: Transformer-Based Relay Optimization

## 📋 Project Overview

This project implements a **Transformer neural network** to optimize relay protection systems in electrical power networks. The transformer learns from Genetic Algorithm (GA) optimization results to predict optimal TDS and pickup values for relay pairs, enabling rapid optimization of new scenarios.

## 🎯 Main Objectives

1. **Train a Transformer model** to learn optimal relay configurations from GA results
2. **Validate model performance** on unseen scenarios
3. **Deploy the model** for real-time relay optimization
4. **Generalize optimization** to new power system configurations

## 🏗️ Project Structure

```
AutoDOC-MG/
├── analysis/
│   └── notebooks/
│       ├── 01.transformer_training.ipynb                     # 🚀 Transformer training
│       ├── 02.transformer_validation.ipynb                   # 🚀 Transformer validation
│       ├── 03.tmt_analysis_automation_all_scenarios.ipynb    # TMT analysis
│       ├── 04.ga_optimization_all_scenarios.ipynb            # GA optimization
│       └── 05.tmt_analysis_ga_specific_scenario.ipynb        # GA-specific analysis
├── data/
│   ├── raw/
│   │   └── automation_results.json                           # Original relay data
│   └── processed/                                            # GA optimization results
├── models/
│   └── transformer/                                          # 🚀 Trained transformer model
│       ├── best_relay_optimization_transformer.pth          # Model weights
│       ├── scaler_input.pkl                                 # Input normalization
│       ├── scaler_target.pkl                                # Target normalization
│       ├── best_params.json                                 # Optimal hyperparameters
│       ├── training_summary.json                            # Training metrics
│       └── transformer_predictor.py                         # Prediction class
├── results/                                                  # Analysis outputs
├── scripts/                                                  # Utility scripts
└── requirements.txt                                          # Dependencies
```

## 🚀 Transformer Model Architecture

### Key Components:
- **PositionalEncoding**: Adds sequence position information
- **TransformerEncoder**: Multi-head attention mechanism
- **Input/Output Projections**: Maps features to/from transformer dimensions
- **Optimization**: Optuna-based hyperparameter tuning

### Input Features (6):
1. Fault current
2. Main relay Ishc
3. Main relay Time_out
4. Backup relay Ishc
5. Backup relay Time_out
6. Number of relay pairs in scenario

### Output Features (4):
1. Main relay TDS
2. Main relay pickup
3. Backup relay TDS
4. Backup relay pickup

## 📊 Usage Instructions

### 1. Environment Setup
```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Training the Transformer
```bash
# Run the training notebook
jupyter notebook analysis/notebooks/01.transformer_training.ipynb
# Execute all cells (Run All button compatible)
```

### 3. Validating the Model
```bash
# Run the validation notebook
jupyter notebook analysis/notebooks/02.transformer_validation.ipynb
# Execute all cells to test model performance
```

### 4. Using the Trained Model
```python
from models.transformer.transformer_predictor import RelayOptimizationPredictor

# Load the predictor
predictor = RelayOptimizationPredictor(
    model_path="models/transformer/best_relay_optimization_transformer.pth",
    scaler_input_path="models/transformer/scaler_input.pkl",
    scaler_target_path="models/transformer/scaler_target.pkl",
    best_params_path="models/transformer/best_params.json"
)

# Make predictions
predictions = predictor.predict_optimization(relay_data)
```

## 🔧 Key Features

### Training Notebook (01.transformer_training.ipynb)
- **Single-cell execution** - Run All button compatible
- **Optuna optimization** - Automated hyperparameter tuning
- **Early stopping** - Prevents overfitting
- **Comprehensive logging** - Detailed progress tracking
- **Model artifacts** - Saves all necessary files for deployment

### Validation Notebook (02.transformer_validation.ipynb)
- **Model loading** - Robust error handling
- **Performance metrics** - MSE, MAE, R², RMSE
- **Generalization testing** - Validates on unseen scenarios
- **Visualization** - Performance charts and analysis

## 📈 Model Performance

The transformer achieves:
- **High R² score** on validation data
- **Low prediction error** for TDS and pickup values
- **Fast inference** for real-time optimization
- **Generalization** to new scenarios

## 🛠️ Dependencies

```
torch>=2.0.0
scikit-learn>=1.3.0
numpy>=1.24.0
pandas>=2.0.0
optuna>=3.0.0
matplotlib>=3.7.0
seaborn>=0.12.0
plotly>=5.15.0
jupyter>=1.0.0
```

## 🎯 Next Steps

1. **Deploy the model** for production use
2. **Integrate with power system simulators**
3. **Extend to multi-objective optimization**
4. **Add real-time monitoring capabilities**
5. **Implement model versioning and A/B testing**

## 📝 Notes

- The transformer is trained on GA optimization results from 68 scenarios
- Model supports both CPU and GPU inference
- All notebooks are optimized for single execution
- Comprehensive error handling ensures robust operation
- Model artifacts are automatically saved for deployment

---

**Status**: ✅ Ready for training and validation
**Last Updated**: October 9, 2024
**Version**: 1.0.0
