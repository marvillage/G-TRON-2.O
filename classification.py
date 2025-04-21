import streamlit as st
from gradio_client import Client, handle_file
import tempfile
import os
import google.generativeai as genai
import re
import matplotlib.pyplot as plt
import numpy as np

# --- CONFIG ---
GEMINI_API_KEY = "AIzaSyBU-gTwq3RqqGGDrY0s8BHS-bM9Sa8O7LY"
genai.configure(api_key=GEMINI_API_KEY)

# --- CUSTOM CSS ---
st.set_page_config(
    page_title="E-Waste Material Analyzer",
    layout="centered",
)

# Custom CSS for modern blue/black theme
st.markdown("""
<style>
    /* Main background and text colors */
    .stApp {
        background-color: #0E1117;
        color: #E0E0E0;
    }
    
    /* Headers styling */
    h1, h2, h3, h4, h5, h6 {
        color: #3498db;
        font-weight: 600;
    }
    
    h1 {
        text-align: center;
        padding-bottom: 20px;
        border-bottom: 2px solid #3498db;
        margin-bottom: 30px;
    }
    
    /* Caption styling */
    .css-v37k9u p {
        color: #7FDBFF;
        text-align: center;
        font-style: italic;
        margin-bottom: 30px;
    }
    
    /* Button styling */
    .stButton > button {
        background-color: #3498db;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 10px 20px;
        font-weight: 600;
        width: 100%;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        background-color: #2980b9;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        transform: translateY(-2px);
    }
    
    /* File uploader styling */
    .css-1offfwp {
        border: 2px dashed #3498db;
        border-radius: 8px;
        padding: 30px 20px;
        background-color: rgba(52, 152, 219, 0.1);
        transition: all 0.3s;
    }
    
    .css-1offfwp:hover {
        border-color: #2980b9;
        background-color: rgba(52, 152, 219, 0.15);
    }
    
    /* Spinner styling */
    .stSpinner > div {
        border-top-color: #3498db !important;
    }
    
    /* Subheader styling */
    .css-10trblm {
        margin-top: 30px;
        padding-top: 20px;
        border-top: 1px solid #2c3e50;
    }
    
    /* Results container styling */
    .element-container {
        background-color: #1a1e26;
        border-radius: 8px;
        padding: 10px;
        margin: 10px 0;
        border-left: 3px solid #3498db;
    }
    
    /* Image container */
    .css-1v0mbdj img {
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 10px;
        background: #0E1117;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #3498db;
        border-radius: 10px;
    }
    
    .stMetric {
        background-color: #1a1e26;
        border-radius: 10px;
        padding: 15px !important;
        border-left: 4px solid #3498db;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 10px 0;
        min-height: 120px; /* Ensure consistent height */
        width: 100%;
        overflow: visible;
    }
    
    /* Make sure label text doesn't get cut off */
    .stMetric label {
        color: #3498db !important;
        font-weight: 600;
        font-size: 16px !important;
        white-space: normal !important;
        overflow: visible !important;
        text-overflow: clip !important;
        max-width: 100% !important;
        display: block !important;
        line-height: 1.2 !important;
        margin-bottom: 10px !important;
    }
    
    /* Make sure value text doesn't get cut off */
    .stMetric [data-testid="stMetricValue"] {
        color: white !important;
        font-size: 24px !important;
        white-space: normal !important;
        overflow: visible !important;
        text-overflow: clip !important;
        width: 100% !important;
        display: block !important;
    }
    
    /* Add some spacing between metrics */
    [data-testid="column"] > div > div > div > div {
        padding: 0 5px !important;
    }
    
    /* Ensure column widths are reasonable */
    [data-testid="column"] {
        min-width: 120px !important;
    }
    
    /* Fix for material visualization header */
    [data-testid="stHeader"] {
        overflow: visible !important;
    }
    
    /* Improve spacing in metrics visualization section */
    [data-testid="stVerticalBlock"] > div:has([data-testid="stMetricValue"]) {
        margin-bottom: 20px !important;
    }
    
</style>
""", unsafe_allow_html=True)

# --- APP CONTENT ---
st.title("E-Waste Material Analyzer")
st.caption("Upload an image to get a breakdown of components and estimate of material types.")

# Create columns for better layout
col1, col2, col3 = st.columns([1, 10, 1])

with col2:
    uploaded_file = st.file_uploader("Upload an image of e-waste", type=["jpg", "jpeg", "png"])

if uploaded_file:
    st.image(uploaded_file, caption="Uploaded E-Waste", use_container_width=True)
    
    if st.button("Analyze Components & Materials"):
        with st.spinner("Processing image..."):
            # Save uploaded file to temp path
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                tmp.write(uploaded_file.read())
                temp_path = tmp.name
            
            try:
                # Step 1: Use Hugging Face model to detect components
                client = Client("maxiw/Qwen2-VL-Detection")
                hf_result = client.predict(
                    image=handle_file(temp_path),
                    text_input="List all visible components like plastic casings, wires, metal parts, batteries etc.",
                    system_prompt="You are an expert in e-waste detection. Just describe what components and materials are visible.",
                    model_id="Qwen/Qwen2-VL-7B-Instruct",
                    api_name="/run_example"
                )
                
                # Fix for handling different response formats
                if isinstance(hf_result, list) and len(hf_result) > 0:
                    raw_result = hf_result[0]
                    if isinstance(raw_result, str) and raw_result.startswith("['") and raw_result.endswith("']"):
                        description = raw_result.strip("['']").replace("\\n", "\n")
                    else:
                        description = raw_result
                else:
                    description = hf_result
                
                # Step 2: Use Gemini to analyze material breakdown
                model = genai.GenerativeModel('gemini-1.5-flash')
                prompt = f"""
                From the following description of an e-waste pile, estimate the material composition by percentage.

                Return it in a clean markdown list like:
                - Plastic: 40%
                - Metal: 30%
                - PCB: 15%
                - Batteries: 10%
                - Others: 5%

                Description: {description}
                """
                gemini_response = model.generate_content(prompt)
                
                # Parse the response to extract percentages for metrics
                response_text = gemini_response.text
                
                st.subheader("Material Breakdown:")
                st.markdown(response_text)
                
                # Display metrics in a more visual way
                try:
                    # Extract material names and percentages using regex
                    materials = re.findall(r'- (.*?): (\d+)%', response_text)
                    
                    if materials:
                        st.subheader("Material Visualization:")
                        
                        # Use fewer columns if there are many materials
                        num_cols = min(len(materials), 6)
                        cols = st.columns(num_cols)
                        
                        for i, (material, percentage) in enumerate(materials):
                            col_index = i % num_cols
                            with cols[col_index]:
                                st.metric(label=material, value=f"{percentage}%")
                        
                        # Create a simple bar chart
                        plt.style.use('dark_background')
                        
                        materials_names = [m[0] for m in materials]
                        percentages = [int(m[1]) for m in materials]
                        
                        fig, ax = plt.subplots(figsize=(10, 6))
                        bars = ax.bar(materials_names, percentages, color=['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6'])
                        
                        # Add percentage labels on top of each bar
                        for bar in bars:
                            height = bar.get_height()
                            ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                                    f'{height}%', ha='center', va='bottom', color='white', fontweight='bold')
                        
                        ax.set_ylim(0, max(percentages) + 10)
                        ax.set_ylabel('Percentage (%)')
                        ax.set_title('E-Waste Material Composition')
                        ax.grid(axis='y', linestyle='--', alpha=0.7)
                        
                        fig.tight_layout()
                        st.pyplot(fig)
                
                except Exception as e:
                    st.info(f"Could not generate visualization from the response format: {str(e)}")
                    
            except Exception as e:
                st.error(f"Error: {str(e)}")
            finally:
                os.remove(temp_path)
else:
    # Display example/instructions when no file is uploaded
    st.markdown("""
    <div style="text-align: center; padding: 30px; background-color: rgba(52, 152, 219, 0.1); border-radius: 10px; margin: 20px 0;">
        <img src="https://img.icons8.com/clouds/150/000000/recycling.png" style="width: 100px; margin-bottom: 20px;">
        <h3 style="color: #3498db;">How it works</h3>
        <p>1. Upload a photo of electronic waste</p>
        <p>2. Click "Analyze" to process the image</p>
        <p>3. Get detailed component identification and material breakdown</p>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align: center; margin-top: 50px; padding-top: 20px; border-top: 1px solid #2c3e50;">
    <p style="color: #7f8c8d; font-size: 12px;">E-Waste Material Analyzer - Helping Recycle Efficiently</p>
</div>
""", unsafe_allow_html=True) 
# import streamlit as st
# import tempfile
# import os
# import google.generativeai as genai
# import re
# import matplotlib.pyplot as plt
# import numpy as np
# from PIL import Image
# import requests
# from io import BytesIO
# import base64
# import torch



# # --- CUSTOM CSS ---
# st.set_page_config(
#     page_title="E-Waste Material Analyzer",
#     layout="centered",
# )

# # Custom CSS for modern blue/black theme
# st.markdown("""
# <style>
#     /* Main background and text colors */
#     .stApp {
#         background-color: #0E1117;
#         color: #E0E0E0;
#     }
    
#     /* Headers styling */
#     h1, h2, h3, h4, h5, h6 {
#         color: #3498db;
#         font-weight: 600;
#     }
    
#     h1 {
#         text-align: center;
#         padding-bottom: 20px;
#         border-bottom: 2px solid #3498db;
#         margin-bottom: 30px;
#     }
    
#     /* Caption styling */
#     .css-v37k9u p {
#         color: #7FDBFF;
#         text-align: center;
#         font-style: italic;
#         margin-bottom: 30px;
#     }
    
#     /* Button styling */
#     .stButton > button {
#         background-color: #3498db;
#         color: white;
#         border: none;
#         border-radius: 5px;
#         padding: 10px 20px;
#         font-weight: 600;
#         width: 100%;
#         transition: all 0.3s;
#     }
    
#     .stButton > button:hover {
#         background-color: #2980b9;
#         box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
#         transform: translateY(-2px);
#     }
    
#     /* File uploader styling */
#     .css-1offfwp {
#         border: 2px dashed #3498db;
#         border-radius: 8px;
#         padding: 30px 20px;
#         background-color: rgba(52, 152, 219, 0.1);
#         transition: all 0.3s;
#     }
    
#     .css-1offfwp:hover {
#         border-color: #2980b9;
#         background-color: rgba(52, 152, 219, 0.15);
#     }
    
#     /* Spinner styling */
#     .stSpinner > div {
#         border-top-color: #3498db !important;
#     }
    
#     /* Subheader styling */
#     .css-10trblm {
#         margin-top: 30px;
#         padding-top: 20px;
#         border-top: 1px solid #2c3e50;
#     }
    
#     /* Results container styling */
#     .element-container {
#         background-color: #1a1e26;
#         border-radius: 8px;
#         padding: 10px;
#         margin: 10px 0;
#         border-left: 3px solid #3498db;
#     }
    
#     /* Image container */
#     .css-1v0mbdj img {
#         border-radius: 10px;
#         box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
#     }
    
#     /* Scrollbar styling */
#     ::-webkit-scrollbar {
#         width: 10px;
#         background: #0E1117;
#     }
    
#     ::-webkit-scrollbar-thumb {
#         background: #3498db;
#         border-radius: 10px;
#     }
    
#     .stMetric {
#         background-color: #1a1e26;
#         border-radius: 10px;
#         padding: 15px !important;
#         border-left: 4px solid #3498db;
#         box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
#         margin: 10px 0;
#         min-height: 120px;
#         width: 100%;
#         overflow: visible;
#     }
    
#     .stMetric label {
#         color: #3498db !important;
#         font-weight: 600;
#         font-size: 16px !important;
#     }
    
#     .stMetric [data-testid="stMetricValue"] {
#         color: white !important;
#         font-size: 24px !important;
#     }
# </style>
# """, unsafe_allow_html=True)

# # --- APP CONTENT ---
# st.title("E-Waste Material Analyzer")
# st.caption("Upload an image to get a breakdown of components and estimate of material types.")

# # Create columns for better layout
# col1, col2, col3 = st.columns([1, 10, 1])

# with col2:
#     uploaded_file = st.file_uploader("Upload an image of e-waste", type=["jpg", "jpeg", "png"])

# def analyze_image_with_gemini(image_path):
#     """Analyze image using Gemini's vision capabilities"""
#     model = genai.GenerativeModel('gemini-pro-vision')
    
#     # Read image as bytes
#     with open(image_path, "rb") as img_file:
#         img_bytes = img_file.read()
    
#     img = Image.open(image_path)
    
#     # First prompt to identify components
#     component_prompt = """
#     Analyze this image of electronic waste and list all visible components like:
#     - Plastic casings
#     - Metal parts
#     - Wires/cables
#     - Circuit boards
#     - Batteries
#     - Screws/fasteners
#     - Other identifiable components
    
#     Return a bulleted list of components found.
#     """
    
#     # Second prompt to estimate materials
#     material_prompt = """
#     Based on the identified components, estimate the material composition by percentage.
#     Focus on these main categories: Plastic, Metal, Circuit Boards, Batteries, Wires, Other.

#     Return it in a clean markdown list like:
#     - Plastic: 40%
#     - Metal: 30%
#     - Circuit Boards: 15%
#     - Batteries: 10%
#     - Wires: 3%
#     - Other: 2%
#     """
    
#     # Get component list
#     component_response = model.generate_content([component_prompt, img])
#     components = component_response.text
    
#     # Get material breakdown
#     material_response = model.generate_content([f"Components: {components}\n\n{material_prompt}", img])
#     materials = material_response.text
    
#     return components, materials

# if uploaded_file:
#     st.image(uploaded_file, caption="Uploaded E-Waste", use_container_width=True)
    
#     if st.button("Analyze Components & Materials"):
#         with st.spinner("Processing image..."):
#             # Save uploaded file to temp path
#             with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
#                 tmp.write(uploaded_file.read())
#                 temp_path = tmp.name
            
#             try:
#                 # Use Gemini for both component identification and material analysis
#                 components, materials = analyze_image_with_gemini(temp_path)
                
#                 st.subheader("Identified Components:")
#                 st.markdown(components)
                
#                 st.subheader("Material Breakdown:")
#                 st.markdown(materials)
                
#                 # Display metrics in a more visual way
#                 try:
#                     # Extract material names and percentages using regex
#                     material_matches = re.findall(r'- (.*?): (\d+)%', materials)
                    
#                     if material_matches:
#                         st.subheader("Material Visualization:")
                        
#                         # Use fewer columns if there are many materials
#                         num_cols = min(len(material_matches), 6)
#                         cols = st.columns(num_cols)
                        
#                         for i, (material, percentage) in enumerate(material_matches):
#                             col_index = i % num_cols
#                             with cols[col_index]:
#                                 st.metric(label=material, value=f"{percentage}%")
                        
#                         # Create a simple bar chart
#                         plt.style.use('dark_background')
                        
#                         materials_names = [m[0] for m in material_matches]
#                         percentages = [int(m[1]) for m in material_matches]
                        
#                         fig, ax = plt.subplots(figsize=(10, 6))
#                         bars = ax.bar(materials_names, percentages, color=['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6'])
                        
#                         # Add percentage labels on top of each bar
#                         for bar in bars:
#                             height = bar.get_height()
#                             ax.text(bar.get_x() + bar.get_width()/2., height + 1,
#                                     f'{height}%', ha='center', va='bottom', color='white', fontweight='bold')
                        
#                         ax.set_ylim(0, max(percentages) + 10)
#                         ax.set_ylabel('Percentage (%)')
#                         ax.set_title('E-Waste Material Composition')
#                         ax.grid(axis='y', linestyle='--', alpha=0.7)
                        
#                         fig.tight_layout()
#                         st.pyplot(fig)
                
#                 except Exception as e:
#                     st.info(f"Could not generate visualization from the response format: {str(e)}")
                    
#             except Exception as e:
#                 st.error(f"Error analyzing image: {str(e)}")
#             finally:
#                 try:
#                     os.remove(temp_path)
#                 except:
#                     pass
# else:
#     # Display example/instructions when no file is uploaded
#     st.markdown("""
#     <div style="text-align: center; padding: 30px; background-color: rgba(52, 152, 219, 0.1); border-radius: 10px; margin: 20px 0;">
#         <img src="https://img.icons8.com/clouds/150/000000/recycling.png" style="width: 100px; margin-bottom: 20px;">
#         <h3 style="color: #3498db;">How it works</h3>
#         <p>1. Upload a photo of electronic waste</p>
#         <p>2. Click "Analyze" to process the image</p>
#         <p>3. Get detailed component identification and material breakdown</p>
#     </div>
#     """, unsafe_allow_html=True)

# # Footer
# st.markdown("""
# <div style="text-align: center; margin-top: 50px; padding-top: 20px; border-top: 1px solid #2c3e50;">
#     <p style="color: #7f8c8d; font-size: 12px;">E-Waste Material Analyzer - Helping Recycle Efficiently</p>
# </div>
# """, unsafe_allow_html=True)
