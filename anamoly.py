import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest

# Load dataset
df = pd.read_csv("e_waste_anomaly_dataset_with_reasons.csv")

# Train model
model = IsolationForest(contamination=0.05, random_state=42)
model.fit(df.drop(["Label", "Reason"], axis=1))

# Function to determine reason and provide details
def determine_reason(row):
    if row["Gas_Concentration"] > 100:
        return (
            "Hazardous Material Leak",
            "The e-waste item is emitting hazardous gases at levels above the safe threshold. "
            "This could indicate the presence of damaged batteries, capacitors, or other components that are leaking toxic substances. "
            "**Action Required:** Isolate the item immediately, use protective equipment, and dispose of it in a designated hazardous waste facility."
        )
    elif row["Weight"] > 800 or row["Vibration"] > 1.5:
        return (
            "Recycling Efficiency Issue",
            "The e-waste item has an abnormal weight or vibration level, which could indicate improper sorting or contamination with non-recyclable materials. "
            "**Action Required:** Re-examine the item, remove non-recyclable materials, and adjust recycling machinery settings."
        )
    elif row["Temperature"] > 40 or row["Humidity"] > 80:
        return (
            "Component Degradation",
            "The e-waste item is showing signs of component degradation, such as high temperature or humidity levels. "
            "This could indicate that internal components are deteriorating and may become hazardous if not handled properly. "
            "**Action Required:** Inspect the item for damage, store it in a cool, dry place, and prioritize it for recycling."
        )
    else:
        return (
            "Fraudulent E-Waste Disposal",
            "The e-waste item exhibits unusual sensor readings that do not match typical e-waste characteristics. "
            "This could indicate fraudulent disposal practices, such as mixing non-e-waste materials with e-waste. "
            "**Action Required:** Verify the contents, investigate the source, and report the incident to authorities."
        )

# Streamlit app
st.title("E-Waste Anomaly Detection")
st.write("Upload sensor data to detect anomalies in e-waste processing.")

# Input fields
weight = st.number_input("Weight (grams)", min_value=0.0, value=500.0)
gas = st.number_input("Gas Concentration (ppm)", min_value=0.0, value=50.0)
temp = st.number_input("Temperature (°C)", min_value=0.0, value=25.0)
humidity = st.number_input("Humidity (%)", min_value=0.0, value=60.0)
vibration = st.number_input("Vibration (g-force)", min_value=0.0, value=1.0)

# Predict button
if st.button("Detect Anomaly"):
    input_data = np.array([[weight, gas, temp, humidity, vibration]])
    prediction = model.predict(input_data)
    if prediction == -1:
        st.error("Anomaly Detected! This e-waste item requires attention.")
        # Determine reason and details
        row = {"Weight": weight, "Gas_Concentration": gas, "Temperature": temp, "Humidity": humidity, "Vibration": vibration}
        reason, details = determine_reason(row)
        st.write(f"**Reason:** {reason}")
        st.write(f"**Details:** {details}")
    else:
        st.success("No Anomaly Detected. This e-waste item is normal.")

# Display dataset
st.write("Sample Dataset:")
st.dataframe(df.head())