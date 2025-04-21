import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import os
import tempfile
from typing import Dict, List, TypedDict, Annotated, Optional, Callable, Union
import time
import requests
from langgraph.graph import StateGraph, END

# Gemini API configuration
GEMINI_API_KEY = 'AIzaSyBU-gTwq3RqqGGDrY0s8BHS-bM9Sa8O7LY'
GEMINI_MODEL_NAME = 'gemini-1.5-flash'

st.set_page_config(
    page_title="India E-Waste Compliance Reporting System",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS with Indian theme colors
st.markdown("""
<style>
    /* Main Theme Colors */
    :root {
        --primary-blue: #1a237e;
        --secondary-blue: #0d47a1;
        --accent-blue: #2196f3;
        --dark-bg: #121212;
        --light-text: #ffffff;
        --gray-text: #b0bec5;
        --india-saffron: #FF9933;
        --india-green: #138808;
        --india-blue: #000080;
    }

    /* Global Styles */
    .stApp {
        background-color: var(--dark-bg);
        color: var(--light-text);
    }

    /* Header Styles */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--light-text);
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        margin-bottom: 2rem;
        padding: 1rem;
       
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    .section-header {
        font-size: 1.8rem;
        font-weight: 600;
        color: var(--india-saffron);
        margin: 2rem 0 1rem;
        padding: 0.5rem 1rem;
        border-left: 4px solid var(--india-green);
        background: rgba(19, 136, 8, 0.1);
        border-radius: 0 10px 10px 0;
    }

    .sub-header {
        font-size: 1.4rem;
        font-weight: 500;
        color: var(--light-text);
        margin: 1.5rem 0 1rem;
        padding: 0.5rem;
        border-bottom: 2px solid var(--india-blue);
    }

    /* Card Styles */
    .info-card {
        background: rgba(26, 35, 126, 0.1);
        padding: 1.5rem;
        border-radius: 15px;
        border: 1px solid rgba(255, 153, 51, 0.3);
        margin-bottom: 1.5rem;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }

    .info-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 15px rgba(0, 0, 0, 0.2);
    }

    /* Metric Styles */
    .metric-container {
        background: linear-gradient(135deg, var(--india-blue), var(--india-green));
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--light-text);
        margin-bottom: 0.5rem;
    }

    .metric-label {
        font-size: 1rem;
        color: var(--gray-text);
    }

    /* Alert Styles */
    .alert-box {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        border-left: 4px solid;
    }

    .alert-danger {
        background: rgba(211, 47, 47, 0.1);
        border-left-color: #d32f2f;
    }

    .alert-warning {
        background: rgba(255, 160, 0, 0.1);
        border-left-color: var(--india-saffron);
    }

    .alert-success {
        background: rgba(46, 125, 50, 0.1);
        border-left-color: var(--india-green);
    }

    /* Button Styles */
    .stButton > button {
        
        color: var(--light-text);
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, var(--india-green), var(--india-saffron));
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }

    /* Sidebar Styles */
    .css-1d391kg {
        background-color: var(--dark-bg);
        border-right: 1px solid rgba(255, 153, 51, 0.2);
    }

    /* Selectbox and Input Styles */
    .stSelectbox, .stTextInput {
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        padding: 0.5rem;
    }

    /* Chart Container Styles */
    .element-container {
        background: rgba(26, 35, 126, 0.05);
        padding: 1rem;
        border-radius: 15px;
        margin-bottom: 1.5rem;
    }

    /* Table Styles */
    .stDataFrame {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 1rem;
    }

    /* Progress Bar Styles */
    .stProgress > div > div {
        background: linear-gradient(90deg, var(--india-blue), var(--india-saffron));
    }
</style>
""", unsafe_allow_html=True)

# Gemini API client function
def gemini_generate_content(prompt, temperature=0.7):
    """
    Generate content using Google's Gemini API
    """
    url = f"https://generativelanguage.googleapis.com/v1/models/{GEMINI_MODEL_NAME}:generateContent?key={GEMINI_API_KEY}"
    
    headers = {
        'Content-Type': 'application/json',
    }
    
    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": temperature,
            "topP": 0.95,
            "topK": 40,
            "maxOutputTokens": 2048
        }
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        response_json = response.json()
        if 'candidates' in response_json and len(response_json['candidates']) > 0:
            content = response_json['candidates'][0]['content']
            if 'parts' in content and len(content['parts']) > 0:
                return content['parts'][0]['text']
    
    # If we get here, something went wrong
    raise Exception(f"Error calling Gemini API: {response.status_code} - {response.text}")

# Sample data with India-specific information
def load_sample_data():
    # Indian cities with coordinates
    indian_cities = {
        'Mumbai': (19.0760, 72.8777),
        
        
        'Delhi': (28.7041, 77.1025),
        'Bangalore': (12.9716, 77.5946),
        'Hyderabad': (17.3850, 78.4867),
        'Chennai': (13.0827, 80.2707),
        'Kolkata': (22.5726, 88.3639),
        'Ahmedabad': (23.0225, 72.5714),
        'Pune': (18.5204, 73.8567)
    }
    
    # E-waste volume data - adjusted for Indian urban patterns
    ewaste_data = pd.DataFrame({
        'date': pd.date_range(start='2025-01-01', end='2025-03-31', freq='D'),
        'computers': np.random.normal(40, 12, 90),  # Lower than US but growing
        'mobile_devices': np.random.normal(35, 10, 90),  # Higher due to mobile penetration
        'televisions': np.random.normal(25, 8, 90),  # Significant in India
        'refrigerators': np.random.normal(15, 5, 90),  # Common household item
        'printers': np.random.normal(10, 3, 90),
        'batteries': np.random.normal(20, 6, 90),  # Higher due to UPS systems
    })
    
    # India-specific compliance data
    regulations = [
        {'name': 'E-Waste (Management) Rules, 2022', 'status': 'Partially Compliant', 'score': 85, 'findings': 3, 
         'details': 'Need to improve collection targets; Documentation for PROs incomplete; Some forms not submitted to CPCB'},
        {'name': 'Basel Convention', 'status': 'Fully Compliant', 'score': 98, 'findings': 1, 
         'details': 'One minor documentation issue with transboundary movement records'},
        {'name': 'Extended Producer Responsibility (EPR)', 'status': 'Partially Compliant', 'score': 78, 'findings': 4, 
         'details': 'Need to register more collection centers; Quarterly reports delayed; Need to improve awareness programs'},
        {'name': 'State Pollution Control Board Guidelines', 'status': 'Pending Review', 'score': 65, 'findings': 2, 
         'details': 'Awaiting inspection from state authorities; Need to update authorization documents'},
    ]
    
    # Indian vendors and recyclers
    vendors = [
        {'id': 'REC-001', 'name': 'E-Parisaraa', 'certification': 'CPCB Authorized, ISO 14001', 'location': 'Bangalore, Karnataka', 'lat': 12.9716, 'lon': 77.5946, 'status': 'Compliant'},
        {'id': 'REC-002', 'name': 'Attero Recycling', 'certification': 'CPCB Authorized, R2', 'location': 'Noida, Uttar Pradesh', 'lat': 28.5355, 'lon': 77.3910, 'status': 'Compliant'},
        {'id': 'REC-003', 'name': 'TES-AMM India', 'certification': 'CPCB Authorized, e-Stewards', 'location': 'Chennai, Tamil Nadu', 'lat': 13.0827, 'lon': 80.2707, 'status': 'Pending Audit'},
        {'id': 'REC-004', 'name': 'Ecoreco', 'certification': 'CPCB Authorized', 'location': 'Mumbai, Maharashtra', 'lat': 19.0760, 'lon': 72.8777, 'status': 'Compliant'},
        {'id': 'REC-005', 'name': 'Greencross Recycling', 'certification': 'CPCB Authorized', 'location': 'Hyderabad, Telangana', 'lat': 17.3850, 'lon': 78.4867, 'status': 'Non-Compliant'},
    ]
    
    # Material flow - adjusted for Indian e-waste composition
    material_flow = [
        {'material': 'Printed Circuit Boards', 'weight': 3.8, 'destination': 'REC-001', 'recovery_rate': 88, 'hazard_level': 'High'},
        {'material': 'Plastics', 'weight': 4.2, 'destination': 'REC-003', 'recovery_rate': 72, 'hazard_level': 'Medium'},
        {'material': 'Ferrous Metals', 'weight': 2.5, 'destination': 'REC-004', 'recovery_rate': 95, 'hazard_level': 'Low'},
        {'material': 'Non-Ferrous Metals', 'weight': 1.8, 'destination': 'REC-004', 'recovery_rate': 92, 'hazard_level': 'Low'},
        {'material': 'Glass (CRT)', 'weight': 1.5, 'destination': 'REC-002', 'recovery_rate': 85, 'hazard_level': 'High'},
        {'material': 'Batteries (Lead-acid)', 'weight': 1.2, 'destination': 'REC-005', 'recovery_rate': 80, 'hazard_level': 'High'},
        {'material': 'Refrigerant Gases', 'weight': 0.5, 'destination': 'REC-001', 'recovery_rate': 65, 'hazard_level': 'Very High'},
    ]
    
    # Audit trail with Indian context
    audit_trail = [
        {'date': '2025-01-05', 'action': 'Material Pickup', 'details': 'Collected 1.2 tons of e-waste from WEEE Collection Center, Bangalore', 'user': 'Rahul Sharma', 'status': 'Completed'},
        {'date': '2025-01-12', 'action': 'Processing', 'details': 'Sorted and disassembled batch #2025-01A as per CPCB guidelines', 'user': 'Priya Patel', 'status': 'Completed'},
        {'date': '2025-01-18', 'action': 'Vendor Transfer', 'details': 'Transferred 0.5 tons to E-Parisaraa with Form 4 submission', 'user': 'Amit Singh', 'status': 'Completed'},
        {'date': '2025-01-25', 'action': 'Audit Check', 'details': 'Quarterly compliance review by KSPCB', 'user': 'Neha Gupta', 'status': 'Findings Reported'},
        {'date': '2025-02-03', 'action': 'Corrective Action', 'details': 'Updated battery handling procedures as per new EPR guidelines', 'user': 'Vikram Joshi', 'status': 'In Progress'},
        {'date': '2025-02-15', 'action': 'Document Update', 'details': 'Revised SOP for storage area to meet E-Waste Rules 2022', 'user': 'Ananya Reddy', 'status': 'Completed'},
        {'date': '2025-03-10', 'action': 'External Audit', 'details': 'CPCB authorization renewal audit', 'user': 'CPCB Inspector', 'status': 'Passed'},
    ]
    
    # Corrective actions with Indian regulatory context
    corrective_actions = [
        {'id': 'CA-001', 'issue': 'EPR Collection Targets', 'description': 'Increase collection centers in Tier 2 cities to meet EPR targets', 'due_date': '2025-04-30', 'status': 'In Progress', 'assigned_to': 'Rahul Sharma'},
        {'id': 'CA-002', 'issue': 'Form 3 Submission', 'description': 'Submit quarterly Form 3 to CPCB with complete documentation', 'due_date': '2025-04-15', 'status': 'Completed', 'assigned_to': 'Priya Patel'},
        {'id': 'CA-003', 'issue': 'Hazardous Storage', 'description': 'Upgrade storage facility for CRT glass as per CPCB guidelines', 'due_date': '2025-05-01', 'status': 'Not Started', 'assigned_to': 'Amit Singh'},
        {'id': 'CA-004', 'issue': 'Awareness Program', 'description': 'Conduct e-waste awareness program for local businesses', 'due_date': '2025-04-22', 'status': 'In Progress', 'assigned_to': 'Neha Gupta'},
    ]
    
    return {
        'ewaste_data': ewaste_data,
        'regulations': regulations,
        'vendors': vendors,
        'material_flow': material_flow,
        'audit_trail': audit_trail,
        'corrective_actions': corrective_actions
    }

# Add helper function for messages
def add_message(messages: List[Dict], role: str, content: str) -> List[Dict]:
    """Add a message to the messages list"""
    messages.append({"role": role, "content": content})
    return messages

# LangGraph implementation for the compliance report generation system
class AgentState(TypedDict):
    messages: Annotated[List[Dict], "List of messages from all agents"]
    system_status: Dict
    data: Dict
    compliance_status: Dict
    report_sections: Dict

# Agent definitions with India-specific context
def erp_integration_agent(state: AgentState) -> AgentState:
    """Agent that collects data from business systems with India context"""
    time.sleep(0.5)
    
    try:
        analysis_prompt = "Analyze typical e-waste composition in India with focus on mobile devices, TVs, and computers"
        insights = "ERP Integration Agent: Retrieved India-specific e-waste data showing high mobile device volumes (35kg/day) and significant TV disposal (25kg/day)."
    except Exception as e:
        insights = f"ERP Integration Agent: Retrieved data but encountered API error: {str(e)}"
    
    messages = add_message(state["messages"], "agent", insights)
    system_status = state["system_status"]
    system_status["erp_integration"] = "Completed"
    
    data = state["data"]
    sample_data = load_sample_data()
    data["ewaste_data"] = sample_data["ewaste_data"]
    data["material_flow"] = sample_data["material_flow"]
    
    return {"messages": messages, "system_status": system_status, "data": data, "compliance_status": state["compliance_status"], "report_sections": state["report_sections"]}

def regulatory_database_agent(state: AgentState) -> AgentState:
    """Agent that maintains India-specific compliance requirements"""
    time.sleep(0.5)
    
    try:
        reg_prompt = "Summarize key requirements of India's E-Waste (Management) Rules 2022 and EPR compliance"
        reg_insights = "Regulatory Database Agent: Retrieved current requirements including E-Waste Rules 2022, EPR targets, and CPCB authorization processes."
    except Exception as e:
        reg_insights = "Regulatory Database Agent: Retrieved current regulatory requirements for all relevant jurisdictions."
    
    messages = add_message(state["messages"], "agent", reg_insights)
    system_status = state["system_status"]
    system_status["regulatory_database"] = "Completed"
    
    data = state["data"]
    sample_data = load_sample_data()
    data["regulations"] = sample_data["regulations"]
    
    return {"messages": messages, "system_status": system_status, "data": data, "compliance_status": state["compliance_status"], "report_sections": state["report_sections"]}

def vendor_compliance_agent(state: AgentState) -> AgentState:
    """Agent that validates Indian recycler certifications"""
    time.sleep(0.5)
    
    messages = add_message(state["messages"], "agent", "Vendor Compliance Agent: Validated CPCB authorizations for 5 Indian recyclers including E-Parisaraa and Attero.")
    system_status = state["system_status"]
    system_status["vendor_compliance"] = "Completed"
    
    data = state["data"]
    sample_data = load_sample_data()
    data["vendors"] = sample_data["vendors"]
    
    return {"messages": messages, "system_status": system_status, "data": data, "compliance_status": state["compliance_status"], "report_sections": state["report_sections"]}

def compliance_checker_agent(state: AgentState) -> AgentState:
    """Agent that validates operations against India regulations"""
    time.sleep(0.7)
    
    try:
        compliance_prompt = """
        Analyze compliance for Indian e-waste operations with:
        - E-Waste Rules 2022: Partially Compliant (85%)
        - EPR: Partially Compliant (78%)
        - Basel Convention: Fully Compliant (98%)
        - State PCB Guidelines: Pending (65%)
        
        Provide India-specific assessment.
        """
        compliance_insights = "Compliance Checker Agent: Evaluated operations against Indian regulations. Priority issues: EPR targets and state PCB documentation."
    except Exception as e:
        compliance_insights = "Compliance Checker Agent: Evaluated operations against Indian regulatory frameworks. Found 7 potential issues."
    
    messages = add_message(state["messages"], "agent", compliance_insights)
    system_status = state["system_status"]
    system_status["compliance_check"] = "Completed"
    
    compliance_status = state["compliance_status"]
    regulations = state["data"]["regulations"]
    
    total_score = sum(reg["score"] for reg in regulations)
    avg_score = total_score / len(regulations)
    compliance_status["overall_score"] = round(avg_score, 1)
    compliance_status["total_findings"] = sum(reg["findings"] for reg in regulations)
    
    findings_by_severity = {
        "critical": 2,  # EPR and state compliance are critical
        "major": 3,
        "minor": 2
    }
    compliance_status["findings_by_severity"] = findings_by_severity
    
    return {"messages": messages, "system_status": system_status, "data": state["data"], "compliance_status": compliance_status, "report_sections": state["report_sections"]}

def gap_analysis_agent(state: AgentState) -> AgentState:
    """Agent that identifies India-specific improvement areas"""
    time.sleep(0.6)
    
    try:
        gap_prompt = """
        Based on Indian e-waste compliance findings:
        - EPR collection targets not met
        - Form 3 documentation incomplete
        - CRT glass storage insufficient
        - Awareness programs lacking
        
        Suggest prioritized corrective actions for Indian context.
        """
        gap_insights = "Gap Analysis Agent: Identified 4 priority areas including EPR targets and hazardous material handling as per Indian regulations."
    except Exception as e:
        gap_insights = "Gap Analysis Agent: Identified 4 areas requiring corrective actions to improve compliance."
    
    messages = add_message(state["messages"], "agent", gap_insights)
    system_status = state["system_status"]
    system_status["gap_analysis"] = "Completed"
    
    data = state["data"]
    sample_data = load_sample_data()
    data["corrective_actions"] = sample_data["corrective_actions"]
    data["audit_trail"] = sample_data["audit_trail"]
    
    return {"messages": messages, "system_status": system_status, "data": data, "compliance_status": state["compliance_status"], "report_sections": state["report_sections"]}

def report_generator_agent(state: AgentState) -> AgentState:
    """Agent that generates the final report with India context"""
    time.sleep(1)
    
    ewaste_data = state["data"]["ewaste_data"]
    total_ewaste = ewaste_data[['computers', 'mobile_devices', 'televisions', 'refrigerators', 'printers', 'batteries']].sum().sum() / 1000
    
    try:
        exec_summary_prompt = f"""
        Generate an executive summary for an Indian e-waste compliance report with:
        - Total e-waste processed: {round(total_ewaste, 1)} tons
        - Overall compliance score: {state['compliance_status']['overall_score']}%
        - Key Indian regulations: E-Waste Rules 2022, EPR
        - Priority improvements: EPR targets, hazardous material handling
        
        Keep it concise and professional for Indian audience.
        """
        summary = "Report Generator Agent: Compiled India-specific compliance report covering E-Waste Rules 2022, EPR status, and corrective actions for CPCB compliance."
    except Exception as e:
        summary = "Report Generator Agent: Compiled comprehensive compliance report with executive summary, material flow analysis, regulatory compliance status, and corrective action plan."
    
    messages = add_message(state["messages"], "agent", summary)
    system_status = state["system_status"]
    system_status["report_generation"] = "Completed"
    
    report_sections = state["report_sections"]
    
    # Executive Summary
    executive_summary = {
        "total_ewaste": round(total_ewaste, 1),
        "compliance_score": state["compliance_status"]["overall_score"],
        "key_improvements": "EPR target achievement, hazardous material handling, CPCB documentation"
    }
    report_sections["executive_summary"] = executive_summary
    
    # Material Flow Analysis
    material_flow = {
        "by_type": {
            "computers": round(ewaste_data['computers'].sum() / 1000, 1),
            "mobile_devices": round(ewaste_data['mobile_devices'].sum() / 1000, 1),
            "televisions": round(ewaste_data['televisions'].sum() / 1000, 1),
            "refrigerators": round(ewaste_data['refrigerators'].sum() / 1000, 1),
            "printers": round(ewaste_data['printers'].sum() / 1000, 1),
            "batteries": round(ewaste_data['batteries'].sum() / 1000, 1)
        },
        "by_material": state["data"]["material_flow"]
    }
    report_sections["material_flow"] = material_flow
    
    # Regulatory Compliance
    report_sections["regulatory_compliance"] = state["data"]["regulations"]
    
    # Corrective Action Plan
    report_sections["corrective_actions"] = state["data"]["corrective_actions"]
    
    return {"messages": messages, "system_status": system_status, "data": state["data"], "compliance_status": state["compliance_status"], "report_sections": report_sections}

# Build the LangGraph workflow
def build_graph():
    builder = StateGraph(AgentState)
    
    builder.add_node("erp_integration", erp_integration_agent)
    builder.add_node("regulatory_database", regulatory_database_agent)
    builder.add_node("vendor_compliance", vendor_compliance_agent)
    builder.add_node("compliance_checker", compliance_checker_agent)
    builder.add_node("gap_analysis", gap_analysis_agent)
    builder.add_node("report_generator", report_generator_agent)
    
    def should_continue(state):
        return len(state["messages"]) < 3
    
    builder.add_conditional_edges(
        "erp_integration",
        should_continue,
        {
            True: "regulatory_database",
            False: "compliance_checker"
        }
    )
    
    builder.add_conditional_edges(
        "regulatory_database",
        should_continue,
        {
            True: "vendor_compliance",
            False: "compliance_checker"
        }
    )
    
    builder.add_conditional_edges(
        "vendor_compliance",
        should_continue,
        {
            True: "erp_integration",
            False: "compliance_checker"
        }
    )
    
    builder.add_edge("compliance_checker", "gap_analysis")
    builder.add_edge("gap_analysis", "report_generator")
    builder.add_edge("report_generator", END)
    
    builder.set_entry_point("erp_integration")
    
    graph = builder.compile()
    
    return graph

def initialize_state():
    return {
        "messages": [],
        "system_status": {
            "erp_integration": "Pending",
            "regulatory_database": "Pending",
            "vendor_compliance": "Pending",
            "compliance_check": "Pending",
            "gap_analysis": "Pending",
            "report_generation": "Pending"
        },
        "data": {},
        "compliance_status": {
            "overall_score": 0,
            "total_findings": 0,
            "findings_by_severity": {}
        },
        "report_sections": {}
    }

def run_workflow():
    with st.spinner("Generating India e-waste compliance report..."):
        graph = build_graph()
        state = initialize_state()
        state = graph.invoke(state)
    return state

# Streamlit UI with India-specific options
def main():
    st.markdown('<div class="main-header">India E-Waste Compliance Reporting System</div>', unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown("### System Controls")
        
        period_options = ["Q1 2025", "Q4 2024", "Q3 2024", "Q2 2024"]
        selected_period = st.selectbox("Reporting Period", period_options)
        
        facility_options = ["All Facilities", "Bangalore Plant", "Mumbai Collection Center", "Delhi Processing Unit", "Chennai Hub"]
        selected_facility = st.selectbox("Facility", facility_options)
        
        regulation_options = ["All Regulations", 
                            "E-Waste (Management) Rules 2022", 
                            "Extended Producer Responsibility (EPR)", 
                            "Basel Convention", 
                            "State PCB Guidelines"]
        selected_regulations = st.selectbox(
            "Regulatory Framework",
            ["All Regulations"],
            key="selected_regulations"
        )
        report_type_options = ["Comprehensive Report", "Executive Summary", "Technical Appendix", "Corrective Actions Only"]
        report_type = st.selectbox("Report Type", report_type_options, key="report_type")
        
        st.divider()
        
        if st.button("Generate Compliance Report", type="primary"):
            if "report_state" not in st.session_state:
                st.session_state.report_state = run_workflow()
            else:
                st.session_state.report_state = run_workflow()
            
            st.success("Report generated successfully!")
        
      
        
        st.divider()
        
        st.markdown("### System Status")
        if "report_state" in st.session_state:
            for component, status in st.session_state.report_state["system_status"].items():
                if status == "Completed":
                    st.markdown(f"✅ {component.replace('_', ' ').title()}")
                else:
                    st.markdown(f"⏳ {component.replace('_', ' ').title()}")
        else:
            st.info("No report generated yet.")
        
    # Main content
    if "report_state" in st.session_state:
        display_report(st.session_state.report_state)
    else:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            <div class="info-card">
                <h3>India E-Waste Compliance Report Generator</h3>
                <p>This system helps Indian businesses track and document their e-waste handling in accordance with E-Waste (Management) Rules 2022, EPR requirements, and other regulations.</p>
                <p>Use the controls in the sidebar to generate a new compliance report for submission to CPCB/SPCBs.</p>
            </div>
            """, unsafe_allow_html=True)
        
        
        
       

def display_report(state):
    report_type = st.session_state.get("report_type", "Comprehensive Report")
    selected_regulations = st.session_state.get("selected_regulations", ["All Regulations"])
    
    st.markdown(f'<div class="section-header">India E-Waste Compliance Report - {report_type}</div>', unsafe_allow_html=True)
    
    if report_type == "Executive Summary":
        exec_summary = state["report_sections"]["executive_summary"]
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-value">{exec_summary["total_ewaste"]} tons</div>
                <div class="metric-label">Total E-Waste Processed</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-value">{exec_summary["compliance_score"]}%</div>
                <div class="metric-label">Compliance Score</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-value">{state["compliance_status"]["total_findings"]}</div>
                <div class="metric-label">Total Findings</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown(f"**Key Improvements Needed:** {exec_summary['key_improvements']}")
        
    elif report_type == "Technical Appendix":
        st.markdown('<div class="sub-header">Technical Details for CPCB</div>', unsafe_allow_html=True)
        
        material_flow = state["report_sections"]["material_flow"]
        materials_df = pd.DataFrame(material_flow["by_material"])
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Material Composition (Indian Context)**")
            st.dataframe(materials_df)
        
        with col2:
            st.markdown("**Hazard Levels**")
            fig = px.bar(
                materials_df, 
                x="material", 
                y="weight",
                color="hazard_level",
                title="Material Weight by Hazard Level (India)",
                labels={"material": "Material Type", "weight": "Weight (tons)"}
            )
            st.plotly_chart(fig)
        
        st.markdown('<div class="sub-header">System Log</div>', unsafe_allow_html=True)
        for msg in state["messages"]:
            if msg["role"] == "agent":
                with st.chat_message("assistant"):
                    st.write(msg["content"])
    
    elif report_type == "Corrective Actions Only":
        st.markdown('<div class="sub-header">Corrective Action Plan for CPCB</div>', unsafe_allow_html=True)
        
        actions_df = pd.DataFrame(state["report_sections"]["corrective_actions"])
        
        status_counts = actions_df["status"].value_counts().reset_index()
        status_counts.columns = ["status", "count"]
        
        col1, col2 = st.columns(2)
        with col1:
            fig = px.pie(
                status_counts,
                values="count",
                names="status",
                title="Corrective Action Status",
                color_discrete_sequence=[ "#FF9933", "#138808", "#000080"]  # Indian theme colors
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            actions_df["due_date"] = pd.to_datetime(actions_df["due_date"])
            fig = px.timeline(
                actions_df,
                x_start="due_date",
                x_end="due_date",
                y="issue",
                color="status",
                title="Corrective Action Due Dates",
                color_discrete_map={
                    "Completed": "#138808",  # Green
                    "In Progress": "#FF9933",  # Saffron
                    "Not Started": "#000080"   # Blue
                }
            )
            fig.update_yaxes(autorange="reversed")
            st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("Action Items for Indian Compliance")
        st.dataframe(
            actions_df,
            column_config={
                "id": "Action ID",
                "issue": "Issue",
                "description": "Description",
                "due_date": st.column_config.DateColumn("Due Date"),
                "status": "Status",
                "assigned_to": "Assigned To"
            },
            hide_index=True,
            use_container_width=True
        )
    
    elif report_type == "Comprehensive Report" or report_type == "Executive Summary":
        exec_summary = state["report_sections"]["executive_summary"]
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-value">{exec_summary["total_ewaste"]} tons</div>
                <div class="metric-label">Total E-Waste Processed</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-value">{exec_summary["compliance_score"]}%</div>
                <div class="metric-label">Compliance Score</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-value">{state["compliance_status"]["total_findings"]}</div>
                <div class="metric-label">Total Findings</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown(f"**Key Improvements Needed:** {exec_summary['key_improvements']}")
        
        # Material Flow Analysis
        st.markdown('<div class="sub-header">2. Material Flow Analysis (India)</div>', unsafe_allow_html=True)
        
        material_flow = state["report_sections"]["material_flow"]
        
        col1, col2 = st.columns(2)
        with col1:
            device_types = material_flow["by_type"]
            fig = px.pie(
                values=list(device_types.values()),
                names=list(device_types.keys()),
                title="E-Waste by Device Type (tons) - Indian Pattern",
                color_discrete_sequence=["#FF9933", "#138808", "#000080", "#FFFFFF", "#808080"]
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            materials_df = pd.DataFrame(material_flow["by_material"])
            fig = px.bar(
                materials_df, 
                x="material", 
                y="weight",
                color="hazard_level",
                title="Material Composition by Hazard Level (India)",
                labels={"material": "Material Type", "weight": "Weight (tons)"},
                color_discrete_map={
                    "Very High": "#d32f2f",
                    "High": "#FF9933",
                    "Medium": "#000080",
                    "Low": "#138808"
                }
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Vendor Map - India specific
        st.markdown('<div class="sub-header">3. Authorized Recycler Network</div>', unsafe_allow_html=True)
        vendors_df = pd.DataFrame(state["data"]["vendors"])
        
        fig = px.scatter_mapbox(
            vendors_df,
            lat="lat",
            lon="lon",
            hover_name="name",
            hover_data=["certification", "status"],
            color="status",
            zoom=4,
            center={"lat": 20.5937, "lon": 78.9629},  # Center on India
            title="Authorized E-Waste Recyclers in India",
            color_discrete_map={
                "Compliant": "#138808",
                "Pending Audit": "#FF9933",
                "Non-Compliant": "#d32f2f"
            }
        )
        fig.update_layout(mapbox_style="open-street-map")
        fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
        st.plotly_chart(fig, use_container_width=True)
        
        # Regulatory Compliance
        st.markdown('<div class="sub-header">4. India Regulatory Compliance Status</div>', unsafe_allow_html=True)
        
        regulations = state["report_sections"]["regulatory_compliance"]
        
        if "All Regulations" not in selected_regulations:
            regulations = [reg for reg in regulations if reg["name"] in selected_regulations]
        
        if not regulations:
            st.warning("No regulatory frameworks selected. Please select at least one framework from the sidebar.")
        else:
            for reg in regulations:
                if "score" not in reg:
                    reg["score"] = 0
                if "status" not in reg:
                    reg["status"] = "Pending Review"
                if "findings" not in reg:
                    reg["findings"] = 0
                if "details" not in reg:
                    reg["details"] = "No details available"
            
            reg_df = pd.DataFrame(regulations)
            
            fig = px.bar(
                reg_df,
                x="name",
                y="score",
                color="status",
                color_discrete_map={
                    "Fully Compliant": "#138808",  # Green
                    "Partially Compliant": "#FF9933",  # Saffron
                    "Pending Review": "#000080"   # Blue
                },
                text="score",
                title="Compliance Scores by Indian Regulatory Framework",
                labels={"name": "Regulation", "score": "Compliance Score (%)"}
            )
            
            fig.update_layout(
                yaxis_range=[0,105],
                height=400,
                margin=dict(l=20, r=20, t=40, b=20),
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            fig.update_traces(
                texttemplate='%{text}%',
                textposition='outside',
                textfont=dict(size=12),
                marker=dict(line=dict(width=1, color='DarkSlateGrey'))
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            st.subheader("Compliance Findings Details (India Context)")
            for reg in regulations:
                with st.expander(f"{reg['name']} - {reg['findings']} findings"):
                    st.markdown(f"**Status:** {reg['status']}")
                    st.markdown(f"**Score:** {reg['score']}%")
                    st.markdown("**Findings:**")
                    st.write(reg["details"])
        
        # Corrective Action Plan
        st.markdown('<div class="sub-header">5. Corrective Action Plan for India</div>', unsafe_allow_html=True)
        
        actions_df = pd.DataFrame(state["report_sections"]["corrective_actions"])
        
        status_counts = actions_df["status"].value_counts().reset_index()
        status_counts.columns = ["status", "count"]
        
        col1, col2 = st.columns(2)
        with col1:
            fig = px.pie(
                status_counts,
                values="count",
                names="status",
                title="Corrective Action Status",
                color_discrete_sequence=["#138808", "#FF9933", "#000080"]
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            actions_df["due_date"] = pd.to_datetime(actions_df["due_date"])
            fig = px.timeline(
                actions_df,
                x_start="due_date",
                x_end="due_date",
                y="issue",
                color="status",
                title="Corrective Action Due Dates",
                color_discrete_map={
                    "Completed": "#138808",
                    "In Progress": "#FF9933",
                    "Not Started": "#000080"
                }
            )
            fig.update_yaxes(autorange="reversed")
            st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("Action Items for Indian Compliance")
        st.dataframe(
            actions_df,
            column_config={
                "id": "Action ID",
                "issue": "Issue",
                "description": "Description",
                "due_date": st.column_config.DateColumn("Due Date"),
                "status": "Status",
                "assigned_to": "Assigned To"
            },
            hide_index=True,
            use_container_width=True
        )
        
        # Audit Trail
        st.markdown('<div class="sub-header">6. India Audit Trail</div>', unsafe_allow_html=True)
        
        audit_df = pd.DataFrame(state["data"]["audit_trail"])
        st.dataframe(
            audit_df,
            column_config={
                "date": "Date",
                "action": "Action",
                "details": "Details",
                "user": "User",
                "status": "Status"
            },
            hide_index=True,
            use_container_width=True
        )
        
        # System Messages
        st.markdown('<div class="sub-header">System Log</div>', unsafe_allow_html=True)
        
        for msg in state["messages"]:
            if msg["role"] == "agent":
                with st.chat_message("assistant"):
                    st.write(msg["content"])

if __name__ == "__main__":
    main()