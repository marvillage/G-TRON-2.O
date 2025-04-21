# train_catboost.py
import pandas as pd
from catboost import CatBoostRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib
import numpy as np

# Load and prepare data
df = pd.read_csv("e_waste_data.csv")

# Analyze data distribution
print("\nData Analysis:")
print(f"Total records: {len(df)}")
print("\nTarget variable (economic_value) statistics:")
print(df['economic_recovery_potential'].describe())

# Use actual columns from the dataset
features = ["lead_content_kg", "plastic_content_kg", "e_waste_quantity", "informal_collection_rate"]
target = "economic_recovery_potential"  # Predicting economic value

# Scale features
scaler = StandardScaler()
X = pd.DataFrame(scaler.fit_transform(df[features]), columns=features)
y = df[target]

print("\nFeature statistics after scaling:")
print(X.describe())

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model with optimized parameters
model = CatBoostRegressor(
    iterations=200,
    learning_rate=0.05,
    depth=4,
    l2_leaf_reg=3,
    random_seed=42,
    verbose=0
)

model.fit(X_train, y_train)

# Save both model and scaler
joblib.dump(model, "catboost_model.cbm")
joblib.dump(scaler, "catboost_scaler.joblib")

# Print model performance
y_pred = model.predict(X_test)
mse = ((y_test - y_pred) ** 2).mean()
r2 = 1 - ((y_test - y_pred) ** 2).sum() / ((y_test - y_test.mean()) ** 2).sum()

print(f"\nModel Performance:")

print(f"R2 Score: {r2:.2f}")

# Print feature importance
print("\nFeature Importance:")
importance_dict = dict(zip(features, model.feature_importances_))
sorted_importance = dict(sorted(importance_dict.items(), key=lambda x: x[1], reverse=True))
for feature, importance in sorted_importance.items():
    print(f"{feature}: {importance:.4f}%")
