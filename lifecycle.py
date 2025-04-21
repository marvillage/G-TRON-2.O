# enhanced_app.py
import streamlit as st
import pandas as pd
import joblib
import numpy as np

# Custom styling for pure blue and black theme appropriate for e-waste software
def set_custom_style():
    st.markdown("""
    <style>
    /* General page styling */
    .stApp {
        background-color: #0F172A;
        color: #94A3B8;
    }
    
    /* Header styling */
    h1, h2, h3 {
        color: #38BDF8;
        font-weight: 600;
    }
    
    /* Form elements */
    .stSlider, .stSelectbox {
        background-color: #1E293B;
        color: #CBD5E1;
        border-radius: 6px;
    }
    
    /* Input label styling */
    .stMarkdown label, .stSlider label, .stSelectbox label {
        color: #64748B;
    }
    
    /* Submit button */
    .stButton>button {
        background-color: #0369A1;
        color: #F1F5F9;
        font-weight: 500;
        border-radius: 6px;
        padding: 10px 20px;
        border: none;
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        background-color: #0284C7;
        box-shadow: 0 4px 12px rgba(2, 132, 199, 0.3);
    }
    
    /* Lifecycle stage styling - using blue shades on dark backgrounds */
    .new-stage { 
        background-color: #0F172A; 
        border-left: 5px solid #38BDF8; 
        padding: 15px; 
        border-radius: 8px;
        margin: 20px 0;
        box-shadow: 0 2px 8px rgba(56, 189, 248, 0.2);
    }
    
    .inuse-stage { 
        background-color: #0F172A; 
        border-left: 5px solid #0EA5E9; 
        padding: 15px; 
        border-radius: 8px;
        margin: 20px 0;
        box-shadow: 0 2px 8px rgba(14, 165, 233, 0.2);
    }
    
    .aging-stage { 
        background-color: #0F172A; 
        border-left: 5px solid #0284C7; 
        padding: 15px; 
        border-radius: 8px;
        margin: 20px 0;
        box-shadow: 0 2px 8px rgba(2, 132, 199, 0.2);
    }
    
    .endoflife-stage { 
        background-color: #0F172A; 
        border-left: 5px solid #1D4ED8; 
        padding: 15px; 
        border-radius: 8px;
        margin: 20px 0;
        box-shadow: 0 2px 8px rgba(29, 78, 216, 0.2);
    }
    
    /* Dividers */
    hr {
        margin: 25px 0;
        border-color: #334155;
    }
    
    /* Key factors section */
    .json-output {
        background-color: #1E293B;
        color: #E2E8F0;
        padding: 15px;
        border-radius: 8px;
        margin-top: 15px;
    }
    
    /* E-waste themed icon colors */
    .icon-recycle {
        color: #0891B2;
    }
    
    /* Card container for form */
    .form-card {
        background-color: #1E293B;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(2, 132, 199, 0.2);
        margin-bottom: 20px;
    }
    
    /* Streamlit specific elements */
    .stTextInput>div>div>input, .stSelectbox>div>div>div, .stNumberInput>div>div>input {
        background-color: #334155;
        color: #F1F5F9;
        border: 1px solid #475569;
    }
    
    .stSlider>div>div>div {
        background-color: #334155;
    }
    
    .stSlider>div>div>div>div {
        background-color: #0EA5E9;
    }
    
    /* Factors cards */
    .factor-card {
        background-color: #1E293B; 
        padding: 10px; 
        border-radius: 8px; 
        text-align: center; 
        box-shadow: 0 2px 5px rgba(56, 189, 248, 0.2);
        border: 1px solid #334155;
    }
    </style>
    """, unsafe_allow_html=True)

def predict_lifecycle(input_data, model):
    # First try model prediction
    try:
        prediction = model.predict(input_data)[0]
        return prediction
    except:
        # Fallback to rule-based if model fails
        age = input_data['age'].values[0]
        if age <= 12: return 0
        elif age <= 48: return 1
        elif age <= 72: return 2
        else: return 3

def app():
    set_custom_style()
    
    # App header with icon and title
    st.markdown("""
    <div style="display: flex; align-items: center; margin-bottom: 10px;">
        <h1 style="margin: 0;">♻️ E-Waste Lifecycle Predictor</h1>
    </div>
    <p style="color: #94A3B8; font-size: 18px;">Predict the lifecycle stage of your electronic devices for better recycling decisions</p>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Load model with fallback
    try:
        model = joblib.load('enhanced_e_waste_model.pkl')
    except:
        model = None
        
    
    # Input form with enhanced styling
    st.markdown('<div class="form-card">', unsafe_allow_html=True)
    with st.form("prediction_form"):
        st.markdown('<h3 style="color: #38BDF8;">📱 Device Information</h3>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            device_type = st.selectbox("Device Type", ['smartphone', 'laptop', 'tablet', 'TV', 'refrigerator'])
            age = st.slider("Age (months)", 0, 120, 24, key="age_slider")
            usage_hours = st.slider("Daily Usage Hours", 0.0, 24.0, 8.0)
            repairs = st.slider("Number of Repairs", 0, 10, 0)
            
        with col2:
            battery_health = st.slider("Battery Health (%)", 0, 100, 100)
            performance_score = st.slider("Performance Score (1-10)", 1, 10, 8)
            environment = st.selectbox("Environmental Conditions", ['optimal', 'moderate', 'harsh'])
            manufacturer = st.selectbox("Manufacturer", ['Samsung', 'Apple', 'LG', 'Sony', 'Dell'])
        
        price = st.slider("Purchase Price (USD)", 50, 5000, 1000)
        last_update = st.slider("Months Since Last Update", 0, 60, 3)
        
        submitted = st.form_submit_button("Predict Lifecycle Stage")
    st.markdown('</div>', unsafe_allow_html=True)
    
    if submitted:
        input_data = pd.DataFrame({
            'device_type': [device_type],
            'age': [age],
            'usage_hours': [usage_hours],
            'repairs': [repairs],
            'battery_health': [battery_health],
            'performance_score': [performance_score],
            'environment': [environment],
            'manufacturer': [manufacturer],
            'price': [price],
            'last_update': [last_update]
        })
        
        # Get prediction
        stage = predict_lifecycle(input_data, model)
        
        # Display results with enhanced styling
        stage_info = {
            0: {'name': 'New (0-12 months)', 'class': 'new-stage', 'icon': '✨', 'color': '#38BDF8',
                'desc': 'Device is in excellent condition with minimal wear. Optimal performance and efficiency.'},
            1: {'name': 'In-use (13-48 months)', 'class': 'inuse-stage', 'icon': '👍', 'color': '#0EA5E9',
                'desc': 'Device is functioning well but showing normal wear. Consider maintenance checks.'},
            2: {'name': 'Aging (49-72 months)', 'class': 'aging-stage', 'icon': '⚠️', 'color': '#0284C7',
                'desc': 'Device requires attention and may need replacement soon. Check for recycling options.'},
            3: {'name': 'End-of-life (73+ months)', 'class': 'endoflife-stage', 'icon': '♻️', 'color': '#1D4ED8',
                'desc': 'Device has reached end-of-life and should be recycled. Consider eco-friendly disposal.'}
        }
        
        st.markdown(f"""
        <div class="{stage_info[stage]['class']}">
            <h3 style="color: {stage_info[stage]['color']};">Prediction Result</h3>
            <p style="font-size: 22px; color: #F1F5F9;"><strong>{stage_info[stage]['icon']} {stage_info[stage]['name']}</strong></p>
            <p style="font-size: 16px; color: #94A3B8;">{stage_info[stage]['desc']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Show key factors with enhanced styling
        st.markdown('<h3 style="margin-top: 30px; color: #38BDF8;">📊 Key Factors</h3>', unsafe_allow_html=True)
        
        factors = {
            'Age': f"{age} months",
            'Battery Health': f"{battery_health}%",
            'Performance Score': f"{performance_score}/10",
            'Repair Count': repairs
        }
        
        # Custom display for factors
        cols = st.columns(4)
        for i, (factor, value) in enumerate(factors.items()):
            with cols[i]:
                st.markdown(f"""
                <div class="factor-card">
                    <p style="color: #64748B; margin-bottom: 5px; font-size: 14px;">{factor}</p>
                    <p style="color: #38BDF8; font-size: 18px; font-weight: 600;">{value}</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Recommendations based on lifecycle stage
        st.markdown('<h3 style="margin-top: 30px; color: #38BDF8;">💡 Recommendations</h3>', unsafe_allow_html=True)
        
        recommendations = {
            0: ["Protect your device with a case and screen protector", 
                "Keep software updated regularly", 
                "Use original charging accessories"],
            1: ["Schedule regular maintenance checks", 
                "Back up your data periodically", 
                "Clean device components regularly"],
            2: ["Consider repair options before replacement", 
                "Research upgrade possibilities", 
                "Start exploring eco-friendly replacements"],
            3: ["Securely erase all personal data", 
                "Find certified e-waste recycling centers", 
                "Consider trade-in or donation programs"]
        }
        
        for i, rec in enumerate(recommendations[stage]):
            st.markdown(f"""
            <div style="display: flex; align-items: center; margin-bottom: 12px;">
                <div style="background-color: #0369A1; color: #F1F5F9; border-radius: 50%; width: 24px; height: 24px; 
                      display: flex; align-items: center; justify-content: center; margin-right: 10px; 
                      box-shadow: 0 2px 4px rgba(2, 132, 199, 0.3);">
                    {i+1}
                </div>
                <div style="color: #CBD5E1;">{rec}</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Environmental impact footer
        st.markdown("""
        <div style="margin-top: 40px; padding: 15px; background-color: #0F172A; border-radius: 8px; 
                   border: 1px solid #334155; box-shadow: 0 4px 12px rgba(2, 132, 199, 0.15);">
            <h4 style="color: #38BDF8; margin-bottom: 10px;">Environmental Impact</h4>
            <p style="color: #94A3B8;">Proper e-waste management helps reduce environmental pollution and conserves valuable resources. 
            By following the recommendations, you contribute to sustainable electronic usage.</p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    app()