
import torch
import torch.nn as nn
import numpy as np
import pickle
import json
import math

class PositionalEncoding(nn.Module):
    def __init__(self, d_model, max_len=5000):
        super(PositionalEncoding, self).__init__()
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0).transpose(0, 1)
        self.register_buffer('pe', pe)

    def forward(self, x):
        x = x + self.pe[:x.size(0), :]
        return x

class RelayOptimizationTransformer(nn.Module):
    def __init__(self, input_dim, output_dim, d_model, nhead, num_encoder_layers, dim_feedforward, dropout=0.1):
        super(RelayOptimizationTransformer, self).__init__()
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.d_model = d_model

        self.input_proj = nn.Linear(input_dim, d_model)
        self.pos_encoder = PositionalEncoding(d_model)
        
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=dim_feedforward,
            dropout=dropout,
            batch_first=False
        )
        self.transformer_encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_encoder_layers)
        self.output_proj = nn.Linear(d_model, output_dim)
        
        self._init_weights()

    def _init_weights(self):
        initrange = 0.1
        self.input_proj.weight.data.uniform_(-initrange, initrange)
        self.output_proj.weight.data.uniform_(-initrange, initrange)

    def forward(self, src):
        # Asegurar que src tenga 3 dimensiones (batch_size, sequence_length, features)
        if src.dim() == 2:
            # Si src tiene 2 dimensiones, agregar una dimensión de secuencia
            src = src.unsqueeze(1)  # (batch_size, 1, features)
        
        src = self.input_proj(src) * math.sqrt(self.d_model)
        # Transformer espera (sequence_length, batch_size, features)
        src = src.permute(1, 0, 2)
        src = self.pos_encoder(src)
        output = self.transformer_encoder(src)
        # Volver a (batch_size, sequence_length, features)
        output = output.permute(1, 0, 2)
        # Promedio sobre la secuencia para obtener (batch_size, features)
        output = output.mean(dim=1)
        output = self.output_proj(output)
        return output

class RelayOptimizationPredictor:
    def __init__(self, model_path, scaler_input_path, scaler_target_path, best_params_path):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Cargar parámetros
        with open(best_params_path, 'r') as f:
            self.best_params = json.load(f)
        
        # Cargar scalers
        with open(scaler_input_path, 'rb') as f:
            self.scaler_input = pickle.load(f)
        with open(scaler_target_path, 'rb') as f:
            self.scaler_target = pickle.load(f)
        
        # Crear modelo
        self.model = RelayOptimizationTransformer(
            input_dim=6,
            output_dim=4,
            d_model=self.best_params['d_model'],
            nhead=self.best_params['nhead'],
            num_encoder_layers=self.best_params['num_encoder_layers'],
            dim_feedforward=self.best_params['dim_feedforward'],
            dropout=self.best_params['dropout']
        ).to(self.device)
        
        # Cargar pesos
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model.eval()
    
    def predict_optimization(self, relay_data):
        predictions = []
        
        with torch.no_grad():
            for relay_pair in relay_data:
                # Preparar características de entrada
                input_features = [
                    float(relay_pair['fault']),
                    relay_pair['main_relay']['Ishc'],
                    relay_pair['main_relay']['Time_out'],
                    relay_pair['backup_relay']['Ishc'],
                    relay_pair['backup_relay']['Time_out'],
                    len(relay_data)
                ]
                
                # Normalizar entrada
                input_normalized = self.scaler_input.transform([input_features])
                
                # Convertir a tensor
                input_tensor = torch.tensor(input_normalized, dtype=torch.float32).to(self.device)
                
                # Hacer predicción
                prediction = self.model(input_tensor)
                prediction_np = prediction.cpu().numpy().reshape(-1, 4)[0]
                
                # Desnormalizar predicción
                prediction_denorm = self.scaler_target.inverse_transform([prediction_np])[0]
                
                # Crear resultado
                result = {
                    'main_relay': {
                        'relay': relay_pair['main_relay']['relay'],
                        'TDS': max(0.05, min(0.8, prediction_denorm[0])),
                        'pickup': max(0.05, min(2.0, prediction_denorm[1]))
                    },
                    'backup_relay': {
                        'relay': relay_pair['backup_relay']['relay'],
                        'TDS': max(0.05, min(0.8, prediction_denorm[2])),
                        'pickup': max(0.05, min(2.0, prediction_denorm[3]))
                    }
                }
                
                predictions.append(result)
        
        return predictions
