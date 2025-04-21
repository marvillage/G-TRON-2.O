import streamlit as st
from google.cloud import vision
import io
import os
from PIL import Image, ImageDraw
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM

# Set Google Cloud credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "service-account-key.json"

# Pre-defined waste classification dictionary with reasons
WASTE_CLASSIFICATIONS = {
    "battery": {
        "type": "Toxic", 
        "disposal": "Take to recycling center or hazardous waste facility",
        "reason": "Contains harmful chemicals that can leach into soil and water"
    },
    "batteries": {
        "type": "Toxic", 
        "disposal": "Take to recycling center or hazardous waste facility",
        "reason": "Contains harmful chemicals that can leach into soil and water"
    },
    "alkaline battery": {
        "type": "Toxic", 
        "disposal": "Take to recycling center or hazardous waste facility",
        "reason": "Contains heavy metals and corrosive materials"
    },
    "lithium battery": {
        "type": "Toxic", 
        "disposal": "Take to recycling center or hazardous waste facility",
        "reason": "Fire hazard and contains reactive metals"
    },
    "electronic waste": {
        "type": "Toxic", 
        "disposal": "E-waste recycling center",
        "reason": "Contains heavy metals and flame retardants"
    },
    "hazardous waste": {
        "type": "Toxic", 
        "disposal": "Hazardous waste facility",
        "reason": "Contains chemicals harmful to environment and health"
    },
    "chemical waste": {
        "type": "Toxic", 
        "disposal": "Hazardous waste facility",
        "reason": "Contains substances that can contaminate ecosystems"
    },
    "box": {
        "type": "Non-toxic", 
        "disposal": "Recycle if cardboard/paper, general waste if plastic",
        "reason": "Made from natural fibers that biodegrade safely"
    },
    "plastic": {
        "type": "Non-toxic", 
        "disposal": "Recycle if appropriate type",
        "reason": "Inert material but takes centuries to decompose"
    },
    "paper": {
        "type": "Non-toxic", 
        "disposal": "Recycle",
        "reason": "Plant-based material that biodegrades naturally"
    },
    "glass": {
        "type": "Non-toxic", 
        "disposal": "Recycle",
        "reason": "Inert material made from natural minerals"
    },
    "metal": {
        "type": "Non-toxic", 
        "disposal": "Recycle",
        "reason": "Can be melted down and reused indefinitely"
    },
    "organic waste": {
        "type": "Non-toxic", 
        "disposal": "Compost",
        "reason": "Naturally decomposes and returns nutrients to soil"
    }
}

def analyze_image_content(image_bytes):
    """Uses Google Cloud Vision API to analyze image content."""
    client = vision.ImageAnnotatorClient()
    image = vision.Image(content=image_bytes)
    
    # Get both object detection and label detection
    object_response = client.object_localization(image=image)
    label_response = client.label_detection(image=image)
    
    # Process object detections
    objects = object_response.localized_object_annotations
    
    # Process label detections
    labels = label_response.label_annotations
    
    # Check if we have any specific labels related to batteries or hazardous waste
    battery_related = False
    relevant_labels = []
    
    for label in labels:
        if any(keyword in label.description.lower() for keyword in ["battery", "batteries", "hazardous", "waste", "electronic", "toxic"]):
            battery_related = True
            relevant_labels.append(label.description)
    
    # If we have battery labels but no objects, create a generic object
    if battery_related and not objects:
        # Define the whole image as containing batteries
        if "battery" in " ".join(relevant_labels).lower() or "batteries" in " ".join(relevant_labels).lower():
            waste_type = "batteries"
        else:
            waste_type = relevant_labels[0]
            
        # Create a generic waste object covering most of the image
        return [WasteObject(waste_type, 0.95, [(0.1, 0.1), (0.9, 0.1), (0.9, 0.9), (0.1, 0.9)])], relevant_labels
    
    return objects, relevant_labels

class WasteObject:
    """Custom class to represent waste objects."""
    def __init__(self, name, score, vertices):
        self.name = name
        self.score = score
        self.bounding_poly = type('obj', (), {'normalized_vertices': 
                                             [type('vertex', (), {'x': v[0], 'y': v[1]}) 
                                              for v in vertices]})()

def get_waste_classification(object_name, image_labels=None):
    """Classify waste based on object name and image labels."""
    # Check if object is in our pre-defined dictionary first
    for key, value in WASTE_CLASSIFICATIONS.items():
        if key in object_name.lower():
            return value["type"], value["disposal"], value["reason"]
    
    # Check if there are battery-related labels
    if image_labels and any("battery" in label.lower() for label in image_labels):
        return "Toxic", "Take to recycling center or hazardous waste facility", "Contains harmful chemicals that can leach into soil and water"
    
    # For unknown items, use the LLM
    template = """
    Classify this waste item: {object_name}
    Output exactly three lines:
    1. Type: [Toxic or Non-toxic]
    2. Disposal: [Brief 5-10 word instruction]
    3. Reason: [One brief sentence explaining classification]
    """
    prompt = ChatPromptTemplate.from_template(template)
    model = OllamaLLM(model="llama3.2:3b", temperature=0.1)
    chain = prompt | model
    response = chain.invoke({"object_name": object_name})
    
    # Parse the result
    lines = response.strip().split('\n')
    if len(lines) >= 3:
        waste_type = "Toxic" if "toxic" in lines[0].lower() and "non-toxic" not in lines[0].lower() else "Non-toxic"
        disposal = lines[1].replace("2. Disposal:", "").strip()
        reason = lines[2].replace("3. Reason:", "").strip()
        return waste_type, disposal, reason
    
    # Fallback for parsing errors
    return "Non-toxic", "General waste", "Not enough information to determine toxicity"

def draw_boxes(image_bytes, objects, waste_info):
    """Draws bounding boxes around detected objects with waste classification."""
    image = Image.open(io.BytesIO(image_bytes))
    draw = ImageDraw.Draw(image)
    
    for i, obj in enumerate(objects):
        # Determine color based on classification
        waste_type = waste_info[i][0]
        box_color = "#FF3A5E" if waste_type == "Toxic" else "#00B4D8" # Red for toxic, blue for non-toxic
        
        box = obj.bounding_poly.normalized_vertices
        # Draw rectangle
        draw.polygon([
            (box[0].x * image.width, box[0].y * image.height),
            (box[1].x * image.width, box[1].y * image.height),
            (box[2].x * image.width, box[2].y * image.height),
            (box[3].x * image.width, box[3].y * image.height),
        ], outline=box_color, width=3)
        
        # Add label
        draw.text(
            (box[0].x * image.width, box[0].y * image.height - 20),
            f"{obj.name}: {waste_type}",
            fill=box_color
        )
    return image

# Set Streamlit page config 
st.set_page_config(
    page_title="EcoScan: Waste Classification",
    page_icon="♻️",
    layout="wide"
)

# Enhanced Custom CSS for a more visually appealing blue and black theme
st.markdown("""
<style>
    /* Modern Enhanced Blue and Black Theme */
    .stApp {
        background: linear-gradient(135deg, #0A192F 0%, #091429 100%);
        color: #E6F1FF;
    }
    .stButton>button {
        background: linear-gradient(90deg, #00B4D8 0%, #0077B6 100%);
        color: white;
        border-radius: 8px;
        border: none;
        padding: 12px 30px;
        font-weight: bold;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
        width: 100%;
        margin-top: 10px;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #0077B6 0%, #00B4D8 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 8px rgba(0, 0, 0, 0.2);
    }
    h1, h2, h3 {
        color: #00B4D8;
        font-weight: bold;
        text-shadow: 0px 2px 4px rgba(0, 0, 0, 0.5);
    }
    h1 {
        font-size: 2.5rem;
        margin-bottom: 0;
        background: linear-gradient(90deg, #00B4D8, #90E0EF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .subtitle {
        color: #8892B0;
        font-size: 1.2rem;
        margin-top: 0;
        margin-bottom: 2rem;
    }
    .stMarkdown {
        color: #CCD6F6;
    }
    .stDataFrame, .stTable {
        background-color: #172A45;
        border-radius: 10px;
        padding: 10px;
    }
    .css-nahz7x {
        background-color: #112240;
    }
    .css-xq1lnh-EmotionIconBase {
        color: #00B4D8;
    }
    .stSpinner > div > div {
        border-top-color: #00B4D8 !important;
    }
    .stAlert {
        background-color: rgba(17, 34, 64, 0.7);
        border-radius: 10px;
        border-left-color: #00B4D8;
        backdrop-filter: blur(10px);
    }
    /* Image container */
    .image-container {
        background-color: rgba(17, 34, 64, 0.5);
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 10px 15px rgba(0, 0, 0, 0.2);
        border: 1px solid rgba(0, 180, 216, 0.2);
        margin-bottom: 30px;
        transition: all 0.3s ease;
    }
    .image-container:hover {
        box-shadow: 0 15px 25px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(0, 180, 216, 0.4);
    }
    /* Style for status containers */
    .toxic-container {
        background: linear-gradient(to right, rgba(255, 58, 94, 0.1), rgba(17, 34, 64, 0.7));
        border-left: 5px solid #FF3A5E;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        box-shadow: 0 5px 15px rgba(255, 58, 94, 0.1);
    }
    .nontoxic-container {
        background: linear-gradient(to right, rgba(0, 180, 216, 0.1), rgba(17, 34, 64, 0.7));
        border-left: 5px solid #00B4D8;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        box-shadow: 0 5px 15px rgba(0, 180, 216, 0.1);
    }
    /* Card-like containers */
    .info-card {
        background: rgba(17, 34, 64, 0.7);
        padding: 25px;
        border-radius: 15px;
        margin-bottom: 25px;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
        border: 1px solid rgba(0, 180, 216, 0.1);
        backdrop-filter: blur(10px);
    }
    .info-card:hover {
        box-shadow: 0 12px 20px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(0, 180, 216, 0.3);
    }
    .header-container {
        display: flex;
        align-items: center;
        margin-bottom: 20px;
        padding: 15px;
        background: rgba(17, 34, 64, 0.5);
        border-radius: 15px;
        border-bottom: 3px solid #00B4D8;
    }
    .logo {
        font-size: 50px;
        margin-right: 20px;
        text-shadow: 0 0 10px rgba(0, 180, 216, 0.7);
    }
    /* File uploader */
    .css-1qrvfrg {
        background-color: rgba(17, 34, 64, 0.5);
        border: 2px dashed rgba(0, 180, 216, 0.3);
        padding: 30px;
        border-radius: 15px;
        text-align: center;
    }
    /* Results section */
    .results-section {
        margin-top: 40px;
        padding-top: 30px;
        border-top: 2px solid rgba(0, 180, 216, 0.3);
    }
    /* Item cards */
    .item-card {
        display: flex;
        align-items: center;
        margin-bottom: 15px;
        padding: 15px;
        border-radius: 10px;
        background-color: rgba(17, 34, 64, 0.5);
    }
    .item-icon {
        font-size: 30px;
        margin-right: 15px;
    }
    .item-details {
        flex-grow: 1;
    }
    .item-name {
        font-weight: bold;
        margin-bottom: 5px;
    }
    .item-reason {
        font-style: italic;
        opacity: 0.8;
    }
    .progress-bar {
        height: 5px;
        background-color: #112240;
        border-radius: 5px;
        overflow: hidden;
        margin-bottom: 20px;
    }
    .progress-fill {
        height: 100%;
        width: 0;
        background: linear-gradient(90deg, #00B4D8, #0077B6);
        animation: progress 2s forwards;
    }
    @keyframes progress {
        0% { width: 0; }
        100% { width: 100%; }
    }
    /* Glowing effect for important elements */
    .glow-text {
        text-shadow: 0 0 10px rgba(0, 180, 216, 0.7);
    }
    /* Footer */
    .footer {
        text-align: center;
        margin-top: 50px;
        padding: 20px;
        background: rgba(17, 34, 64, 0.5);
        border-radius: 10px;
        font-size: 0.9rem;
        color: #8892B0;
        border-top: 1px solid rgba(0, 180, 216, 0.2);
    }
    /* Mobile responsive design */
    @media (max-width: 768px) {
        .header-container {
            flex-direction: column;
            text-align: center;
        }
        .logo {
            margin-right: 0;
            margin-bottom: 10px;
        }
    }
</style>
""", unsafe_allow_html=True)

# App header with logo
st.markdown("""
<div class="header-container">
    <div class="logo">♻️</div>
    <div>
        <h1>EcoScan: Waste Detection</h1>
        <p class="subtitle">AI-Powered Waste Classification for Environmental Safety</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Main content - now in a vertical layout
st.markdown("<div class='info-card'>", unsafe_allow_html=True)
st.markdown("""
### How It Works
1. Upload an image containing waste material
2. Click 'Analyze Waste' to process the image
3. View detection results with classification
4. Learn proper disposal methods based on toxicity

The system can identify various types of waste including batteries, electronics, plastics, paper, and more.
""")
st.markdown("</div>", unsafe_allow_html=True)

# Image upload section
st.markdown("<div class='image-container'>", unsafe_allow_html=True)
uploaded_file = st.file_uploader("Upload an image of waste", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image_bytes = uploaded_file.read()
    st.image(image_bytes, caption="Uploaded Image", use_container_width=True)
    
    if st.button("Analyze Waste"):
        st.markdown("<div class='progress-bar'><div class='progress-fill'></div></div>", unsafe_allow_html=True)
        
        with st.spinner("Processing image..."):
            # Detect objects and analyze image content
            objects, image_labels = analyze_image_content(image_bytes)
            
            # Results section
            st.markdown("<div class='results-section'>", unsafe_allow_html=True)
            st.markdown("## <span class='glow-text'>Analysis Results</span>", unsafe_allow_html=True)
            
            if objects:
                st.success(f"Found {len(objects)} waste items!")
                
                # Get waste classifications for each object
                waste_info = []
                
                for obj in objects:
                    waste_type, disposal, reason = get_waste_classification(obj.name, image_labels)
                    waste_info.append((waste_type, disposal, reason))
                
                # Draw bounding boxes
                annotated_image = draw_boxes(image_bytes, objects, waste_info)
                st.image(annotated_image, caption="Classified Waste Objects", use_container_width=True)
                
                # Display detected objects grouped by classification
                toxic_items = [(obj.name, info[1], info[2]) for obj, info in zip(objects, waste_info) if info[0] == "Toxic"]
                nontoxic_items = [(obj.name, info[1], info[2]) for obj, info in zip(objects, waste_info) if info[0] == "Non-toxic"]
                
                if toxic_items:
                    st.markdown("<div class='toxic-container'>", unsafe_allow_html=True)
                    st.markdown("### ⚠️ Toxic Items")
                    st.markdown("These items require special handling due to harmful components.")
                    
                    for item, disposal, reason in toxic_items:
                        st.markdown(f"""
                        <div class="item-card">
                            <div class="item-icon">⚠️</div>
                            <div class="item-details">
                                <div class="item-name">{item}</div>
                                <div>{disposal}</div>
                                <div class="item-reason">Why toxic: {reason}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                
                if nontoxic_items:
                    st.markdown("<div class='nontoxic-container'>", unsafe_allow_html=True)
                    st.markdown("### ✅ Non-toxic Items")
                    st.markdown("These items are generally safe for standard disposal methods.")
                    
                    for item, disposal, reason in nontoxic_items:
                        st.markdown(f"""
                        <div class="item-card">
                            <div class="item-icon">✅</div>
                            <div class="item-details">
                                <div class="item-name">{item}</div>
                                <div>{disposal}</div>
                                <div class="item-reason">Why non-toxic: {reason}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                
                # Show related image labels
                if image_labels:
                    st.markdown("<div class='info-card'>", unsafe_allow_html=True)
                    st.markdown("#### 🏷️ Related Categories")
                    st.write(", ".join(image_labels))
                    st.markdown("</div>", unsafe_allow_html=True)
                
                # Show battery disposal instructions if batteries found
                if toxic_items and any("battery" in item[0].lower() for item in toxic_items):
                    st.markdown("<div class='toxic-container'>", unsafe_allow_html=True)
                    st.markdown("### 🔋 Battery Disposal Instructions")
                    st.markdown("""
                    • Never dispose of batteries in regular trash
                    • Take to designated battery recycling drop-off points
                    • Many electronics stores accept used batteries
                    • Keep batteries separated and tape terminals of lithium batteries
                    • Check with your local waste management authority for options
                    """)
                    st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.warning("No waste objects detected using standard object detection.")
                
                # Fallback to image labels
                if image_labels:
                    st.markdown("<div class='info-card'>", unsafe_allow_html=True)
                    st.info("Image analysis detected the following waste categories:")
                    st.write(", ".join(image_labels))
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    if any("battery" in label.lower() for label in image_labels):
                        st.markdown("<div class='toxic-container'>", unsafe_allow_html=True)
                        st.markdown("### 🔋 Battery Detected - Classified as Toxic Waste")
                        st.markdown("*Why toxic: Contains harmful chemicals that can leach into soil and water*")
                        st.markdown("""
                        #### Battery Disposal Instructions:
                        • Never dispose of batteries in regular trash
                        • Take to designated battery recycling drop-off points
                        • Many electronics stores accept used batteries
                        • Keep batteries separated and tape terminals of lithium batteries
                        • Check with your local waste management authority for options
                        """)
                        st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.error("No waste objects or categories detected. Try another image.")
            
            st.markdown("</div>", unsafe_allow_html=True)  # End results section
st.markdown("</div>", unsafe_allow_html=True)  # End image container

# Footer
st.markdown("""
<div class="footer">
    <p>EcoScan Waste Detection System • Making proper waste disposal easier</p>
    <p>Powered by AI for environmental protection</p>
</div>
""", unsafe_allow_html=True)