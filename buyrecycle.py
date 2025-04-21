import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.llms import Ollama
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
import random

# Set page title
st.set_page_config(page_title="Recyclee E-Waste Chatbot", page_icon="♻️")
def apply_custom_css():
    # CSS from the recyclee-ewaste-dark-theme file
    css = """
    /* Modern Dark Blue and Black Theme for Recyclee E-Waste Chatbot */

    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Global Styles and Variables */
    :root {
      --primary-dark: #0a1929;
      --secondary-dark: #0f2942;
      --accent-blue: #1e88e5;
      --accent-blue-light: #42a5f5;
      --accent-green: #4caf50;
      --text-primary: #ffffff;
      --text-secondary: #b0bec5;
      --success-green: #43a047;
      --danger-red: #e53935;
      --success-green-light: rgba(76, 175, 80, 0.1);
      --border-radius: 8px;
      --box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
    }

    /* Base Styles */
    body {
      background-color: var(--primary-dark);
      color: var(--text-primary);
      font-family: 'Inter', sans-serif;
      margin: 0;
      padding: 0;
      line-height: 1.6;
    }

    /* Streamlit Container Styling */
    .main .block-container {
      padding: 2rem 1rem;
      max-width: 1200px;
    }

    /* Header Styling */
    h1, h2, h3, h4, h5, h6 {
      color: var(--text-primary);
      font-weight: 600;
      letter-spacing: -0.025em;
    }

    h1 {
      font-size: 2.5rem;
      margin-bottom: 1rem;
      background: linear-gradient(90deg, var(--accent-blue-light), var(--accent-green));
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
      display: inline-block;
    }

    h2, .stMarkdown h2 {
      font-size: 1.75rem;
      color: var(--accent-blue-light);
      margin-top: 1.5rem;
    }

    h3, .stMarkdown h3 {
      font-size: 1.25rem;
      border-bottom: 1px solid var(--secondary-dark);
      padding-bottom: 0.5rem;
      margin-top: 1.25rem;
    }

    /* Text and Paragraph Styling */
    p, div {
      color: var(--text-secondary);
      font-size: 1rem;
    }

    a {
      color: var(--accent-blue-light);
      text-decoration: none;
      transition: color 0.2s ease;
    }

    a:hover {
      color: var(--accent-blue);
      text-decoration: underline;
    }

    /* Input Fields */
    .stTextInput > div > div > input {
      background-color: var(--secondary-dark);
      color: var(--text-primary);
      border: 1px solid var(--accent-blue);
      border-radius: var(--border-radius);
      padding: 0.75rem 1rem;
      font-size: 1rem;
      box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.1);
      transition: all 0.3s ease;
    }

    .stTextInput > div > div > input:focus {
      border-color: var(--accent-blue-light);
      box-shadow: 0 0 0 2px rgba(30, 136, 229, 0.2);
    }

    /* Buttons */
    .stButton > button {
      background-color: var(--accent-blue);
      color: var(--text-primary);
      border: none;
      border-radius: var(--border-radius);
      padding: 0.5rem 1rem;
      font-weight: 500;
      transition: all 0.2s ease;
      box-shadow: var(--box-shadow);
    }

    .stButton > button:hover {
      background-color: var(--accent-blue-light);
      transform: translateY(-2px);
    }

    .stButton > button:active {
      transform: translateY(1px);
    }

    /* Category Buttons */
    button[key^="cat_"] {
      background-color: var(--secondary-dark);
      border: 1px solid rgba(30, 136, 229, 0.3);
      color: var(--text-secondary);
      padding: 0.375rem 0.75rem;
      border-radius: var(--border-radius);
      transition: all 0.2s ease;
      margin: 0.25rem;
      font-size: 0.875rem;
    }

    button[key^="cat_"]:hover {
      background-color: rgba(30, 136, 229, 0.2);
      border-color: var(--accent-blue);
      color: var(--text-primary);
    }

    /* Cards and Containers */
    .element-container {
      background-color: var(--secondary-dark);
      border-radius: var(--border-radius);
      padding: 1rem;
      margin: 1rem 0;
      box-shadow: var(--box-shadow);
      border-left: 4px solid var(--accent-blue);
    }

    /* Spinner */
    .stSpinner > div {
      border-color: var(--accent-blue-light) transparent var(--accent-blue-light) transparent;
    }

    /* Markdown Content Styling */
    .stMarkdown strong {
      color: var(--text-primary);
      font-weight: 600;
    }

    .stMarkdown ul, .stMarkdown ol {
      padding-left: 1.5rem;
    }

    .stMarkdown li {
      margin-bottom: 0.5rem;
      color: var(--text-secondary);
    }

    /* Custom Scrollbar */
    ::-webkit-scrollbar {
      width: 8px;
      height: 8px;
    }

    ::-webkit-scrollbar-track {
      background: var(--primary-dark);
    }

    ::-webkit-scrollbar-thumb {
      background: var(--accent-blue);
      border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
      background: var(--accent-blue-light);
    }
    """
    
    st.markdown(f"""
    <style>
    {css}
    </style>
    """, unsafe_allow_html=True)

# Call the function to apply the CSS
apply_custom_css()

st.title("♻️ Recyclee E-Waste Assistant")
st.write("Ask me about buying recycled e-waste products, smartphones, and more!")

# Function to generate fake product data
def generate_fake_database(num_items=500):
    # Product templates
    categories = ["smartphone", "laptop", "tablet", "desktop", "monitor", "printer", 
                 "camera", "headphone", "speaker", "smartwatch", "gaming console"]
    
    brands = {
        "smartphone": ["Apple", "Samsung", "Xiaomi", "OnePlus", "Vivo", "Oppo", "Realme", "Motorola", "Google", "Nothing"],
        "laptop": ["Apple", "Dell", "HP", "Lenovo", "Asus", "Acer", "MSI", "Microsoft", "Samsung", "LG"],
        "tablet": ["Apple", "Samsung", "Lenovo", "Microsoft", "Xiaomi", "Huawei", "Amazon", "Google"],
        "desktop": ["Dell", "HP", "Lenovo", "Asus", "Acer", "Apple", "MSI", "Custom Built"],
        "monitor": ["Dell", "LG", "Samsung", "Asus", "BenQ", "Acer", "ViewSonic", "AOC", "MSI"],
        "printer": ["HP", "Canon", "Epson", "Brother", "Xerox", "Samsung", "Ricoh"],
        "camera": ["Canon", "Nikon", "Sony", "Fujifilm", "Panasonic", "Olympus", "GoPro"],
        "headphone": ["Sony", "Bose", "JBL", "Sennheiser", "Apple", "Samsung", "Skullcandy", "boAt", "Noise"],
        "speaker": ["JBL", "Sony", "Bose", "Harman Kardon", "Marshall", "boAt", "Ultimate Ears", "Anker"],
        "smartwatch": ["Apple", "Samsung", "Fitbit", "Garmin", "Fossil", "Amazfit", "Noise", "boAt"],
        "gaming console": ["Sony PlayStation", "Microsoft Xbox", "Nintendo"]
    }
    
    models = {
        "Apple": ["iPhone 13", "iPhone 12", "iPhone 11", "iPhone SE", "iPhone XR", "MacBook Air", "MacBook Pro", "iPad Pro", "iPad Air", "iPad Mini", "AirPods", "Apple Watch"],
        "Samsung": ["Galaxy S21", "Galaxy S20", "Galaxy A52", "Galaxy Note 20", "Galaxy Tab S7", "Galaxy Book", "Galaxy Watch"],
        "Xiaomi": ["Redmi Note 10", "Mi 11", "Poco X3", "Redmi 9", "Mi Pad 5"],
        "OnePlus": ["9 Pro", "9", "8T", "Nord", "7 Pro"],
        "Dell": ["XPS 13", "XPS 15", "Inspiron", "Latitude", "Alienware", "Precision"],
        "HP": ["Spectre", "Envy", "Pavilion", "EliteBook", "ProBook", "Omen"],
        "Lenovo": ["ThinkPad", "Yoga", "IdeaPad", "Legion", "Tab"],
        "Sony": ["WH-1000XM4", "WF-1000XM4", "PlayStation 5", "PlayStation 4", "α7 III", "RX100"],
        "Microsoft": ["Surface Pro", "Surface Laptop", "Surface Book", "Xbox Series X", "Xbox Series S"],
        "Google": ["Pixel 6", "Pixel 5", "Pixel 4a", "Nest Audio", "Nest Hub"]
    }
    
    # Fill in with generic models for brands not explicitly listed
    for brand_list in brands.values():
        for brand in brand_list:
            if brand not in models:
                models[brand] = [f"Model {i}" for i in range(1, 6)]
    
    conditions = ["Like New", "Excellent", "Very Good", "Good", "Fair"]
    warranty_periods = ["1 year", "6 months", "90 days", "30 days", "No warranty"]
    
    # Generate sustainability scores with some weighting toward better scores for refurbished items
    sustainability_scores = [f"{i}/10" for i in [5, 6, 6, 7, 7, 7, 8, 8, 9, 9]]
    
    # Generate product database
    products = []
    for _ in range(num_items):
        category = random.choice(categories)
        brand = random.choice(brands[category])
        
        # Get models specific to the brand or use generic if not found
        available_models = models.get(brand, [f"Model {i}" for i in range(1, 6)])
        model = random.choice(available_models)
        
        # For smartphones, tablets, laptops: add storage and other specs
        specs = ""
        if category in ["smartphone", "tablet", "laptop"]:
            storage = random.choice(["16GB", "32GB", "64GB", "128GB", "256GB", "512GB", "1TB"])
            ram = random.choice(["2GB", "3GB", "4GB", "6GB", "8GB", "12GB", "16GB", "32GB"])
            
            if category == "smartphone" or category == "tablet":
                specs = f"{ram} RAM, {storage} Storage"
            elif category == "laptop":
                processor = random.choice(["Intel i3", "Intel i5", "Intel i7", "Intel i9", "AMD Ryzen 3", "AMD Ryzen 5", "AMD Ryzen 7", "Apple M1", "Apple M2"])
                specs = f"{processor}, {ram} RAM, {storage} SSD"
        
        # Generate price based on category, brand prestige, and condition
        base_prices = {
            "smartphone": (5000, 120000),
            "laptop": (15000, 200000),
            "tablet": (8000, 100000),
            "desktop": (20000, 150000),
            "monitor": (5000, 50000),
            "printer": (3000, 35000),
            "camera": (5000, 150000),
            "headphone": (500, 30000),
            "speaker": (1000, 40000),
            "smartwatch": (2000, 50000),
            "gaming console": (15000, 70000)
        }
        
        # Brand prestige factor (higher for premium brands)
        brand_factor = 1.0
        premium_brands = ["Apple", "Samsung", "Sony", "Bose", "Microsoft"]
        if brand in premium_brands:
            brand_factor = 1.3
        
        # Condition factor (lower price for worse condition)
        condition = random.choice(conditions)
        condition_factor = {
            "Like New": 0.9,
            "Excellent": 0.8,
            "Very Good": 0.7,
            "Good": 0.6,
            "Fair": 0.5
        }[condition]
        
        min_price, max_price = base_prices[category]
        base_price = random.randint(min_price, max_price)
        final_price = int(base_price * brand_factor * condition_factor)
        
        # Round to nearest common pricing point
        if final_price > 10000:
            final_price = round(final_price / 1000) * 1000
        elif final_price > 1000:
            final_price = round(final_price / 500) * 500
        else:
            final_price = round(final_price / 100) * 100
        
        # Generate product info
        product = {
            "id": f"EWASTE-{random.randint(10000, 99999)}",
            "category": category,
            "name": f"{brand} {model}",
            "brand": brand,
            "model": model,
            "price": f"₹{final_price}",
            "condition": condition,
            "warranty": random.choice(warranty_periods),
            "sustainability_score": random.choice(sustainability_scores),
            "specifications": specs,
            "description": f"Refurbished {brand} {model} in {condition.lower()} condition. {specs}",
            "in_stock": random.choice([True, True, True, False])  # 75% chance in stock
        }
        products.append(product)
    
    # Generate recycling centers database
    recycling_centers = [
        {
            "name": "GreenTech Recyclers",
            "location": "Mumbai, Delhi, Bangalore, Chennai",
            "accepts": "All electronics, batteries, and accessories",
            "certification": "e-Stewards and R2 certified",
            "process": "Zero-landfill policy with responsible material recovery"
        },
        {
            "name": "EcoReturn India",
            "location": "Delhi, Pune, Hyderabad",
            "accepts": "Computers, phones, tablets, and peripherals",
            "certification": "R2 certified",
            "process": "Component harvesting and precious metal recovery"
        },
        {
            "name": "Attero Recycling",
            "location": "Nationwide service",
            "accepts": "All electronic waste",
            "certification": "ISO 9001, ISO 14001, OHSAS 18001",
            "process": "Clean technology for e-waste management"
        },
        {
            "name": "E-Waste Recyclers India",
            "location": "Multiple collection centers across major cities",
            "accepts": "All types of e-waste",
            "certification": "Government authorized",
            "process": "Scientific disposal with material recovery"
        },
        {
            "name": "Karo Sambhav",
            "location": "Pan-India presence",
            "accepts": "Electronics, batteries, packaging",
            "certification": "E-waste PRO",
            "process": "Producer responsibility organization for systematic collection"
        }
    ]
    
    # Recycling tips specific to India
    recycling_tips = [
        "Under E-Waste Management Rules in India, consumers should hand over e-waste to authorized recyclers only",
        "Many electronics manufacturers in India have take-back programs for their products",
        "Before recycling, ensure all personal data is completely wiped from devices",
        "Look for recyclers with proper authorization from State Pollution Control Boards",
        "Many cities have designated e-waste collection centers operated by municipal corporations",
        "Some retailers offer discounts when you exchange old electronics for new purchases",
        "Store e-waste separately from regular waste until proper disposal",
        "Remove batteries before recycling devices as they require specialized processing",
        "Consider donating working but unwanted electronics to schools or NGOs",
        "Participate in e-waste collection drives organized in your community",
        "When buying refurbished, check for certification and proper testing documentation",
        "Mobile phone retailers often collect old phones for recycling or refurbishment"
    ]
    
    # Environmental impact data
    environmental_impact = {
        "smartphone_production": "Producing one smartphone generates approximately 60kg of CO2",
        "e_waste_facts": "India generates approximately 3.2 million tonnes of e-waste annually",
        "raw_materials": "Recycling one million mobile phones can recover 24 kg of gold, 250 kg of silver, and 9 kg of palladium",
        "water_usage": "Manufacturing a single computer and monitor uses about 1,500 gallons of water",
        "landfill_issues": "E-waste in landfills can leach toxic chemicals like lead, mercury, and cadmium into soil and groundwater",
        "energy_savings": "Refurbishing a laptop uses 85% less energy than manufacturing a new one",
        "india_specific": "Less than 5% of India's e-waste is recycled through the formal sector"
    }
    
    # Organize data by category for easy lookup
    products_by_category = {}
    for product in products:
        category = product["category"]
        if category not in products_by_category:
            products_by_category[category] = []
        products_by_category[category].append(product)
    
    products_by_brand = {}
    for product in products:
        brand = product["brand"]
        if brand not in products_by_brand:
            products_by_brand[brand] = []
        products_by_brand[brand].append(product)
    
    # Complete database structure
    database = {
        "products": products,
        "products_by_category": products_by_category,
        "products_by_brand": products_by_brand,
        "recycling_centers": recycling_centers,
        "recycling_tips": recycling_tips,
        "environmental_impact": environmental_impact
    }
    
    return database

# Generate the database with 500 items
EWASTE_DB = generate_fake_database(500)

# Function to search the internal database based on keywords
def search_internal_db(query):
    query_lower = query.lower()
    results = []
    
    # Extract key terms from query
    query_terms = query_lower.split()
    
    # Check for category mentions
    mentioned_categories = []
    for category in EWASTE_DB["products_by_category"].keys():
        if category in query_lower or category + "s" in query_lower:
            mentioned_categories.append(category)
    
    # Check for brand mentions
    mentioned_brands = []
    for brand in EWASTE_DB["products_by_brand"].keys():
        if brand.lower() in query_lower:
            mentioned_brands.append(brand)
    
    # Check for price range mentions
    price_range = None
    if "under" in query_lower and "₹" in query_lower or "rs" in query_lower:
        # Extract price with regex
        import re
        price_matches = re.findall(r'under ₹?(\d+,?\d*)', query_lower)
        if not price_matches:
            price_matches = re.findall(r'under rs\.? ?(\d+,?\d*)', query_lower)
        
        if price_matches:
            try:
                max_price = int(price_matches[0].replace(',', ''))
                price_range = (0, max_price)
            except ValueError:
                pass
    
    # Function to extract numerical price from string format "₹12,345"
    def extract_price(price_str):
        try:
            return int(price_str.replace('₹', '').replace(',', ''))
        except:
            return 0
    
    # Search for products based on filters
    matching_products = []
    
    # If specific categories or brands mentioned, filter by those
    if mentioned_categories or mentioned_brands:
        if mentioned_categories:
            for category in mentioned_categories:
                matching_products.extend(EWASTE_DB["products_by_category"].get(category, []))
        
        if mentioned_brands:
            for brand in mentioned_brands:
                matching_products.extend(EWASTE_DB["products_by_brand"].get(brand, []))
    else:
        # If no specific category/brand filters, include all products
        matching_products = EWASTE_DB["products"]
    
    # Apply price filter if applicable
    if price_range:
        matching_products = [p for p in matching_products if extract_price(p["price"]) <= price_range[1]]
    
    # Limit to 10 most relevant products
    if matching_products:
        matching_products = matching_products[:10]
        results.append("### Relevant Products:")
        for product in matching_products:
            results.append(f"- **{product['name']}** - {product['price']} - {product['condition']} - {product['warranty']} warranty - Sustainability: {product['sustainability_score']}")
            if product.get("specifications"):
                results.append(f"  *{product['specifications']}*")
    
    # Include relevant recycling centers if query is about recycling
    if "recycl" in query_lower or "dispos" in query_lower or "e-waste" in query_lower:
        results.append("\n### Nearby Recycling Centers:")
        for center in EWASTE_DB["recycling_centers"]:
            results.append(f"- **{center['name']}** - {center['location']}")
            results.append(f"  Accepts: {center['accepts']}")
            results.append(f"  Certification: {center['certification']}")
    
    # Include recycling tips if appropriate
    if "tip" in query_lower or "how to" in query_lower or "advice" in query_lower:
        results.append("\n### Recycling Tips:")
        relevant_tips = EWASTE_DB["recycling_tips"][:5]  # Limit to 5 tips
        for tip in relevant_tips:
            results.append(f"- {tip}")
    
    # Include environmental impact information if asked
    if "environment" in query_lower or "impact" in query_lower or "sustain" in query_lower:
        results.append("\n### Environmental Impact Facts:")
        for key, fact in EWASTE_DB["environmental_impact"].items():
            results.append(f"- {fact}")
    
    return "\n".join(results) if results else "No relevant information found in our database. Let me search external sources."

# Prompt template
prompt = ChatPromptTemplate.from_template("""
You are an expert on e-waste recycling and electronics, specializing in the Indian market.

User asked: {query}

Based on the context below (from our database and web search), help the user with budget-friendly recycled products, refurbished devices, or e-waste recycling tips relevant to India.

Internal Database Results:
{db_results}

Web Search Results:
{web_results}

Answer in a helpful, non-hallucinating way. Focus on providing practical advice relevant to the Indian context, with prices in Indian Rupees (₹). If recommending products, prioritize environmentally sustainable options. Always suggest proper e-waste disposal methods according to Indian regulations.
""")

# Setup LLaMA 3 model with error handling
try:
    llm = Ollama(model="llama3.2:3b", temperature=0.2)  
except Exception as e:
    st.warning(f"Failed to load Ollama model: {str(e)}. Using a simpler model instead.")
    try:
        llm = Ollama(model="mistral", temperature=0.2)  # Try mistral as fallback
    except Exception as e:
        st.error(f"Failed to load any Ollama model: {str(e)}. The application will continue with limited functionality.")
        llm = None

# Web search tool (Tavily) with error handling
try:
    search = TavilySearchResults(tavily_api_key="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", k=3)
except Exception as e:
    st.warning(f"Failed to initialize Tavily search: {str(e)}. Web search functionality will be limited.")
    search = None

# Function to get context from web with error handling
def get_web_results(query):
    if search is None:
        return "Web search is currently unavailable. Using internal database information only."
    
    try:
        return search.invoke({"query": f"{query} e-waste recycling India refurbished electronics"})
    except Exception as e:
        return f"Error retrieving web results: {str(e)}\n\nProceeding with internal database information only."

# Function to combine both sources with error handling
def get_context(input_query):
    db_results = search_internal_db(input_query)
    web_results = get_web_results(input_query)
    
    return {
        "query": input_query,
        "db_results": db_results,
        "web_results": web_results
    }

# Define RAG Chain with error handling
if llm is not None:
    chain = (
        RunnableLambda(get_context)
        | prompt
        | llm
        | StrOutputParser()
    )
else:
    # Fallback chain without LLM
    chain = RunnableLambda(lambda x: f"Internal database results:\n{search_internal_db(x)}")

# Chat Interface
user_query = st.text_input("🔍 Type your question here (e.g., 'Find me a refurbished smartphone under ₹15,000')")

if user_query:
    with st.spinner("Searching and thinking... 🤖"):
        try:
            response = chain.invoke(user_query)
            st.markdown("### 📦 Response")
            st.write(response)
        except Exception as e:
            st.error(f"Error processing your query: {str(e)}")
            st.info("Here are some relevant products from our database:")
            st.write(search_internal_db(user_query))
    
    # Add additional UI elements for better experience
    st.markdown("---")
    st.markdown("### 🔍 Explore Categories")
    cols = st.columns(4)
    categories = list(EWASTE_DB["products_by_category"].keys())
    
    for i, col in enumerate(cols):
        for j in range(i, len(categories), 4):
            if j < len(categories):
                col.button(f"📱 {categories[j].title()}", key=f"cat_{j}")