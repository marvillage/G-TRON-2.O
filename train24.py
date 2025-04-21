import numpy as np
import pandas as pd
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import joblib
import os
import sys

# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

# Generate synthetic e-waste dataset
def generate_dataset(n_samples=10000):
    np.random.seed(42)
    
    # Features
    complexity = np.random.uniform(0.1, 1, n_samples)  # Device complexity (0.1-1)
    age = np.random.randint(0, 20, n_samples)          # Age in years (0-20)
    weight = np.random.uniform(50, 20000, n_samples)   # Weight in grams (50-20,000)
    has_battery = np.random.choice([0, 1], n_samples, p=[0.3, 0.7])
    condition = np.random.choice([0.3, 0.5, 0.7, 0.9], n_samples)  # Condition scores
    
    # Target - recovery yield (0.3-0.95)
    base_yield = 0.3 + 0.65 * (
        0.4 * complexity + 
        0.1 * (1 - age/20) + 
        0.2 * condition + 
        0.1 * (1 - has_battery*0.2) + 
        0.2 * np.random.normal(0, 0.1, n_samples)
    )
    
    # Create DataFrame
    data = pd.DataFrame({
        'complexity': complexity,
        'age': age,
        'weight': weight,
        'has_battery': has_battery,
        'condition': condition,
        'recovery_yield': np.clip(base_yield, 0.3, 0.95)
    })
    
    return data

# Train model
def train_and_save_model():
    try:
        # Generate dataset
        data = generate_dataset()
        
        # Save the dataset to CSV
        model_dir = os.path.join(project_root, 'models')
        os.makedirs(model_dir, exist_ok=True)
        dataset_path = os.path.join(model_dir, 'e_waste_dataset.csv')
        data.to_csv(dataset_path, index=False)
        print(f"Dataset saved to {dataset_path}")
        
        # Split features and target
        X = data[['complexity', 'age', 'weight', 'has_battery', 'condition']]
        y = data['recovery_yield']
        
        # Split train/test
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Save train and test sets
        train_data = pd.concat([X_train, pd.Series(y_train, name='recovery_yield')], axis=1)
        test_data = pd.concat([X_test, pd.Series(y_test, name='recovery_yield')], axis=1)
        
        train_data.to_csv(os.path.join(model_dir, 'train_dataset.csv'), index=False)
        test_data.to_csv(os.path.join(model_dir, 'test_dataset.csv'), index=False)
        print("Train and test datasets saved successfully")
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train MLP Regressor
        model = MLPRegressor(
            hidden_layer_sizes=(100, 50),
            activation='relu',
            solver='adam',
            max_iter=500,
            random_state=42,
            early_stopping=True
        )
        
        model.fit(X_train_scaled, y_train)
        
        # Evaluate
        train_pred = model.predict(X_train_scaled)
        test_pred = model.predict(X_test_scaled)
        
        print(f"Train RMSE: {np.sqrt(mean_squared_error(y_train, train_pred)):.4f}")
        print(f"Test RMSE: {np.sqrt(mean_squared_error(y_test, test_pred)):.4f}")
        
        # Calculate additional metrics
        train_r2 = r2_score(y_train, train_pred)
        test_r2 = r2_score(y_test, test_pred)
        
        train_mae = mean_absolute_error(y_train, train_pred)
        test_mae = mean_absolute_error(y_test, test_pred)
        
        # Save model and scaler
        joblib.dump(model, os.path.join(model_dir, 'e_waste_model.joblib'))
        joblib.dump(scaler, os.path.join(model_dir, 'scaler.joblib'))
        
        # Save metrics
        metrics = {
            'train_rmse': np.sqrt(mean_squared_error(y_train, train_pred)),
            'test_rmse': np.sqrt(mean_squared_error(y_test, test_pred)),
            'train_r2': train_r2,
            'test_r2': test_r2,
            'train_mae': train_mae,
            'test_mae': test_mae
        }
        
        joblib.dump(metrics, os.path.join(model_dir, 'model_metrics.joblib'))
        
        print("\nModel Metrics:")
        print(f"Train R²: {train_r2:.4f}")
        print(f"Test R²: {test_r2:.4f}")
        print(f"Train MAE: {train_mae:.4f}")
        print(f"Test MAE: {test_mae:.4f}")
        print("Model and scaler saved successfully")
        
    except Exception as e:
        print(f"Error during model training: {str(e)}")
        raise

if __name__ == '__main__':
    train_and_save_model()