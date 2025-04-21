import streamlit as st
import requests
import os
import tempfile
from PIL import Image
import io
import re
from gradio_client import Client, handle_file

# Set page configuration with expanded layout to prevent scrollbars
st.set_page_config(
    page_title="Electronic Device Detector",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Clean, elegant CSS without unnecessary elements
st.markdown("""
<style>
    /* Fix main layout issues */
    .main {
        background: #0c1221;
        color: #f0f5ff;
        font-family: 'Inter', 'Segoe UI', sans-serif;
        padding: 0;
        max-width: 100%;
        overflow-x: hidden;
    }
    
    /* Remove Streamlit branding and extra padding */
    #MainMenu, footer, header {
        visibility: hidden;
    }
    
    .stApp {
        margin: 0 auto;
    }
    
    /* Remove scrollbar */
    ::-webkit-scrollbar {
        display: none;
    }
    
    .main .block-container {
        max-width: 1000px;
        padding-top: 2rem;
        padding-bottom: 2rem;
        margin: 0 auto;
    }
    
    /* Main container with clean borders */
    .app-container {
        background: #0a1019;
        border-radius: 16px;
        padding: 3rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        border: 1px solid #1d2b44;
        margin: 0 auto;
        max-width: 900px;
    }
    
    /* Typography */
    h1 {
        color: #fff;
        text-align: center;
        font-weight: 700;
        font-size: 2.4rem;
        margin-bottom: 1.5rem;
        letter-spacing: -0.5px;
    }
    
    p {
        color: #b0bdce;
        font-size: 1rem;
        line-height: 1.6;
        text-align: center;
    }
    
    /* Icon styling */
    .title-icon {
        color: #38bdf8;
        font-size: 2.4rem;
        margin-right: 0.5rem;
        vertical-align: middle;
    }
    
    /* File uploader area */
    .upload-area {
        background: #111827;
        border-radius: 12px;
        border: 1px dashed #2f4265;
        padding: 2rem;
        margin: 2rem 0;
        text-align: center;
        transition: all 0.2s ease;
    }
    
    /* Hide default Streamlit uploader styling */
    .stFileUploader {
        padding: 0 !important;
    }
    
    .stFileUploader > div {
        padding: 0 !important;
    }
    
    .stFileUploader > div > small {
        display: none !important;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(90deg, #0ea5e9, #2563eb);
        border: none;
        color: white;
        font-weight: 600;
        padding: 0.8rem 2rem;
        border-radius: 8px;
        cursor: pointer;
        width: 100%;
        margin-top: 1rem;
        transition: all 0.2s ease;
        box-shadow: 0 4px 12px rgba(14, 165, 233, 0.25);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(14, 165, 233, 0.35);
    }
    
    /* Result area */
    .result-box {
        background: #0f172a;
        border-radius: 12px;
        padding: 2rem;
        margin: 1.5rem 0;
        border-left: 4px solid #38bdf8;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    
    /* Device list */
    .device-list {
        list-style-type: none;
        padding: 0;
        margin: 1.5rem 0 0 0;
    }
    
    .device-item {
        background: #1e293b;
        margin: 0.8rem 0;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        display: flex;
        align-items: center;
        transition: all 0.2s ease;
    }
    
    .device-item:hover {
        background: #233249;
        transform: translateX(4px);
    }
    
    .device-icon {
        margin-right: 1rem;
        font-size: 1.25rem;
    }
    
    /* Image preview */
    .image-preview {
        margin: 1.5rem 0;
        text-align: center;
    }
    
    .image-preview img {
        max-height: 350px;
        object-fit: contain;
        border-radius: 8px;
        border: 1px solid #2f4265;
    }
    
    /* Loading state */
    .loading {
        display: flex;
        align-items: center;
        justify-content: center;
        color: #38bdf8;
        font-weight: 500;
    }
    
    .loading::before {
        content: "🔄";
        margin-right: 0.5rem;
    }
    
    /* Footer */
    .app-footer {
        text-align: center;
        margin-top: 2rem;
        color: #64748b;
        font-size: 0.875rem;
        border-top: 1px solid #1e293b;
        padding-top: 1.5rem;
    }
    
    /* Placeholder text */
    .placeholder-text {
        color: #64748b;
        text-align: center;
        font-style: italic;
        padding: 1rem;
    }
    
    /* Fix for Streamlit components */
    div[data-testid="stVerticalBlock"] {
        gap: 0 !important;
    }
    
    /* Fix for Streamlit spinners */
    div[data-testid="stSpinner"] {
        text-align: center;
        margin: 1rem auto;
    }
    
    /* Clean up caption styling */
    .css-1aehpvj {
        color: #64748b !important;
        font-size: 0.875rem !important;
        padding: 0.5rem 0 !important;
    }
</style>
""", unsafe_allow_html=True)

def format_device_list(result_text):
    """Format the result into a clean list"""
    # Try to extract devices from the result text
    devices = []
    
    # Check if result is in list format like [device1, device2]
    if '[' in result_text and ']' in result_text:
        list_content = result_text[result_text.find('[')+1:result_text.find(']')]
        devices = [device.strip(' "\'') for device in list_content.split(',')]
    else:
        # Alternative parsing if not in expected format
        for item in re.split(r'[,.\n]', result_text):
            clean_item = item.strip()
            if clean_item and clean_item not in ['[', ']']:
                devices.append(clean_item)
    
    # Remove empty entries
    devices = [device for device in devices if device]
    
    # Generate HTML for the device list
    if not devices:
        return "<p class='placeholder-text'>No devices detected or could not parse the result.</p>"
    
    device_icons = {
        "laptop": "💻",
        "computer": "🖥️",
        "phone": "📱",
        "smartphone": "📱",
        "camera": "📷",
        "keyboard": "⌨️",
        "mouse": "🖱️",
        "headphones": "🎧",
        "speaker": "🔊",
        "tv": "📺",
        "television": "📺",
        "monitor": "🖥️",
        "tablet": "📱",
        "printer": "🖨️",
        "scanner": "📠",
        "router": "📡",
        "watch": "⌚",
        "smartwatch": "⌚",
        "game": "🎮",
        "console": "🎮",
        "controller": "🎮"
    }
    
    html = "<ul class='device-list'>"
    for device in devices:
        # Find an appropriate icon or use default
        icon = "🔌"  # Default icon
        for key, value in device_icons.items():
            if key in device.lower():
                icon = value
                break
                
        html += f"<li class='device-item'><span class='device-icon'>{icon}</span> {device}</li>"
    html += "</ul>"
    
    return html

def detect_devices(image_file):
    """Function to send image to backend and get detection results"""
    try:
        # Create a temporary file for the uploaded image
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
        temp_file.write(image_file.getvalue())
        temp_file.close()
        
        # Option 1: Using local API endpoint if available
        try:
            files = {'image': open(temp_file.name, 'rb')}
            data = {
                'text_input': 'Just return the name of electronic devices in this image in the form of a list,for example if u have an image of a laptop,mouse,monitor. you should return [laptop,mouse,monitor]',
                'system_prompt': 'You are an experienced electronic device detector',
                'model_id': 'Qwen/Qwen2-VL-7B-Instruct',
                'api_name': '/run_example'
            }
            response = requests.post('http://localhost:5000/api/detect', files=files, data=data)
            response.raise_for_status()
            result = response.json()['result']
        except:
            # Option 2: Using Gradio client directly if API is not available
            client = Client("maxiw/Qwen2-VL-Detection")
            result = client.predict(
                image=handle_file(temp_file.name),
                text_input='Just return the name of electronic devices in this image in the form of a list,for example if u have an image of a laptop,mouse,monitor. you should return [laptop,mouse,monitor]',
                system_prompt='You are an experienced electronic device detector',
                model_id="Qwen/Qwen2-VL-7B-Instruct",
                api_name="/run_example"
            )[0]

        # Clean up the temporary file
        os.unlink(temp_file.name)
        return result
    except Exception as e:
        return f"Error: {str(e)}"

# App UI with fixed layout
st.markdown('<div class="app-container">', unsafe_allow_html=True)

# Clean header
st.markdown(f'<h1><span class="title-icon">🔍</span> Electronic Device Detector</h1>', unsafe_allow_html=True)
st.markdown('<p>Upload any image to identify and detect electronic devices using AI-powered recognition technology</p>', unsafe_allow_html=True)

# File upload area with custom styling
st.markdown('<div class="upload-area">', unsafe_allow_html=True)
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"], 
                                label_visibility="collapsed")
st.markdown("Drag and drop file here<br>Limit 200MB per file • JPG, JPEG, PNG", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Preview image
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.markdown('<div class="image-preview">', unsafe_allow_html=True)
    st.image(image, caption='Uploaded Image', use_column_width=False)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Detect button
    if st.button('Detect Devices'):
        with st.spinner(''):
            st.markdown('<div class="result-box">', unsafe_allow_html=True)
            st.markdown('<p class="loading">Analyzing image... Please wait</p>', unsafe_allow_html=True)
            result = detect_devices(uploaded_file)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Display result
        st.markdown('<div class="result-box">', unsafe_allow_html=True)
        st.markdown('<p><strong>Detected Devices:</strong></p>', unsafe_allow_html=True)
        st.markdown(format_device_list(result), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
else:
    # Display placeholder text when no image is uploaded
    st.markdown('<div class="result-box">', unsafe_allow_html=True)
    st.markdown('<p class="placeholder-text">📤 Upload an image and click "Detect Devices" to identify electronic devices in your photo</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown('<div class="app-footer">', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)