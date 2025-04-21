import streamlit as st
import pickle
import numpy as np

# Load saved models
with open("esg_model.pkl", "rb") as model_file:
    model_data = pickle.load(model_file)
    model = model_data[0]  # Assuming model is the first element in the tuple

with open("scaler.pkl", "rb") as scaler_file:
    scaler = pickle.load(scaler_file)

with open("label_encoder.pkl", "rb") as le_file:
    label_encoder = pickle.load(le_file)

# Streamlit App
st.title("🌱 EPR Compliance Prediction App")

# User Inputs
esg_score = st.number_input("ESG Score", min_value=0.0, max_value=100.0, value=50.0)
energy_usage = st.number_input("Energy Usage (MWh)", min_value=0.0, value=100.0)
carbon_emissions = st.number_input("Carbon Emissions (tons)", min_value=0.0, value=50.0)
renewable_energy = st.number_input("Renewable Energy Adoption (%)", min_value=0.0, max_value=100.0, value=20.0)
waste_recycling = st.number_input("Waste Recycling Performance (%)", min_value=0.0, max_value=100.0, value=40.0)
water_conservation = st.number_input("Water Conservation (%)", min_value=0.0, max_value=100.0, value=30.0)
regulatory_fines = st.number_input("Regulatory Fines (USD)", min_value=0.0, value=5000.0)
# Add missing features
employee_training = st.number_input("Employee Training Hours", min_value=0.0, value=20.0)
community_engagement = st.number_input("Community Engagement Score", min_value=0.0, max_value=100.0, value=50.0)
supply_chain_score = st.number_input("Supply Chain Sustainability Score", min_value=0.0, max_value=100.0, value=60.0)

# Predict Button
if st.button("Predict Compliance Status"):
    # First scale the original 7 features
    original_features = np.array([[esg_score, energy_usage, carbon_emissions, renewable_energy, 
                                 waste_recycling, water_conservation, regulatory_fines]])
    input_data_scaled = scaler.transform(original_features)
    
    # Add the additional features after scaling
    additional_features = np.array([[employee_training, community_engagement, supply_chain_score]])
    input_data_final = np.hstack([input_data_scaled, additional_features])
    
    # Make prediction
    prediction = model.predict(input_data_final)
    prediction_proba = model.predict_proba(input_data_final)
    compliance_status = label_encoder.inverse_transform(prediction)[0]
    

    if compliance_status == "comply":
        compliance_status = "Non-compliant"


    # Display prediction probabilities
    st.write("### Prediction Probabilities")
    for i, prob in enumerate(prediction_proba[0]):
        status = label_encoder.inverse_transform([i])[0]
        st.write(f"- {status}: {prob:.2%}")

    # Display final result
    st.success(f"✅ Predicted Compliance Status: **{compliance_status}**")