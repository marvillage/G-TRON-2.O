import streamlit as st
import pandas as pd
import numpy as np
import joblib
from datetime import datetime
import plotly.express as px
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import matplotlib.pyplot as plt
import os

# Get the project root directory
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
models_dir = os.path.join(project_root, 'models')

# Load trained model and scaler
@st.cache_resource
def load_model():
    try:
        model_path = os.path.join(models_dir, 'e_waste_model.joblib')
        scaler_path = os.path.join(models_dir, 'scaler.joblib')
        metrics_path = os.path.join(models_dir, 'model_metrics.joblib')
        
        if not all(os.path.exists(path) for path in [model_path, scaler_path, metrics_path]):
            st.error("Model files not found. Please run train24.py first to generate the model files.")
            return None, None, None
            
        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)
        metrics = joblib.load(metrics_path)
        return model, scaler, metrics
    except Exception as e:
        st.error(f"Error loading model: {str(e)}")
        return None, None, None

# Load model and handle potential errors
model, scaler, metrics = load_model()
if model is None or scaler is None or metrics is None:
    st.error("Failed to load model. Please ensure you have run train24.py to generate the model files.")
    st.stop()

# Device database (same as before)
DEVICE_DATABASE = {
    'smartphone': {
        'materials': {'gold': 0.034, 'silver': 0.34, 'copper': 8, 'aluminum': 12, 'plastic': 25, 'lithium': 3},
        'complexity': 0.9,
        'base_weight': 150  # grams
    },
    'laptop': {
        'materials': {'gold': 0.25, 'silver': 1.5, 'copper': 80, 'aluminum': 250, 'plastic': 500, 'lithium': 15},
        'complexity': 0.95,
        'base_weight': 2000
    },
    'tablet': {
        'materials': {'gold': 0.05, 'silver': 0.5, 'copper': 15, 'aluminum': 50, 'plastic': 150, 'lithium': 5},
        'complexity': 0.85,
        'base_weight': 500
    },
    'led_tv': {
        'materials': {'gold': 0.1, 'silver': 1.0, 'copper': 50, 'aluminum': 300, 'plastic': 1000},
        'complexity': 0.8,
        'base_weight': 10000
    }
}

# Recovery methods database (same as before)
RECOVERY_METHODS = {
    'mechanical_separation': {
        'name': 'Mechanical Separation',
        'description': 'Shredding and sorting by density/magnetism',
        'suitable_for': ['plastic', 'aluminum', 'copper'],
        'efficiency': {'plastic': 0.85, 'aluminum': 0.9, 'copper': 0.88},
        'cost_per_kg': 0.50
    },
    'pyrometallurgy': {
        'name': 'Pyrometallurgy',
        'description': 'High-temperature smelting for metals',
        'suitable_for': ['gold', 'silver', 'copper', 'aluminum'],
        'efficiency': {'gold': 0.95, 'silver': 0.93, 'copper': 0.91, 'aluminum': 0.85},
        'cost_per_kg': 2.00
    },
    'hydrometallurgy': {
        'name': 'Hydrometallurgy',
        'description': 'Chemical leaching for precious metals',
        'suitable_for': ['gold', 'silver', 'palladium'],
        'efficiency': {'gold': 0.98, 'silver': 0.96, 'palladium': 0.95},
        'cost_per_kg': 5.00
    },
    'battery_special': {
        'name': 'Battery Special Processing',
        'description': 'Specialized lithium and hazardous material recovery',
        'suitable_for': ['lithium'],
        'efficiency': {'lithium': 0.75},
        'cost_per_kg': 8.00
    }
}

# Material prices (simplified)
material_prices = {
    'gold': 58.50, 'silver': 0.75, 'copper': 0.009, 
    'aluminum': 0.002, 'plastic': 0.0005, 'lithium': 0.15
}

# Initialize session state for history
if 'submissions' not in st.session_state:
    st.session_state.submissions = pd.DataFrame(columns=[
        'timestamp', 'device_type', 'model', 'condition', 
        'recovery_method', 'predicted_yield', 'estimated_value'
    ])

# Streamlit UI
st.title('♻️ E-Waste Material Recovery Optimizer (with Trained Model)')
st.markdown("""
This AI-powered tool uses a trained neural network to analyze your e-waste items and recommend 
the most efficient recycling process to maximize material recovery.
""")

# Input form
with st.form("e_waste_form"):
    st.subheader("Device Information")
    
    col1, col2 = st.columns(2)
    device_type = col1.selectbox("Device Type", list(DEVICE_DATABASE.keys()), 
                              format_func=lambda x: x.replace('_', ' ').title())
    model_name = col2.text_input("Model/Brand (optional)", "")
    
    col1, col2 = st.columns(2)
    condition = col1.selectbox("Condition", ["Poor", "Fair", "Good", "Excellent"])
    age = col2.slider("Age (years)", 0, 20, 5)
    
    contains_battery = st.checkbox("Contains battery", value=('lithium' in DEVICE_DATABASE[device_type]['materials']))
    
    submitted = st.form_submit_button("Optimize Recovery")

# Process form submission
if submitted:
    # Get device data
    device_data = DEVICE_DATABASE[device_type].copy()
    
    # Map condition to numerical value
    condition_map = {"Poor": 0.3, "Fair": 0.5, "Good": 0.7, "Excellent": 0.9}
    condition_score = condition_map[condition]
    
    # Prepare input features for model
    input_features = np.array([[
        device_data['complexity'],
        age,
        device_data['base_weight'],
        1 if contains_battery else 0,
        condition_score
    ]])
    
    # Scale features and make prediction
    scaled_features = scaler.transform(input_features)
    predicted_yield = model.predict(scaled_features)[0]
    predicted_yield = max(min(predicted_yield, 0.95), 0.3)  # Clip to reasonable range
    
    # Determine best recovery methods for each material
    material_methods = {}
    material_recovery = {}
    material_values = {}
    
    for material, amount in device_data['materials'].items():
        best_method = None
        best_efficiency = 0
        
        for method_name, method_data in RECOVERY_METHODS.items():
            if material in method_data['suitable_for']:
                if method_data['efficiency'][material] > best_efficiency:
                    best_efficiency = method_data['efficiency'][material]
                    best_method = method_name
        
        if best_method:
            material_methods[material] = best_method
            material_recovery[material] = amount * best_efficiency * predicted_yield
            material_values[material] = material_recovery[material] * material_prices[material]
        else:
            material_recovery[material] = 0
            material_values[material] = 0
    
    # Calculate total value
    total_value = sum(material_values.values())
    
    # Primary recommended method
    if material_methods:
        primary_method = max(set(material_methods.values()), key=list(material_methods.values()).count)
    else:
        primary_method = "No suitable method found"
    
    # Display results
    st.subheader("Optimized Recovery Plan")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Predicted Recovery Yield", f"{predicted_yield*100:.1f}%")
    col2.metric("Estimated Material Value", f"${total_value:.2f}")
    
    if isinstance(primary_method, str):
        col3.metric("Recommended Process", primary_method)
    else:
        col3.metric("Recommended Process", RECOVERY_METHODS[primary_method]['name'])
    
    # Materials breakdown
    st.subheader("Material Recovery Breakdown")
    
    materials_df = pd.DataFrame({
        'Material': list(device_data['materials'].keys()),
        'Amount (g)': list(device_data['materials'].values()),
        'Recovery Method': [RECOVERY_METHODS[m]['name'] if m in RECOVERY_METHODS else 'Not Recovered' 
                          for m in material_methods.values()],
        'Recoverable Amount (g)': [material_recovery[m] for m in device_data['materials'].keys()],
        'Value ($)': [material_values[m] for m in device_data['materials'].keys()]
    })
    
    st.dataframe(materials_df.style.format({
        'Amount (g)': '{:.2f}',
        'Recoverable Amount (g)': '{:.2f}',
        'Value ($)': '{:.2f}'
    }), use_container_width=True)
    
    # Value distribution pie chart
    if total_value > 0:
        fig = px.pie(materials_df, values='Value ($)', names='Material', 
                    title='Material Value Distribution')
        st.plotly_chart(fig, use_container_width=True)
    
    # Save to history
    new_entry = {
        'timestamp': datetime.now(),
        'device_type': device_type,
        'model': model_name,
        'condition': condition,
        'recovery_method': primary_method if isinstance(primary_method, str) else RECOVERY_METHODS[primary_method]['name'],
        'predicted_yield': predicted_yield,
        'estimated_value': total_value
    }
    st.session_state.submissions = pd.concat([
        st.session_state.submissions, 
        pd.DataFrame([new_entry])
    ], ignore_index=True)

# Display history
if not st.session_state.submissions.empty:
    st.subheader("Analysis History")
    st.dataframe(st.session_state.submissions.sort_values('timestamp', ascending=False), 
                use_container_width=True)
def show_model_metrics():
    st.subheader("Model Performance Metrics")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Train R² Score", f"{metrics['train_r2']:.3f}")
    col2.metric("Test R² Score", f"{metrics['test_r2']:.3f}")
    col3.metric("Test RMSE", f"{metrics['test_rmse']:.3f}")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Error Distribution**")
        fig, ax = plt.subplots()
        ax.hist([metrics['train_mae'], metrics['test_mae']], 
                label=['Train MAE', 'Test MAE'])
        ax.set_xlabel("Mean Absolute Error")
        ax.set_ylabel("Frequency")
        ax.legend()
        st.pyplot(fig)
    
    with col2:
        st.markdown("**Metric Comparison**")
        metric_df = pd.DataFrame({
            'Metric': ['RMSE', 'R²', 'MAE'],
            'Train': [metrics['train_rmse'], metrics['train_r2'], metrics['train_mae']],
            'Test': [metrics['test_rmse'], metrics['test_r2'], metrics['test_mae']]
        })
        st.dataframe(metric_df.style.format({
            'Train': '{:.3f}',
            'Test': '{:.3f}'
        }), use_container_width=True)
    
    st.markdown("""
    **Interpretation:**
    - **R² Score**: Closer to 1 is better (1 = perfect prediction)
    - **RMSE**: Lower is better (root mean squared error)
    - **MAE**: Lower is better (mean absolute error)
    """)

# Add this to your Streamlit UI (before or after the model information expander)
with st.expander("📊 Model Accuracy Evaluation"):
    show_model_metrics()

# Update the "About the AI Model" expander in e_waste_app.py
with st.expander("ℹ️ About the AI Model"):
    st.markdown(f"""
    **Machine Learning Model Details:**
    - Model Type: Multi-layer Perceptron (MLP) Regressor
    - Architecture: 2 hidden layers (100, 50 neurons)
    - Activation: ReLU
    - Optimizer: Adam
    - Training Samples: 8,000 (80% of dataset)
    - Test Samples: 2,000 (20% of dataset)
    
    **Last Training Metrics:**
    - Final Train R²: {metrics['train_r2']:.3f}
    - Final Test R²: {metrics['test_r2']:.3f}
    - Final Train RMSE: {metrics['train_rmse']:.3f}
    - Final Test RMSE: {metrics['test_rmse']:.3f}
    - Final Train MAE: {metrics['train_mae']:.3f}
    - Final Test MAE: {metrics['test_mae']:.3f}
    
    **Interpretation Guide:**
    - R² Score ranges from 0 to 1 (1 = perfect prediction)
    - RMSE and MAE show average prediction error (lower is better)
    """)