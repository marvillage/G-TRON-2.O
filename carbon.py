from flask import Flask, request, jsonify
import joblib
from flask_cors import CORS 
import numpy as np

app = Flask(__name__)
CORS(app)
# Load trained model and scaler
model = joblib.load("carbon_footprint_model.pkl")
scaler = joblib.load("scaler2.pkl")

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json  # Expecting JSON input
    
    # Extract features
    input_data = np.array([[data['Weight'], data['Plastic'], data['Aluminum'], data['Copper'], 
                            data['Lithium'], data['Gold'], data['Glass'], 
                            data['Manufacturing Energy'], data['Transport Distance']]])

    # Scale input
    input_scaled = scaler.transform(input_data)

    # Predict carbon footprint
    prediction = model.predict(input_scaled)[0]

    return jsonify({'Estimated Carbon Footprint (kg CO₂e)': round(prediction, 2)})

if __name__ == '__main__':
    app.run(debug=True)
