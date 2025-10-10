# Models Directory

This directory contains all trained models and related files for the AutoDOC-MG project.

## Structure

```
models/
├── transformer/           # Transformer neural network model
│   ├── best_params.json           # Best hyperparameters found by Optuna
│   ├── scaler_input.pkl          # Input data normalizer
│   ├── scaler_target.pkl         # Output data normalizer
│   └── transformer_predictor.py  # Standalone prediction script
└── README.md             # This file
```

## Transformer Model Files

### Core Files
- **`best_params.json`**: Contains the optimal hyperparameters found during training
- **`scaler_input.pkl`**: StandardScaler for normalizing input features
- **`scaler_target.pkl`**: StandardScaler for denormalizing output predictions
- **`transformer_predictor.py`**: Standalone script for making predictions

### Usage

#### From Python
```python
from models.transformer.transformer_predictor import RelayOptimizationPredictor

predictor = RelayOptimizationPredictor(
    model_path='models/transformer/best_relay_optimization_transformer.pth',
    scaler_input_path='models/transformer/scaler_input.pkl',
    scaler_target_path='models/transformer/scaler_target.pkl',
    best_params_path='models/transformer/best_params.json'
)

predictions = predictor.predict_optimization(relay_data)
```

#### From Command Line
```bash
python models/transformer/transformer_predictor.py \
    --model_dir models/transformer \
    --input_file relay_data.json \
    --output_file predictions.json
```

## Training

To train the transformer model, run the training notebook:
- `analysis/notebooks/04.transformer_optimization_training.ipynb`

## Validation

To validate the trained model, run the validation notebook:
- `analysis/notebooks/05.transformer_validation_generalization.ipynb`

## Notes

- The trained model file (`best_relay_optimization_transformer.pth`) will be generated after running the training notebook
- All files are organized in the `transformer/` subdirectory for easy management
- The predictor script is self-contained and can be used independently
