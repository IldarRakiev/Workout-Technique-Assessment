import numpy as np
import joblib
from tensorflow.keras.models import load_model
from pathlib import Path
import os

class AutoencoderValidator:
    def __init__(self,
                 model_path="./models/autoencoder_model.h5",
                 scaler_path="./models/feature_scaler.pkl",
                 threshold=0.3872):
        
        base_dir = Path(__file__).resolve().parent.parent
        
        model_path_abs = str(base_dir / "models" / model_path)
        scaler_path_abs = str(base_dir / "models" / scaler_path)

        if not os.path.exists(model_path_abs):
            raise FileNotFoundError(f"Autoencoder model not found: {model_path_abs}")
        if not os.path.exists(scaler_path_abs):
            raise FileNotFoundError(f"Scaler not found: {scaler_path_abs}")

        self.model = load_model(model_path_abs, compile=False)
        self.scaler = joblib.load(scaler_path_abs)
        self.threshold = threshold

    def validate(self, feature_vectors_sequence):

        # Transform to matrix form
        X = np.array(feature_vectors_sequence)

        # Scale
        X_scaled = self.scaler.transform(X)

        print("X_scaled: ", X_scaled)

        # Go through autoencoder
        X_reconstructed = self.model.predict(X_scaled, verbose=0)

        print("X_reconstr: ", X_reconstructed)

        # Reconstruction error
        reconstruction_errors = np.mean((X_scaled - X_reconstructed) ** 2, axis=1)

        print("errors: ", reconstruction_errors)

        # Mean error
        avg_error = float(np.nanmean(reconstruction_errors))

        print("avg_error = ", avg_error)

        is_anomaly = avg_error > self.threshold

        return {
            "avg_reconstruction_error": avg_error,
            "is_anomaly": is_anomaly
        }
