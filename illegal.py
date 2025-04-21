import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore, storage
from firebase_admin.exceptions import FirebaseError
import pandas as pd
import folium
from streamlit_folium import folium_static
from PIL import Image
import io
import uuid
import datetime
import requests
import json
import time
import os
from geopy.geocoders import Nominatim

# App title and configuration
st.set_page_config(page_title="E-Waste Dumping Reporter", layout="wide")

# Initialize Firebase (if not already initialized)
@st.cache_resource
def initialize_firebase():
    try:
        # Check if already initialized
        firebase_admin.get_app()
    except ValueError:
        try:
            # Try to get credentials from Streamlit secrets
            if 'firebase' in st.secrets and 'service_account' in st.secrets.firebase:
                # Get the raw string and clean it
                service_account_str = st.secrets.firebase.service_account.strip()
                # Remove the triple quotes if present
                if service_account_str.startswith('"""') and service_account_str.endswith('"""'):
                    service_account_str = service_account_str[3:-3].strip()
                # Parse the JSON
                service_account_info = json.loads(service_account_str)
                cred = credentials.Certificate(service_account_info)
            else:
                st.error("Firebase service account credentials not found in secrets")
                return None, None
            
            # Initialize app with storage bucket
            firebase_admin.initialize_app(cred, {
                'storageBucket': 'e-waste-management-2a578.firebasestorage.app'
            })
        except Exception as e:
            st.error(f"Error initializing Firebase: {e}")
            st.warning("Running in demo mode without Firebase connection")
            return None, None
    
    # Return Firestore client and storage bucket
    try:
        db = firestore.client()
        # Try to get the bucket
        bucket = storage.bucket('e-waste-management-2a578.firebasestorage.app')
        # Verify bucket exists by attempting to list files
        list(bucket.list_blobs(max_results=1))
        return db, bucket
    except Exception as e:
        st.error(f"Error connecting to Firebase services: {e}")
        st.warning("Storage bucket not found. Please ensure the bucket exists in your Firebase project.")
        return None, None

# Initialize Firebase
db, bucket = initialize_firebase()

# Function to get user's location
def get_user_location():
    try:
        # Use IP-based geolocation as fallback
        response = requests.get('https://ipinfo.io/json')
        if response.status_code == 200:
            data = response.json()
            if 'loc' in data:
                lat, lng = map(float, data['loc'].split(','))
                return lat, lng, data.get('city', '') + ', ' + data.get('region', '') + ', ' + data.get('country', '')
    except Exception as e:
        st.error(f"Error getting location: {e}")
    
    # Default location if geolocation fails
    return 20.0, 0.0, "Unknown location"

# Function to geocode address
def geocode_location(address):
    try:
        geolocator = Nominatim(user_agent="e_waste_app")
        location = geolocator.geocode(address)
        if location:
            return location.latitude, location.longitude, location.address
    except:
        pass
    return None, None, None

# Function to reverse geocode coordinates
def reverse_geocode(lat, lng):
    try:
        geolocator = Nominatim(user_agent="e_waste_app")
        location = geolocator.reverse(f"{lat}, {lng}")
        if location:
            return location.address
    except:
        pass
    return "Unknown location"

# Function to upload file to Firebase Storage
def upload_file_to_storage(file_bytes, file_name, content_type):
    if bucket is None:
        st.warning("Running in demo mode - file upload is disabled")
        return "demo_image_url"
    
    try:
        # Create a unique filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        unique_filename = f"reports/{timestamp}_{file_name}"
        
        # Create a blob in the bucket
        blob = bucket.blob(unique_filename)
        
        # Upload the file
        blob.upload_from_string(
            file_bytes,
            content_type=content_type
        )
        
        # Make the blob publicly accessible
        blob.make_public()
        
        # Return the public URL
        return blob.public_url
    except Exception as e:
        st.error(f"Error uploading file: {e}")
        st.warning("Please ensure the storage bucket exists in your Firebase project and the service account has the necessary permissions.")
        return None

# Function to analyze image using Google Cloud Vision API
def analyze_image(image_url, api_key):
    if not api_key:
        # Mock data if API key not available
        return [
            {"name": "Electronic Components", "confidence": 85},
            {"name": "Waste Material", "confidence": 92}
        ]
    
    try:
        # Prepare request to Vision API
        headers = {'Content-Type': 'application/json'}
        payload = {
            "requests": [
                {
                    "image": {
                        "source": {
                            "imageUri": image_url
                        }
                    },
                    "features": [
                        {"type": "LABEL_DETECTION", "maxResults": 10},
                        {"type": "OBJECT_LOCALIZATION", "maxResults": 10}
                    ]
                }
            ]
        }
        
        # Make API request
        response = requests.post(
            f'https://vision.googleapis.com/v1/images:annotate?key={api_key}',
            headers=headers,
            data=json.dumps(payload)
        )
        
        if response.status_code != 200:
            st.error(f"Error from Vision API: {response.text}")
            return []
        
        data = response.json()
        
        # Process the results
        e_waste_keywords = ['electronic', 'computer', 'laptop', 'phone', 'battery', 
                         'circuit', 'television', 'monitor', 'appliance', 'cable', 
                         'wire', 'device']
        
        detected_types = []
        
        # Process label annotations
        if 'labelAnnotations' in data['responses'][0]:
            for label in data['responses'][0]['labelAnnotations']:
                label_lower = label['description'].lower()
                if any(keyword in label_lower for keyword in e_waste_keywords):
                    detected_types.append({
                        "name": label['description'],
                        "confidence": round(label['score'] * 100)
                    })
        
        # Process object annotations
        if 'localizedObjectAnnotations' in data['responses'][0]:
            for obj in data['responses'][0]['localizedObjectAnnotations']:
                obj_lower = obj['name'].lower()
                if any(keyword in obj_lower for keyword in e_waste_keywords):
                    detected_types.append({
                        "name": obj['name'],
                        "confidence": round(obj['score'] * 100)
                    })
        
        # If no e-waste detected, use generic detection
        if not detected_types and 'labelAnnotations' in data['responses'][0]:
            # Get top 3 general labels
            for label in data['responses'][0]['labelAnnotations'][:3]:
                detected_types.append({
                    "name": label['description'],
                    "confidence": round(label['score'] * 100)
                })
        
        return detected_types
    
    except Exception as e:
        st.error(f"Error analyzing image: {e}")
        # Fallback to mock data
        return [
            {"name": "Electronic Components", "confidence": 85},
            {"name": "Waste Material", "confidence": 92}
        ]

# Function to fetch reports from Firestore
def fetch_reports():
    if db is None:
        st.warning("Running in demo mode - using sample data")
        return [
            {
                'id': 'demo1',
                'description': 'Sample report 1',
                'status': 'Pending',
                'createdAt': datetime.datetime.now().isoformat(),
                'location': {
                    'lat': 20.0,
                    'lng': 0.0,
                    'address': 'Demo Location 1'
                },
                'imageUrl': 'https://via.placeholder.com/300'
            }
        ]
    
    try:
        reports_ref = db.collection('reports')
        docs = reports_ref.order_by('createdAt', direction=firestore.Query.DESCENDING).stream()
        
        reports = []
        for doc in docs:
            report_data = doc.to_dict()
            report_data['id'] = doc.id
            reports.append(report_data)
            
        return reports
    except Exception as e:
        st.error(f"Error fetching reports: {e}")
        return []

# Function to update report status
def update_report_status(report_id, status):
    if db is None:
        st.warning("Running in demo mode - status update is disabled")
        return True
    
    try:
        report_ref = db.collection('reports').document(report_id)
        report_ref.update({
            'status': status,
            'updatedAt': datetime.datetime.now().isoformat()
        })
        return True
    except Exception as e:
        st.error(f"Error updating report status: {e}")
        return False

# Function to create folium map
def create_map(reports, center_lat=20.0, center_lng=0.0, zoom=3):
    # Create a map
    m = folium.Map(location=[center_lat, center_lng], zoom_start=zoom, 
                  tiles="OpenStreetMap")
    
    # Add heat map layer
    heat_data = []
    for report in reports:
        if report.get('location') and report['location'].get('lat') and report['location'].get('lng'):
            heat_data.append([report['location']['lat'], report['location']['lng'], 1])
    
    if heat_data:
        from folium.plugins import HeatMap
        HeatMap(heat_data, radius=15).add_to(m)
    
    # Add markers for each report
    for report in reports:
        if report.get('location') and report['location'].get('lat') and report['location'].get('lng'):
            popup_html = f"""
            <div style="width:200px">
                <h4>Report</h4>
                <p>Status: {report.get('status', 'Pending')}</p>
                <p>Date: {report.get('createdAt', '')[:10]}</p>
            </div>
            """
            
            # Create marker with popup
            folium.Marker(
                location=[report['location']['lat'], report['location']['lng']],
                popup=folium.Popup(popup_html, max_width=300),
                icon=folium.Icon(
                    color='red' if report.get('status') == 'Pending' else 
                          'orange' if report.get('status') == 'Verified' else 
                          'green'
                )
            ).add_to(m)
    
    return m

# App header with custom CSS
st.markdown("""
<style>
    .app-header {
        background-color: #1E88E5;
        color: white;
        padding: 10px 0;
        text-align: center;
        border-radius: 5px;
        margin-bottom: 20px;
    }
    .report-card {
        border: 1px solid #ddd;
        border-radius: 8px;
        overflow: hidden;
        margin-bottom: 15px;
    }
    .report-image {
        position: relative;
        height: 180px;
    }
    .report-image img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }
    .status-badge {
        position: absolute;
        top: 10px;
        right: 10px;
        padding: 5px 10px;
        border-radius: 15px;
        font-weight: bold;
    }
    .status-pending {
        background-color: #FFC107;
        color: black;
    }
    .status-verified {
        background-color: #2196F3;
        color: white;
    }
    .status-resolved {
        background-color: #4CAF50;
        color: white;
    }
    .report-details {
        padding: 10px;
    }
    .modal-container {
        padding: 20px;
        border: 1px solid #ddd;
        border-radius: 8px;
        background-color: white;
    }
</style>
<div class="app-header">
    <h1>E-Waste Dumping Reporter</h1>
</div>
""", unsafe_allow_html=True)

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Map View", "Report Illegal Dumping", "View Reports"])

# Fetch reports (common for all pages)
reports = fetch_reports()

# Map View Page
if page == "Map View":
    st.header("Illegal Dumping Heatmap")
    
    # Get user location for centering map
    user_lat, user_lng, user_address = get_user_location()
    
    # Create and display map
    map_container = st.container()
    with map_container:
        # Create the map
        m = create_map(reports, user_lat, user_lng, 5)
        
        # Display the map
        folium_static(m, width=800, height=500)
    
    # Recent Reports Section
    st.header("Recent Reports")
    
    # Create a grid layout
    cols = st.columns(3)
    
    # Display only up to 6 recent reports
    for i, report in enumerate(reports[:6]):
        col = cols[i % 3]
        with col:
            with st.container():
                st.markdown(f"""
                <div class="report-card">
                    <div class="report-image">
                        <img src="{report.get('imageUrl', 'https://via.placeholder.com/300')}" alt="Reported waste">
                        <span class="status-badge status-{report.get('status', 'pending').lower()}">{report.get('status', 'Pending')}</span>
                    </div>
                    <div class="report-details">
                        <p>{report.get('location', {}).get('address', 'Unknown location')}</p>
                        <p>{report.get('createdAt', '')[:10]}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"View Details #{i+1}"):
                    st.session_state.selected_report = report
                    st.session_state.show_report_details = True
                    st.rerun()

# Report Illegal Dumping Page
elif page == "Report Illegal Dumping":
    st.header("Report Illegal E-Waste Dumping")
    
    # Form for reporting
    with st.form("report_form"):
        # Upload image
        uploaded_file = st.file_uploader("Upload Photo Evidence", type=["jpg", "jpeg", "png"])
        
        if uploaded_file:
            # Display preview
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_container_width=True)
            
            # Store in session state
            if 'image_file' not in st.session_state:
                st.session_state.image_file = uploaded_file
                st.session_state.image_analyzed = False
                st.session_state.waste_types = []
        
        # Location input
        st.subheader("Location")
        
        # Get initial location
        if 'user_location' not in st.session_state:
            lat, lng, address = get_user_location()
            st.session_state.user_location = {
                'lat': lat,
                'lng': lng,
                'address': address
            }
        
        # Show current location
        st.write(f"Current location: {st.session_state.user_location['address']}")
        
        # Allow manual address input
        manual_address = st.text_input("Or enter address manually:")
        if manual_address:
            lat, lng, address = geocode_location(manual_address)
            if lat and lng:
                st.session_state.user_location = {
                    'lat': lat,
                    'lng': lng,
                    'address': address
                }
                st.success(f"Location updated to: {address}")
            else:
                st.error("Could not find this address. Please try another.")
        
        # Show location on map
        loc_map = create_map([], 
                           st.session_state.user_location['lat'], 
                           st.session_state.user_location['lng'], 
                           zoom=13)
        
        # Add user marker
        folium.Marker(
            [st.session_state.user_location['lat'], st.session_state.user_location['lng']],
            popup="Selected Location",
            icon=folium.Icon(color='blue')
        ).add_to(loc_map)
        
        folium_static(loc_map, width=700, height=300)
        
        # Description
        description = st.text_area("Description", 
                                  placeholder="Describe the dumping incident, waste type, and other details",
                                  height=100)
        
        # Anonymous reporting
        anonymous = st.checkbox("Report Anonymously")
        
        # Submit button
        submit_button = st.form_submit_button("Submit Report")
        
        if submit_button:
            if not uploaded_file:
                st.error("Please upload an image first.")
            elif not description:
                st.error("Please provide a description.")
            else:
                with st.spinner("Submitting report..."):
                    try:
                        # Upload image to Firebase Storage
                        file_bytes = uploaded_file.getvalue()
                        content_type = uploaded_file.type
                        image_url = upload_file_to_storage(file_bytes, uploaded_file.name, content_type)
                        
                        if not image_url:
                            st.error("Failed to upload image.")
                            st.stop()
                        
                        # Analyze image if not already done
                        if not st.session_state.get('image_analyzed', False):
                            # Get API key from secrets
                            vision_api_key = st.secrets.get("GOOGLE_VISION_API_KEY", "")
                            waste_types = analyze_image(image_url, vision_api_key)
                            st.session_state.waste_types = waste_types
                            st.session_state.image_analyzed = True
                        else:
                            waste_types = st.session_state.waste_types
                        
                        # Prepare report data
                        report_data = {
                            'description': description,
                            'anonymous': anonymous,
                            'imageUrl': image_url,
                            'location': st.session_state.user_location,
                            'wasteTypes': waste_types,
                            'status': 'Pending',
                            'createdAt': datetime.datetime.now().isoformat()
                        }
                        
                        # Save to Firestore
                        doc_ref = db.collection('reports').document()
                        doc_ref.set(report_data)
                        
                        # Success message
                        st.success("Report submitted successfully!")
                        
                        # Reset session state
                        if 'image_file' in st.session_state:
                            del st.session_state.image_file
                        if 'image_analyzed' in st.session_state:
                            del st.session_state.image_analyzed
                        if 'waste_types' in st.session_state:
                            del st.session_state.waste_types
                        
                        # Show the waste types identified
                        if waste_types:
                            st.subheader("AI-Detected Items:")
                            for type_info in waste_types:
                                st.write(f"- {type_info['name']} ({type_info['confidence']}% confidence)")
                    
                    except Exception as e:
                        st.error(f"Error submitting report: {e}")

# View Reports Page
elif page == "View Reports":
    st.header("All Reports")
    
    # Filter options
    status_filter = st.selectbox("Filter by Status", 
                               ["All", "Pending", "Verified", "Resolved"])
    
    # Apply filters
    filtered_reports = reports
    if status_filter != "All":
        filtered_reports = [r for r in reports if r.get('status') == status_filter]
    
    # Display reports in a table
    if filtered_reports:
        # Convert to DataFrame for easier display
        report_data = []
        for report in filtered_reports:
            report_data.append({
                'ID': report.get('id', ''),
                'Date': report.get('createdAt', '')[:10],
                'Location': report.get('location', {}).get('address', 'Unknown'),
                'Status': report.get('status', 'Pending'),
                'Description': report.get('description', '')[:50] + '...' if report.get('description') else '',
            })
        
        df = pd.DataFrame(report_data)
        st.dataframe(df, use_container_width=True)
        
        # Select report to view details
        selected_id = st.selectbox("Select report to view details", 
                                 [""] + [r['ID'] for r in report_data])
        
        if selected_id and selected_id != "":
            selected_report = next((r for r in filtered_reports if r.get('id') == selected_id), None)
            if selected_report:
                # Display report details directly here instead of using session state
                st.header("Report Details")
                
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.image(selected_report.get('imageUrl', 'https://via.placeholder.com/400'), 
                           caption="Reported Waste", use_container_width=True)
                
                with col2:
                    st.markdown(f"**Date:** {selected_report.get('createdAt', '')[:10]}")
                    st.markdown(f"**Location:** {selected_report.get('location', {}).get('address', 'Unknown')}")
                    st.markdown(f"**Status:** {selected_report.get('status', 'Pending')}")
                    st.markdown(f"**Description:** {selected_report.get('description', 'No description provided.')}")
                    
                    if selected_report.get('wasteTypes'):
                        st.markdown("**AI-Detected Items:**")
                        for item in selected_report['wasteTypes']:
                            st.markdown(f"- {item['name']} ({item['confidence']}%)")
                    
                    # Status update buttons
                    if selected_report.get('status') == 'Pending':
                        if st.button("Verify Report"):
                            if update_report_status(selected_report['id'], 'Verified'):
                                st.success("Report status updated to Verified!")
                                time.sleep(1)
                                st.rerun()
                    
                    elif selected_report.get('status') == 'Verified':
                        if st.button("Mark as Resolved"):
                            if update_report_status(selected_report['id'], 'Resolved'):
                                st.success("Report status updated to Resolved!")
                                time.sleep(1)
                                st.rerun()
                    
                    elif selected_report.get('status') == 'Resolved':
                        st.success("This issue has been resolved.")
    else:
        st.info("No reports found with the selected filter.")

# Remove the old report details modal code that was here before
# Initialize session state variables
if 'user_location' not in st.session_state:
    lat, lng, address = get_user_location()
    st.session_state.user_location = {
        'lat': lat,
        'lng': lng,
        'address': address
    }