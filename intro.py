import streamlit as st
import os

# Set page configuration
st.set_page_config(
    page_title="E-Waste Management System",
    page_icon="♻️",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        background-color: #f5f5f5;
    }
    .title {
        color: #2E7D32;
        text-align: center;
        font-size: 2.5em;
        margin-bottom: 0.5em;
    }
    .subtitle {
        color: #1B5E20;
        text-align: center;
        font-size: 1.5em;
        margin-bottom: 1em;
    }
    .feature-card {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        margin: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .metric-card {
        background-color: #E8F5E9;
        border-radius: 10px;
        padding: 15px;
        margin: 10px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

try:
    # Header
    st.markdown('<h1 class="title">♻️ AI-Powered E-Waste Management System</h1>', unsafe_allow_html=True)
    st.markdown('<h2 class="subtitle">Smart Solutions for Sustainable E-Waste Management</h2>', unsafe_allow_html=True)

    # Introduction
    st.markdown("""
    <div class="feature-card">
        <h3>Welcome to the Future of E-Waste Management</h3>
        <p>Our AI-powered platform revolutionizes how we handle electronic waste, combining cutting-edge machine learning with environmental sustainability. 
        By leveraging advanced analytics and predictive modeling, we help organizations and individuals make informed decisions about e-waste management, 
        maximizing resource recovery while minimizing environmental impact.</p>
    </div>
    """, unsafe_allow_html=True)

    # Key Features
    st.markdown("## 🚀 Key Features")

    # Create columns for features
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="feature-card">
            <h4>📊 AI-Powered Analytics</h4>
            <p>Advanced machine learning models predict waste generation patterns and optimize collection routes</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="feature-card">
            <h4>🌍 Environmental Impact</h4>
            <p>Track and reduce carbon footprint through intelligent waste management strategies</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="feature-card">
            <h4>💰 Economic Benefits</h4>
            <p>Maximize resource recovery and optimize operational costs through data-driven insights</p>
        </div>
        """, unsafe_allow_html=True)

    # System Capabilities
    st.markdown("## 💡 System Capabilities")

    # Create columns for capabilities
    cap1, cap2 = st.columns(2)

    with cap1:
        st.markdown("""
        <div class="feature-card">
            <h4>🔍 Smart Waste Analysis</h4>
            <ul>
                <li>Predictive modeling for waste generation</li>
                <li>Automated waste classification</li>
                <li>Real-time monitoring and alerts</li>
                <li>Resource recovery optimization</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with cap2:
        st.markdown("""
        <div class="feature-card">
            <h4>📱 User-Friendly Interface</h4>
            <ul>
                <li>Interactive dashboards</li>
                <li>Real-time data visualization</li>
                <li>Customizable reports</li>
                <li>Mobile-responsive design</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # Benefits Section
    st.markdown("## 🌟 Key Benefits")

    # Create columns for benefits
    ben1, ben2, ben3 = st.columns(3)

    with ben1:
        st.markdown("""
        <div class="metric-card">
            <h4>Environmental Impact</h4>
            <p>Reduce landfill waste by up to 80%</p>
        </div>
        """, unsafe_allow_html=True)

    with ben2:
        st.markdown("""
        <div class="metric-card">
            <h4>Cost Savings</h4>
            <p>Optimize operations and reduce costs by 30%</p>
        </div>
        """, unsafe_allow_html=True)

    with ben3:
        st.markdown("""
        <div class="metric-card">
            <h4>Resource Recovery</h4>
            <p>Increase material recovery rates by 50%</p>
        </div>
        """, unsafe_allow_html=True)

    # Call to Action
    st.markdown("""
    <div class="feature-card" style="text-align: center;">
        <h3>Ready to Transform Your E-Waste Management?</h3>
        <p>Join us in creating a sustainable future through intelligent waste management solutions.</p>
        <p>Get started today and make a difference!</p>
    </div>
    """, unsafe_allow_html=True)

    # Navigation buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 Get Started", use_container_width=True):
            st.switch_page("pages/1_🏠_Home.py")
    with col2:
        if st.button("📚 Learn More", use_container_width=True):
            st.switch_page("pages/2_📚_Documentation.py")

    # Footer
    st.markdown("""
    <div style="text-align: center; margin-top: 2em;">
        <p>© 2024 E-Waste Management System | Powered by AI</p>
        <p>Contact us: support@ewastemanagement.com</p>
    </div>
    """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    st.info("Please try refreshing the page or contact support if the issue persists.") 