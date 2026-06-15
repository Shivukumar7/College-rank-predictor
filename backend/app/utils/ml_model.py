import os
import joblib
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor

def get_ml_prediction(
    model_name: str, 
    x_train: np.ndarray, 
    y_train: np.ndarray, 
    x_predict: float | list | np.ndarray,
    model_type: str = "rf"
) -> float:
    """
    Trains a Random Forest or XGBoost Regressor if not already cached, and returns the predicted value.
    This model is cached to disk using joblib for fast subsequent predictions.
    """
    cache_dir = os.path.join(os.path.dirname(__file__), "..", "cache")
    os.makedirs(cache_dir, exist_ok=True)
    model_path = os.path.join(cache_dir, f"{model_name}.joblib")
    
    model = None
    if os.path.exists(model_path):
        try:
            model = joblib.load(model_path)
        except Exception:
            model = None
            
    if model is None:
        X = x_train.reshape(-1, 1) if len(x_train.shape) == 1 else x_train
        if model_type == "xgb":
            model = XGBRegressor(n_estimators=150, random_state=42)
        else:
            model = RandomForestRegressor(n_estimators=150, random_state=42)
        
        model.fit(X, y_train)
        joblib.dump(model, model_path)
        
    # Handle prediction input shape
    if isinstance(x_predict, (int, float, np.number)):
        X_pred = np.array([[float(x_predict)]])
    else:
        X_pred = np.array(x_predict).reshape(1, -1)
        
    prediction = model.predict(X_pred)[0]
    return float(prediction)

