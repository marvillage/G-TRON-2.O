# train_xgboost.py
import pandas as pd
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib
from sklearn.metrics import mean_squared_error, r2_score
import numpy as np

# Load and prepare data
df = pd.read_csv("e_waste_data.csv")

# Analyze data distribution
print("\nData Analysis:")
print(f"Total records: {len(df)}")
print("\nTarget variable (e_waste_quantity) statistics:")
print(df['e_waste_quantity'].describe())

# Use actual columns from the dataset
features = ["lead_content_kg", "plastic_content_kg", "economic_recovery_potential", "informal_collection_rate"]
target = "e_waste_quantity"

# Scale features
scaler = StandardScaler()
X = pd.DataFrame(scaler.fit_transform(df[features]), columns=features)
y = df[target]

print("\nFeature statistics after scaling:")
print(X.describe())

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model with adjusted parameters
model = XGBRegressor(
    n_estimators=200,          # More trees
    learning_rate=0.05,        # Slower learning rate
    max_depth=4,              # Reduced depth to prevent overfitting
    min_child_weight=5,       # Increased to reduce overfitting
    colsample_bytree=0.8,     # Use 80% of features per tree
    subsample=0.8,            # Use 80% of samples per tree
    gamma=1,                  # Minimum loss reduction
    random_state=42
)

model.fit(X_train, y_train)

# Save both model and scaler
joblib.dump(model, "xgboost_model.joblib")
joblib.dump(scaler, "scaler.joblib")

# Print model performance
y_pred = model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)
print(f"\nModel Performance:")

print(f"R2 Score: {r2:.2f}")

# Print feature importance
print("\nFeature Importance:")
importance_dict = dict(zip(features, model.feature_importances_))
sorted_importance = dict(sorted(importance_dict.items(), key=lambda x: x[1], reverse=True))
for feature, importance in sorted_importance.items():
    print(f"{feature}: {importance:.4f} ({importance*100:.1f}%)")
