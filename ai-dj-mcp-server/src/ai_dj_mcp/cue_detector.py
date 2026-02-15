"""LSTM-based cue point detection."""

import numpy as np
import torch
import torch.nn as nn
from pathlib import Path
from typing import Tuple, Optional
from sklearn.preprocessing import StandardScaler
import joblib


class LSTMNet(nn.Module):
    """LSTM network for cue point prediction."""

    def __init__(self, input_dim: int = 24, hidden_dim: int = 10, output_dim: int = 1, num_layers: int = 1):
        """
        Initialize LSTM network.

        Args:
            input_dim: Input feature dimension (default: 24)
            hidden_dim: Hidden state dimension (default: 10)
            output_dim: Output dimension (default: 1)
            num_layers: Number of LSTM layers (default: 1)
        """
        super(LSTMNet, self).__init__()
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers

        self.lstm = nn.LSTM(
            input_dim,
            hidden_dim,
            num_layers,
            batch_first=True
        )
        self.fc = nn.Linear(hidden_dim, output_dim)
        self.sigmoid = nn.Sigmoid()

        # Xavier initialization
        for name, param in self.lstm.named_parameters():
            if 'weight' in name:
                nn.init.xavier_uniform_(param)

    def forward(self, x: torch.Tensor, hidden: Optional[Tuple[torch.Tensor, torch.Tensor]] = None):
        """
        Forward pass.

        Args:
            x: Input tensor (batch_size, sequence_length, input_dim)
            hidden: Optional hidden state tuple (h_0, c_0)

        Returns:
            Output predictions and final hidden state
        """
        if hidden is None:
            h_0 = torch.zeros(self.num_layers, x.size(0), self.hidden_dim)
            c_0 = torch.zeros(self.num_layers, x.size(0), self.hidden_dim)
            hidden = (h_0, c_0)

        lstm_out, hidden = self.lstm(x, hidden)
        out = self.fc(lstm_out)
        out = self.sigmoid(out)

        return out, hidden


class CuePointDetector:
    """Detects optimal DJ cue points using LSTM neural network."""

    def __init__(self, model_path: Optional[str] = None, scaler_path: Optional[str] = None):
        """
        Initialize cue point detector.

        Args:
            model_path: Path to trained LSTM model (.pth file)
            scaler_path: Path to feature scaler (.joblib file)
        """
        self.model: Optional[LSTMNet] = None
        self.scaler: Optional[StandardScaler] = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        if model_path:
            self.load_model(model_path)
        if scaler_path:
            self.load_scaler(scaler_path)

    def load_model(self, model_path: str) -> None:
        """Load pre-trained LSTM model."""
        self.model = LSTMNet(input_dim=24, hidden_dim=10, output_dim=1, num_layers=1)
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model.to(self.device)
        self.model.eval()

    def load_scaler(self, scaler_path: str) -> None:
        """Load feature scaler."""
        self.scaler = joblib.load(scaler_path)

    def prepare_features(self, features: np.ndarray) -> torch.Tensor:
        """
        Prepare features for LSTM inference.

        Args:
            features: Feature array (num_beats x 24)

        Returns:
            Normalized tensor ready for LSTM input
        """
        if self.scaler is not None:
            features_normalized = self.scaler.transform(features)
        else:
            # Simple normalization if no scaler provided
            features_normalized = (features - features.mean(axis=0)) / (features.std(axis=0) + 1e-8)

        # Convert to tensor (1, num_beats, 24)
        x_tensor = torch.FloatTensor(features_normalized).unsqueeze(0)
        return x_tensor.to(self.device)

    def predict_cue_points(
        self,
        features: np.ndarray,
        beats: np.ndarray,
        num_cues: int = 12,
        align_to_phrase: bool = True
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Predict optimal cue points from beat features.

        Args:
            features: Feature array (num_beats x 24)
            beats: Beat times in seconds
            num_cues: Number of cue points to select (default: 12)
            align_to_phrase: Align cues to 4-beat phrases (default: True)

        Returns:
            Tuple of (cue_point_times, cue_point_indices, confidence_scores)
        """
        if self.model is None:
            raise ValueError("Model not loaded. Call load_model() first.")

        # Prepare features
        x_tensor = self.prepare_features(features)

        # Run inference
        with torch.no_grad():
            predictions, _ = self.model(x_tensor)

        # Get probabilities (num_beats,)
        probabilities = predictions.squeeze().cpu().numpy()

        # Apply phrase alignment (modulo-4 filtering)
        if align_to_phrase:
            # Boost scores for beats aligned with 4-beat phrases
            phrase_mask = np.arange(len(probabilities)) % 4 == 0
            probabilities = probabilities * (1 + phrase_mask * 0.5)

        # Select top N cue points
        top_indices = np.argsort(probabilities)[-num_cues:][::-1]
        top_indices = np.sort(top_indices)  # Sort chronologically

        cue_point_indices = top_indices
        cue_point_times = beats[top_indices]
        confidence_scores = probabilities[top_indices]

        return cue_point_times, cue_point_indices, confidence_scores

    def detect_intro_outro(
        self,
        cue_points: np.ndarray,
        duration: float
    ) -> dict:
        """
        Suggest intro/outro points from detected cues.

        Args:
            cue_points: Array of cue point times
            duration: Track duration in seconds

        Returns:
            Dictionary with intro_start, intro_end, outro_start, outro_end
        """
        if len(cue_points) < 4:
            return {
                'intro_start': 0.0,
                'intro_end': duration * 0.2,
                'outro_start': duration * 0.8,
                'outro_end': duration
            }

        # Simple heuristic: first 2 cues for intro, last 2 for outro
        return {
            'intro_start': float(cue_points[0]),
            'intro_end': float(cue_points[1]),
            'outro_start': float(cue_points[-2]),
            'outro_end': float(cue_points[-1])
        }


def create_dummy_model() -> LSTMNet:
    """
    Create a dummy LSTM model for testing when no pre-trained model is available.

    Returns:
        Initialized LSTMNet model
    """
    model = LSTMNet(input_dim=24, hidden_dim=10, output_dim=1, num_layers=1)
    return model


def create_dummy_scaler() -> StandardScaler:
    """
    Create a dummy scaler for testing.

    Returns:
        Fitted StandardScaler
    """
    scaler = StandardScaler()
    # Fit with dummy data
    dummy_data = np.random.randn(100, 24)
    scaler.fit(dummy_data)
    return scaler
