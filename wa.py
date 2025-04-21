# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
from prophet import Prophet
import joblib
from langchain_community.llms import Ollama
from py2neo import Graph
import geopandas as gpd
import json
import os
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import numpy as np

# Configure page
st.set_page_config(page_title="E-Waste Analytics Dashboard", layout="wide")

# Load Data with error handling
@st.cache_data
def load_data():
    try:
        return pd.read_csv("e_waste_data.csv")
    except FileNotFoundError:
        st.error("E-waste data file not found. Using sample data instead.")
        # Create sample data
        states = ["Karnataka", "Maharashtra", "Tamil Nadu", "Gujarat", "Delhi"]
        devices = ["Mobile Phones", "Computers", "TVs", "Refrigerators"]
        years = list(range(2015, 2023))
        
        data = []
        for state in states:
            for device in devices:
                for year in years:
                    data.append({
                        "state": state,
                        "device_type": device,
                        "year": year,
                        "e_waste_quantity": int(100 * (1 + 0.2 * (year - 2015)) + 50 * (states.index(state) + 1) + 30 * (devices.index(device) + 1)),
                        "hazard_factor": 0.5 + 0.1 * devices.index(device),
                        "recycling_rate": 0.3 + 0.05 * (year - 2015)
                    })
        return pd.DataFrame(data)

# Load data
df = load_data()

# Prophet Forecasting Function
def forecast_e_waste(data, state, device_type=None):
    try:
        if device_type:
            df_filtered = data[(data["state"] == state) & (data["device_type"] == device_type)]
        else:
            df_filtered = data[data["state"] == state]
        
        if df_filtered.empty:
            return None
        
        df_state = df_filtered[["year", "e_waste_quantity"]].rename(columns={"year": "ds", "e_waste_quantity": "y"})
        
        # Convert year to datetime if it's not
        if not pd.api.types.is_datetime64_any_dtype(df_state['ds']):
            df_state['ds'] = pd.to_datetime(df_state['ds'], format='%Y')
        
        model = Prophet()
        model.fit(df_state)
        future = model.make_future_dataframe(periods=5, freq='Y')
        forecast = model.predict(future)
        return forecast
    except Exception as e:
        st.error(f"Forecasting error: {str(e)}")
        return None

# Hazard Prediction using ML models
@st.cache_resource
def load_models():
    try:
        # Try to load XGBoost model
        try:
            xgb_model = joblib.load("xgboost_model.joblib")
        except Exception as e:
            st.warning(f"Could not load XGBoost model: {str(e)}")
            xgb_model = None

        # Try to load CatBoost model with additional error handling
        try:
            original_numpy_version = np.__version__
            
            # Temporarily modify numpy version info if needed
            if hasattr(np, '_ARRAY_API_VERSION'):
                original_api_version = np._ARRAY_API_VERSION
                np._ARRAY_API_VERSION = 1
            
            catboost_model = joblib.load("catboost_model.cbm")
            
            # Restore original numpy version info
            if hasattr(np, '_ARRAY_API_VERSION'):
                np._ARRAY_API_VERSION = original_api_version
                
        except Exception as e:
            st.warning(f"Could not load CatBoost model: {str(e)}")
            st.info("Using fallback prediction method for hazard analysis.")
            catboost_model = None

        if xgb_model is None and catboost_model is None:
            st.warning("Using simplified predictions since models could not be loaded.")
        
        return xgb_model, catboost_model
    except Exception as e:
        st.warning(f"Model loading failed: {str(e)}. Using fallback predictions.")
        return None, None

def predict_hazard_and_value(data, state, device_type, xgb_model, catboost_model):
    # Filter data for the specific state and device type
    filtered_data = data[(data["state"] == state) & (data["device_type"] == device_type)]
    
    if filtered_data.empty:
        return None, None
    
    def normalize_hazard_score(score):
        """Helper function to normalize hazard score to 0-10 range"""
        try:
            # Convert to float and handle any potential string/invalid values
            score = float(score)
            # If score is unusually large, apply logarithmic scaling
            if score > 100:
                score = np.log10(score + 1) * 2
            # Ensure the score is between 0 and 10
            return min(10, max(0, score))
        except (ValueError, TypeError):
            return 5.0  # Return middle value if conversion fails
    
    # If no models are available, use simple calculations based on available data
    if xgb_model is None or catboost_model is None:
        if 'hazard_factor' in filtered_data.columns and 'recycling_rate' in filtered_data.columns:
            recent_data = filtered_data.sort_values('year', ascending=False).iloc[0]
            hazard_score = normalize_hazard_score(recent_data.get('hazard_factor', 0.5) * 10)
            avg_quantity = filtered_data['e_waste_quantity'].mean()
            econ_value = avg_quantity * 1000
            return hazard_score, econ_value
        else:
            return 5.0, filtered_data['e_waste_quantity'].mean() * 1000
    
    # Prepare features for prediction with actual models
    try:
        features = filtered_data.drop(columns=["e_waste_quantity", "state", "year", "device_type"])
        
        if features.empty:
            return None, None
        
        # Calculate mean values for prediction
        user_input = features.mean().values.reshape(1, -1)
        
        # Make predictions and normalize hazard score
        raw_hazard_score = xgb_model.predict(user_input)[0]
        hazard_score = normalize_hazard_score(raw_hazard_score)
        
        econ_value = catboost_model.predict(user_input)[0]
        
        return hazard_score, econ_value
    except Exception as e:
        st.error(f"Prediction error: {str(e)}")
        return 5.0, filtered_data['e_waste_quantity'].mean() * 1000

# Neo4j Connection with better error handling
@st.cache_resource
def connect_neo4j():
    # Get connection details from environment variables or use defaults
    NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "helifort333")
    
    try:
        graph = Graph(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        # Test the connection
        graph.run("MATCH (n) RETURN count(n) AS count LIMIT 1").data()
        return graph
    except Exception as e:
        st.warning(f"Neo4j connection failed: {str(e)}")
        return None

def run_neo4j_query(graph, state=None):
    if graph is None:
        # Return sample data when Neo4j is not available
        sample_data = [
            {"policy": "E-Waste Management Rules 2016", "region": "All India"},
            {"policy": "Extended Producer Responsibility", "region": "All India"},
            {"policy": "State E-Waste Policy", "region": state if state else "Various States"}
        ]
        return pd.DataFrame(sample_data)
    
    try:
        if state:
            query = f"""
            MATCH (p:Policy)-[:AFFECTS]->(r:Region)
            WHERE r.name = '{state}' OR r.name = 'All India'
            RETURN p.name AS policy, r.name AS region
            """
        else:
            query = """
            MATCH (p:Policy)-[:AFFECTS]->(r:Region)
            RETURN p.name AS policy, r.name AS region
            """
        result = graph.run(query).to_data_frame()
        if result.empty:
            # If no results found, return sample data
            return pd.DataFrame([
                {"policy": "E-Waste Management Rules 2016", "region": "All India"},
                {"policy": "Extended Producer Responsibility", "region": "All India"},
                {"policy": "State E-Waste Policy", "region": state if state else "Various States"}
            ])
        return result
    except Exception as e:
        st.error(f"Failed to query Neo4j: {str(e)}")
        # Return sample data as fallback
        return pd.DataFrame([
            {"policy": "E-Waste Management Rules 2016", "region": "All India"},
            {"policy": "Extended Producer Responsibility", "region": "All India"},
            {"policy": "State E-Waste Policy", "region": state if state else "Various States"}
        ])

# Ollama LLM Setup with error handling
@st.cache_resource
def load_llm():
    try:
        return Ollama(model="llama3.2:3b", temperature=0.1)
    except Exception as e:
        st.warning(f"Failed to load Ollama LLM: {str(e)}. Using fallback responses.")
        return None

def ask_policy_question(llm, query):
    if llm is None:
        # Provide a generic response if LLM is not available
        return """
        E-waste management is governed by the E-Waste Management Rules 2016 (amended in 2018).
        Key points include:
        - Extended Producer Responsibility (EPR)
        - Collection targets for manufacturers
        - Proper recycling and disposal requirements
        - Registration of e-waste handlers
        
        Most states implement these national policies with some regional variations.
        """
    
    try:
        prompt = f"""You are an expert in e-waste management and environmental policies. 
        Please provide a detailed response to the following question about e-waste policies:
        
        Question: {query}
        
        Provide a clear, structured response focusing on:
        - Key policy points
        - Implementation status
        - Environmental impact
        - Economic implications
        """
        return llm.invoke(prompt)
    except Exception as e:
        st.error(f"LLM query failed: {str(e)}")
        return "Unable to process your query at this time. Please try again later."

# GeoJSON loading with proper error handling
@st.cache_data
def load_geojson(): 
    try:
        with open("india_state_geo.json", "r", encoding='utf-8') as f:
            geojson_data = json.load(f)
            # Verify the structure
            if 'features' not in geojson_data:
                st.error("Invalid GeoJSON structure: 'features' not found")
                return None
            return geojson_data
    except FileNotFoundError:
        st.warning("GeoJSON file not found. Please ensure 'india_state_geo.json' is in the correct location.")
        return None
    except json.JSONDecodeError:
        st.error("Invalid GeoJSON file format.")
        return None

def normalize_state_names(df):
    """Normalize state names to match GeoJSON format"""
    state_mapping = {
        'ANDHRA PRADESH': 'Andhra Pradesh',
        'ARUNACHAL PRADESH': 'Arunachal Pradesh',
        'ASSAM': 'Assam',
        'BIHAR': 'Bihar',
        'CHHATTISGARH': 'Chhattisgarh',
        'GOA': 'Goa',
        'GUJARAT': 'Gujarat',
        'HARYANA': 'Haryana',
        'HIMACHAL PRADESH': 'Himachal Pradesh',
        'JHARKHAND': 'Jharkhand',
        'KARNATAKA': 'Karnataka',
        'KERALA': 'Kerala',
        'MADHYA PRADESH': 'Madhya Pradesh',
        'MAHARASHTRA': 'Maharashtra',
        'MANIPUR': 'Manipur',
        'MEGHALAYA': 'Meghalaya',
        'MIZORAM': 'Mizoram',
        'NAGALAND': 'Nagaland',
        'ODISHA': 'Odisha',
        'PUNJAB': 'Punjab',
        'RAJASTHAN': 'Rajasthan',
        'SIKKIM': 'Sikkim',
        'TAMIL NADU': 'Tamil Nadu',
        'TELANGANA': 'Telangana',
        'TRIPURA': 'Tripura',
        'UTTAR PRADESH': 'Uttar Pradesh',
        'UTTARAKHAND': 'Uttarakhand',
        'WEST BENGAL': 'West Bengal',
        'DELHI': 'Delhi',
        'JAMMU AND KASHMIR': 'Jammu and Kashmir',
        'LADAKH': 'Ladakh',
        'PUDUCHERRY': 'Puducherry',
        'CHANDIGARH': 'Chandigarh',
        'DADRA AND NAGAR HAVELI AND DAMAN AND DIU': 'Dadra and Nagar Haveli and Daman and Diu',
        'LAKSHADWEEP': 'Lakshadweep',
        'ANDAMAN AND NICOBAR ISLANDS': 'Andaman and Nicobar Islands'
    }
    
    df['state'] = df['state'].str.upper().map(state_mapping).fillna(df['state'])
    return df

# Business value calculation function - NEW
def calculate_business_value(data, state, device_type):
    filtered_data = data[(data["state"] == state) & (data["device_type"] == device_type)]
    
    if filtered_data.empty:
        return None, None, None
    
    # Calculate average e-waste quantity
    avg_quantity = filtered_data['e_waste_quantity'].mean()
    
    # Estimate setup cost based on e-waste quantity
    setup_cost = avg_quantity * 1500  # Assuming ₹1500 per unit for setup
    
    # Use recycling_rate if available, otherwise use default value
    if 'recycling_rate' in filtered_data.columns:
        recycling_rate = filtered_data['recycling_rate'].mean()
    else:
        recycling_rate = 0.4  # Default recycling rate
    
    # Calculate revenue based on e-waste quantity and recycling rate
    revenue = avg_quantity * recycling_rate * 3500  # Assuming ₹3500 per unit revenue
    
    # Calculate ROI
    roi = (revenue - setup_cost) / setup_cost if setup_cost > 0 else 0
    
    return revenue, setup_cost, roi

def main():
    st.title("E-Waste Analytics Dashboard")
    
    # Create sidebar for filters
    st.sidebar.title("Filters")
    state = st.sidebar.selectbox("Select State", sorted(df["state"].unique()))
    device = st.sidebar.selectbox("Select Device Type", sorted(df["device_type"].unique()))
    
    # Main content with tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Forecasting", 
        "🔍 Hazard Analysis", 
        "📋 Policy Intelligence", 
        "🗺️ Geo Visualization", 
        "💰 Business Value"
    ])
    
    # Tab 1: Forecasting
    with tab1:
        st.header("E-Waste Forecasting")
        forecast = forecast_e_waste(df, state, device)
        
        if forecast is None:
            st.warning(f"Not enough data to forecast for {device} in {state}")
        else:
            fig1 = px.line(
                forecast, 
                x='ds', 
                y=['yhat', 'yhat_lower', 'yhat_upper'], 
                title=f"E-Waste Forecast for {device} in {state}",
                labels={'ds': 'Year', 'value': 'E-Waste Quantity', 'variable': 'Forecast Type'},
                color_discrete_map={
                    'yhat': 'blue',
                    'yhat_lower': 'lightblue',
                    'yhat_upper': 'lightblue'
                }
            )
            fig1.update_layout(legend_title_text='')
            st.plotly_chart(fig1, use_container_width=True)
            
            # Add forecast metrics
            current_year_forecast = forecast[forecast['ds'].dt.year == 2023]['yhat'].values[0] if len(forecast[forecast['ds'].dt.year == 2023]) > 0 else 0
            next_year_forecast = forecast[forecast['ds'].dt.year == 2024]['yhat'].values[0] if len(forecast[forecast['ds'].dt.year == 2024]) > 0 else 0
            growth_rate = ((next_year_forecast - current_year_forecast) / current_year_forecast) * 100 if current_year_forecast > 0 else 0
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Current Year Forecast", f"{current_year_forecast:.0f} units")
            col2.metric("Next Year Forecast", f"{next_year_forecast:.0f} units")
            col3.metric("Growth Rate", f"{growth_rate:.1f}%", f"{growth_rate:.1f}%")
    
    # Tab 2: Hazard Analysis
    with tab2:
        st.header("Hazard Score & Economic Value Prediction")
        xgb_model, catboost_model = load_models()
        hazard_score, econ_value = predict_hazard_and_value(df, state, device, xgb_model, catboost_model)
        
        if hazard_score is None or econ_value is None:
            st.warning(f"No data available for {device} in {state}")
        else:
            # Create two columns for metrics
            col1, col2 = st.columns(2)
            with col1:
                # Format hazard score to 2 decimal places
                formatted_hazard = f"{hazard_score:.2f}"
                st.metric("Predicted Hazard Score", formatted_hazard)
                
                # Visualization for hazard score
                fig_hazard = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=hazard_score,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Hazard Score"},
                    number={'suffix': '/10', 'valueformat': '.2f'},  # Add /10 suffix and format to 2 decimal places
                    gauge={
                        'axis': {'range': [0, 10], 'tickwidth': 1, 'tickcolor': "white"},
                        'bar': {'color': "darkred"},
                        'steps': [
                            {'range': [0, 3.33], 'color': "green"},
                            {'range': [3.33, 6.66], 'color': "yellow"},
                            {'range': [6.66, 10], 'color': "red"}
                        ],
                        'threshold': {
                            'line': {'color': "white", 'width': 4},
                            'thickness': 0.75,
                            'value': hazard_score
                        }
                    }
                ))
                
                fig_hazard.update_layout(
                    font={'color': "white"},
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)"
                )
                
                st.plotly_chart(fig_hazard, use_container_width=True)
            
            with col2:
                # Format economic value with Indian currency format
                formatted_value = f"₹{econ_value:,.2f}"
                st.metric("Estimated Economic Value", formatted_value)
                # Historical trend
                filtered_data = df[(df["state"] == state) & (df["device_type"] == device)]
                if not filtered_data.empty:
                    fig_trend = px.line(
                        filtered_data, 
                        x="year", 
                        y="e_waste_quantity",
                        title=f"Historical E-Waste Trend for {device} in {state}",
                        markers=True
                    )
                    fig_trend.update_layout(
                        xaxis_title="Year",
                        yaxis_title="E-Waste Quantity (units)"
                    )
                    st.plotly_chart(fig_trend, use_container_width=True)
    
    # Tab 3: Policy Intelligence
    with tab3:
        st.header("Policy Intelligence")
        
        # Policy query using LLM
        policy_query = st.text_area(
            "Ask a question about e-waste policies:", 
            f"What are the specific policies for {device} disposal in {state}?"
        )
        
        llm = load_llm()
        if st.button("Get Policy Information"):
            with st.spinner("Analyzing policy information..."):
                response = ask_policy_question(llm, policy_query)
            st.write(response)

        # Neo4j Policy Graph
        st.subheader("Policy Graph")
        
        # Create two columns for better layout
        col1, col2 = st.columns([2, 1])
        
        with col1:
            graph = connect_neo4j()
            policy_df = run_neo4j_query(graph, state)
            
            if not policy_df.empty:
                # Create a bar chart for policies
                fig_policy = px.bar(
                    policy_df,
                    x="policy",
                    y=[1] * len(policy_df),
                    color="region",
                    title=f"Policies Affecting {state}",
                    labels={"policy": "Policy Name", "region": "Region"},
                    height=400
                )
                fig_policy.update_layout(
                    showlegend=True,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                st.plotly_chart(fig_policy, use_container_width=True)
            else:
                st.warning("No policy data available for the selected state.")
        
        with col2:
            if not policy_df.empty:
                st.write("### Policy Details")
                for _, row in policy_df.iterrows():
                    with st.expander(f"{row['policy']} - {row['region']}"):
                        st.write(f"**Policy:** {row['policy']}")
                        st.write(f"**Region:** {row['region']}")
                        st.write("This policy affects e-waste management in the specified region.")
        
        # Add policy setup instructions if no data or connection issues
        if graph is None:
            st.info("""
            To set up Neo4j and add sample policy data:
            
            1. Install Neo4j Desktop from https://neo4j.com/download/
            2. Create a new project and database
            3. Run these Cypher queries in Neo4j Browser:
            ```
            CREATE (p1:Policy {name: 'E-Waste Management Rules 2016'})
            CREATE (p2:Policy {name: 'Extended Producer Responsibility'})
            CREATE (r1:Region {name: 'Karnataka'})
            CREATE (r2:Region {name: 'Maharashtra'})
            CREATE (r3:Region {name: 'All India'})
            CREATE (p1)-[:AFFECTS]->(r3)
            CREATE (p2)-[:AFFECTS]->(r1)
            CREATE (p2)-[:AFFECTS]->(r2)
            ```
            4. Update the connection details in the app
            """)
    
    # Tab 4: Geo Visualization
    with tab4:
        st.header("Geo Visualization")
        
        # Load GeoJSON data
        geojson_data = load_geojson()
        
        # Filter and prepare state data
        state_map = df[df["device_type"] == device].groupby("state")["e_waste_quantity"].sum().reset_index()
        state_map = normalize_state_names(state_map)
        
        if geojson_data:
            try:
                # Create choropleth map with geojson
                fig_map = px.choropleth(
                    state_map,
                    geojson=geojson_data,
                    featureidkey="properties.ST_NM",
                    locations="state",
                    color="e_waste_quantity",
                    title=f"State-wise {device} E-Waste Quantity",
                    color_continuous_scale="Viridis",
                    hover_data={"state": True, "e_waste_quantity": ":.2f"},
                    labels={"e_waste_quantity": "E-Waste Quantity", "state": "State"}
                )
                
                # Update layout for better visualization
                fig_map.update_geos(
                    fitbounds="locations",
                    visible=False,
                    showcoastlines=True,
                    showsubunits=True,
                    subunitcolor="white",
                    center=dict(lat=20.5937, lon=78.9629),  # Center of India
                    projection_scale=4
                )
                
                fig_map.update_layout(
                    margin={"r":0,"t":30,"l":0,"b":0},
                    height=600,
                    geo=dict(
                        showframe=False,
                        showcoastlines=True,
                        projection_type='mercator',
                        lonaxis_range=[68, 98],  # Longitude range for India
                        lataxis_range=[6, 38]    # Latitude range for India
                    )
                )
                
                # Add hover template
                fig_map.update_traces(
                    hovertemplate="<b>State:</b> %{location}<br>" +
                                "<b>E-Waste Quantity:</b> %{z:.2f}<br><extra></extra>"
                )
                
                st.plotly_chart(fig_map, use_container_width=True)
                
                # Debug information
                if st.checkbox("Show Debug Information"):
                    st.write("### Data Verification")
                    st.write("States in your data:", sorted(state_map['state'].unique()))
                    st.write("States in GeoJSON:", sorted([feature['properties']['ST_NM'] for feature in geojson_data['features']]))
                    
                    # Show states that might not be matching
                    geojson_states = set([feature['properties']['ST_NM'] for feature in geojson_data['features']])
                    data_states = set(state_map['state'].unique())
                    missing_states = data_states - geojson_states
                    if missing_states:
                        st.warning(f"States in your data that don't match GeoJSON: {missing_states}")
                
                # Add a data table below the map
                st.subheader("Detailed State-wise Data")
                detailed_data = state_map.sort_values("e_waste_quantity", ascending=False)
                detailed_data.columns = ["State", "E-Waste Quantity"]
                st.dataframe(
                    detailed_data,
                    use_container_width=True,
                    hide_index=True
                )
                
            except Exception as e:
                st.error(f"Error creating choropleth map: {str(e)}")
                create_fallback_visualization(state_map, device)
        else:
            create_fallback_visualization(state_map, device)
    
    # Tab 5: Business Value Insights
    with tab5:
        st.header("Business Value Insights")
        
        # Calculate business metrics
        revenue, setup_cost, roi = calculate_business_value(df, state, device)
        
        if revenue is None:
            st.warning(f"Not enough data to calculate business value for {device} in {state}")
        else:
            # Create metrics display
            col1, col2, col3 = st.columns(3)
            col1.metric("Estimated Annual Revenue", f"₹{revenue:,.2f}")
            col2.metric("Estimated Setup Cost", f"₹{setup_cost:,.2f}")
            col3.metric("ROI", f"{roi:.2f}x")
            
            # Create business value visualization
            st.subheader("ROI Analysis")
            
            # Create sample data for ROI over multiple years
            years = list(range(2023, 2028))
            cumulative_profit = []
            
            for i, year in enumerate(years):
                # Simple model: increasing revenue each year
                year_revenue = revenue * (1 + 0.1 * i)
                
                if i == 0:
                    # First year includes setup cost
                    year_profit = year_revenue - setup_cost
                else:
                    # Subsequent years only operational costs (30% of revenue)
                    year_profit = year_revenue - (year_revenue * 0.3)
                
                if i == 0:
                    cumulative_profit.append(year_profit)
                else:
                    cumulative_profit.append(cumulative_profit[i-1] + year_profit)
            
            # Create dataframe for visualization
            roi_df = pd.DataFrame({
                'Year': years,
                'Cumulative Profit': cumulative_profit
            })
            
            # Create visualization
            fig_roi = px.line(
                roi_df,
                x='Year',
                y='Cumulative Profit',
                title=f"Projected Cumulative Profit for {device} in {state}",
                markers=True
            )
            
            # Add breakeven point line if applicable
            if any(p >= 0 for p in cumulative_profit):
                # Find breakeven year
                try:
                    breakeven_year = years[next(i for i, p in enumerate(cumulative_profit) if p >= 0)]
                    fig_roi.add_vline(
                        x=breakeven_year, 
                        line_dash="dash", 
                        line_color="green",
                        annotation_text="Breakeven Point",
                        annotation_position="top right"
                    )
                except StopIteration:
                    pass  # No breakeven within the projection period
            
            fig_roi.add_hline(
                y=0, 
                line_dash="solid", 
                line_color="red",
                annotation_text="Breakeven Line",
                annotation_position="left"
            )
            
            st.plotly_chart(fig_roi, use_container_width=True)
            
            # Market potential analysis
            st.subheader("Market Potential Analysis")
            
            # Calculate recovery rates and potential value
            if 'recycling_rate' in df.columns:
                recovery_data = df[(df["device_type"] == device)].groupby("state")[["e_waste_quantity", "recycling_rate"]].mean().reset_index()
                recovery_data["potential_value"] = recovery_data["e_waste_quantity"] * recovery_data["recycling_rate"] * 3500  # Value per unit
                
                fig_potential = px.scatter(
                    recovery_data,
                    x="e_waste_quantity",
                    y="recycling_rate",
                    size="potential_value",
                    color="potential_value",
                    hover_name="state",
                    title=f"Market Potential for {device} Recycling",
                    labels={
                        "e_waste_quantity": "Average E-Waste Quantity",
                        "recycling_rate": "Recovery Rate",
                        "potential_value": "Potential Value (₹)"
                    }
                )
                
                # Highlight selected state
                selected_state_data = recovery_data[recovery_data["state"] == state]
                if not selected_state_data.empty:
                    fig_potential.add_trace(
                        go.Scatter(
                            x=selected_state_data["e_waste_quantity"],
                            y=selected_state_data["recycling_rate"],
                            mode="markers",
                            marker=dict(color="red", size=15, line=dict(color="black", width=2)),
                            name=state,
                            hoverinfo="name"
                        )
                    )
                
                st.plotly_chart(fig_potential, use_container_width=True)
            else:
                st.info("Recovery rate data not available for detailed market potential analysis.")

def create_fallback_visualization(state_map, device):
    """Create a fallback bar chart visualization when map fails"""
    st.warning("Unable to display map visualization. Showing bar chart instead.")
    
    fig_bar = px.bar(
        state_map.sort_values("e_waste_quantity", ascending=False),
        x="state",
        y="e_waste_quantity",
        title=f"State-wise {device} E-Waste Quantity",
        color="e_waste_quantity",
        color_continuous_scale="Viridis",
        labels={"state": "State", "e_waste_quantity": "E-Waste Quantity"}
    )
    
    fig_bar.update_layout(
        xaxis_tickangle=-45,
        height=500,
        margin=dict(b=100)  # Add bottom margin for rotated labels
    )
    
    st.plotly_chart(fig_bar, use_container_width=True)
    
    # Add a data table below the chart
    st.subheader("Detailed State-wise Data")
    detailed_data = state_map.sort_values("e_waste_quantity", ascending=False)
    detailed_data.columns = ["State", "E-Waste Quantity"]
    st.dataframe(
        detailed_data,
        use_container_width=True,
        hide_index=True
    )

def add_state_and_policy_to_neo4j(graph, state_name, policy_name):
    """
    Add a new state and policy to Neo4j database, with relationship between them
    """
    if graph is None:
        st.error("Neo4j connection not available")
        return False
    
    try:
        # Check if state exists already
        result = graph.run(f"MATCH (r:Region {{name: '{state_name}'}}) RETURN r").data()
        if not result:
            # Create state if it doesn't exist
            graph.run(f"CREATE (r:Region {{name: '{state_name}'}})") 
            st.success(f"Added new state: {state_name}")
        
        # Check if policy exists already
        result = graph.run(f"MATCH (p:Policy {{name: '{policy_name}'}}) RETURN p").data()
        if not result:
            # Create policy if it doesn't exist
            graph.run(f"CREATE (p:Policy {{name: '{policy_name}'}})") 
            st.success(f"Added new policy: {policy_name}")
        
        # Check if relationship exists
        result = graph.run(f"""
            MATCH (p:Policy {{name: '{policy_name}'}})-[r:AFFECTS]->(reg:Region {{name: '{state_name}'}}) 
            RETURN r
        """).data()
        
        if not result:
            # Create relationship if it doesn't exist
            graph.run(f"""
                MATCH (p:Policy {{name: '{policy_name}'}})
                MATCH (r:Region {{name: '{state_name}'}})
                CREATE (p)-[:AFFECTS]->(r)
            """)
            st.success(f"Connected policy '{policy_name}' to state '{state_name}'")
        
        return True
    except Exception as e:
        st.error(f"Error adding to Neo4j: {str(e)}")
        return False

if __name__ == "__main__":
    main()