# enhanced_model_training.py
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report
import joblib

def create_lifecycle_stage(age):
    """Create labeled data based on age thresholds"""
    if age <= 12: return 0  # New
    elif age <= 48: return 1  # In-use
    elif age <= 72: return 2  # Aging
    else: return 3  # End-of-life

def train_model():
    # Load enhanced data
    df = pd.read_csv('enhanced_e_waste_data.csv')
    
    # Create labels based on age (for supervised learning)
    df['lifecycle_stage'] = df['age'].apply(create_lifecycle_stage)
    
    # Define features and preprocessing
    numeric_features = ['age', 'usage_hours', 'repairs', 'battery_health', 
                       'performance_score', 'price', 'last_update']
    categorical_features = ['device_type', 'environment', 'manufacturer']
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numeric_features),
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
        ])
    
    # Use RandomForest for better decision boundaries
    pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('classifier', RandomForestClassifier(
            n_estimators=100,
            max_depth=8,
            min_samples_leaf=5,
            class_weight='balanced',
            random_state=42
        ))
    ])
    
    # Train model
    X = df.drop('lifecycle_stage', axis=1)
    y = df['lifecycle_stage']
    pipeline.fit(X, y)
    
    # Evaluate
    y_pred = pipeline.predict(X)
    print(classification_report(y, y_pred))
    
    # Save model
    joblib.dump(pipeline, 'enhanced_e_waste_model.pkl')
    print("Model trained and saved to 'enhanced_e_waste_model.pkl'")

if __name__ == "__main__":
    train_model()