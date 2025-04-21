from flask import Flask, request, jsonify
from flask_cors import CORS
import streamlit as st
import pandas as pd
import numpy as np
from route import optimize_routes, predict_waste_with_llama, load_llama_model
import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize the model at startup
model, tokenizer = load_llama_model()

@app.route('/api/initial-data', methods=['GET'])
def get_initial_data():
    # Sample data
    collection_points = [
        {"location_name": "Ramdaspeth", "latitude": 21.1458, "longitude": 79.0882, "base_waste_tons": 3.5, "area_type": "Commercial"},
        {"location_name": "Dharampeth", "latitude": 21.1352, "longitude": 79.0629, "base_waste_tons": 4.8, "area_type": "Residential"},
        {"location_name": "Sadar", "latitude": 21.1534, "longitude": 79.0857, "base_waste_tons": 7.2, "area_type": "Commercial"},
        {"location_name": "Civil Lines", "latitude": 21.1498, "longitude": 79.0818, "base_waste_tons": 2.9, "area_type": "Residential"},
        {"location_name": "Gandhibagh", "latitude": 21.1519, "longitude": 79.1089, "base_waste_tons": 5.6, "area_type": "Mixed"}
    ]
    
    trucks = [
        {"id": "TRK001", "capacity": 10.0, "current_location": [21.1458, 79.0882], "status": "available"},
        {"id": "TRK002", "capacity": 8.0, "current_location": [21.1352, 79.0629], "status": "available"},
        {"id": "TRK003", "capacity": 5.0, "current_location": [21.1534, 79.0857], "status": "available"}
    ]
    
    return jsonify({
        'collection_points': collection_points,
        'trucks': trucks
    })

@app.route('/api/optimize-routes', methods=['POST'])
def optimize_routes_api():
    try:
        data = request.json
        collection_points = data.get('collection_points', [])
        trucks = data.get('trucks', [])
        
        # Generate routes
        route_plans = optimize_routes(
            api_key="YOUR_GOOGLE_MAPS_API_KEY",
            collection_points=collection_points,
            trucks=trucks,
            llama_model=model,
            tokenizer=tokenizer
        )
        
        return jsonify({
            'status': 'success',
            'route_plans': route_plans
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/predict-waste', methods=['POST'])
def predict_waste_api():
    try:
        data = request.json
        location_data = data.get('location_data')
        day_of_week = datetime.datetime.now().weekday()
        
        prediction = predict_waste_with_llama(
            model, tokenizer, location_data, day_of_week
        )
        
        return jsonify({
            'status': 'success',
            'prediction': prediction
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
