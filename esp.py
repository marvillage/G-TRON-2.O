import streamlit as st
import pandas as pd
import pickle
import random
from textblob import TextBlob
import spacy
from collections import Counter
import re

# Configure page
st.set_page_config(page_title="ESG Analytics Dashboard", layout="wide")

# Load NLP models with progress indicators
@st.cache_resource
def load_nlp_models():
    with st.spinner("Loading NLP models..."):
        try:
            nlp = spacy.load("en_core_web_sm")
            return nlp
        except Exception as e:
            st.error(f"Error loading NLP models: {str(e)}")
            return None

# Load models
nlp = load_nlp_models()

# Load trained model
with open("esg_model.pkl", "rb") as f:
    model, label_encoder = pickle.load(f)

def extract_keywords(text, n_keywords=5):
    """Extract key terms from text using NLP"""
    if nlp is None:
        return []
    
    try:
        doc = nlp(text)
        # Filter for nouns, proper nouns, and adjectives
        keywords = [token.text for token in doc if token.pos_ in ["NOUN", "PROPN", "ADJ"] 
                   and not token.is_stop and len(token.text) > 2]
        # Count and get most common
        keyword_counts = Counter(keywords)
        return [word for word, _ in keyword_counts.most_common(n_keywords)]
    except Exception as e:
        st.warning(f"Keyword extraction failed: {str(e)}")
        return []

def analyze_sentiment(text):
    """Analyze sentiment of text using TextBlob"""
    try:
        # Using TextBlob for polarity and subjectivity
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        
        # Determine sentiment category
        if polarity > 0.3:
            return "Very Positive", "🟢", subjectivity
        elif polarity > 0:
            return "Slightly Positive", "🟡", subjectivity
        elif polarity < -0.3:
            return "Very Negative", "🔴", subjectivity
        elif polarity < 0:
            return "Slightly Negative", "🟠", subjectivity
        else:
            return "Neutral", "⚪", subjectivity
    except Exception as e:
        st.warning(f"Sentiment analysis failed: {str(e)}")
        return "Unknown", "⚪", 0.0

def generate_summary(text):
    """Generate a summary using spaCy"""
    if nlp is None:
        return text
    
    try:
        doc = nlp(text)
        # Get the most important sentences based on word importance
        sentences = [sent for sent in doc.sents]
        if len(sentences) <= 2:
            return text
            
        # Calculate sentence importance based on word importance
        sentence_importance = []
        for sent in sentences:
            importance = sum([token.prob for token in sent if not token.is_stop])
            sentence_importance.append((sent, importance))
        
        # Get top 2-3 most important sentences
        sentence_importance.sort(key=lambda x: x[1], reverse=True)
        summary_sents = [str(sent[0]) for sent in sentence_importance[:2]]
        return " ".join(summary_sents)
    except Exception as e:
        st.warning(f"Summary generation failed: {str(e)}")
        return text

def analyze_esg_metrics(data):
    """Analyze ESG metrics and provide insights"""
    insights = []
    
    # Analyze environmental metrics
    if data["Renewable Energy Use (%)"] > 75:
        insights.append("🌟 **Strong renewable energy adoption**")
    elif data["Renewable Energy Use (%)"] < 25:
        insights.append("⚠️ **Low renewable energy usage**")
    
    if data["Waste Recycled (%)"] > 70:
        insights.append("♻️ **Excellent waste management**")
    elif data["Waste Recycled (%)"] < 30:
        insights.append("⚠️ **Poor waste recycling rate**")
    
    # Analyze social metrics
    if data["Board Diversity (%)"] > 40:
        insights.append("👥 **Strong board diversity**")
    elif data["Board Diversity (%)"] < 20:
        insights.append("⚠️ **Limited board diversity**")
    
    if data["Employee Satisfaction (%)"] > 75:
        insights.append("😊 **High employee satisfaction**")
    elif data["Employee Satisfaction (%)"] < 50:
        insights.append("⚠️ **Low employee satisfaction**")
    
    return insights

def generate_esg_report(data):
    """Generate a detailed ESG sustainability report with NLP enhancements"""
    # Extract data
    company = data["Company Name"]
    industry = data["Industry"]
    country = data["Country"]
    esg_score = data["ESG Score"]
    compliance = data["Compliance Status"]
    energy_usage = data["Energy Usage (MWh)"]
    carbon_emissions = data["CO₂ Emissions (tons)"]
    renewable_energy = data["Renewable Energy Use (%)"]
    waste_recycling = data["Waste Recycled (%)"]
    water_consumption = data["Water Consumption (Million Liters)"]
    regulatory_fines = data["Environmental Fines (USD)"]
    board_diversity = data["Board Diversity (%)"]
    employee_satisfaction = data["Employee Satisfaction (%)"]
    social_responsibility = data["Social Responsibility Score"]

    # Generate base report
    base_report = (
        f"📄 **ESG Report for {company} ({industry}, {country})**\n\n"
        f"{company} has an ESG score of {esg_score}, categorizing it as {compliance}. "
        f"The company consumes {energy_usage} MWh of energy, with carbon emissions of {carbon_emissions} tons. "
        f"Renewable energy accounts for {renewable_energy}% of its energy use, while {waste_recycling}% of waste is recycled. "
        f"Water consumption stands at {water_consumption} million liters. "
        f"Board diversity is {board_diversity}% with an employee satisfaction rate of {employee_satisfaction}%. "
        f"Social responsibility score is {social_responsibility}. "
        f"{'No significant regulatory fines have been reported.' if regulatory_fines == 0 else f'Regulatory fines have amounted to Rs{regulatory_fines}.'}"
    )

    # Get ESG insights
    insights = analyze_esg_metrics(data)
    
    # Add NLP enhancements
    try:
        # Extract keywords
        keywords = extract_keywords(base_report)
        
        # Analyze sentiment
        sentiment, sentiment_emoji, subjectivity = analyze_sentiment(base_report)
        
        # Generate summary
        summary = generate_summary(base_report)
        
        # Enhanced report with NLP insights
        enhanced_report = (
            f"{base_report}\n\n"
            f"### 🔍 ESG Performance Analysis\n"
            + "\n".join(insights) + "\n\n"
            f"### 📊 NLP Analysis\n"
           
           
            f"- **Key Terms**: {', '.join(keywords)}\n"
            f"- **Summary**: {summary}\n"
        )
        
        return enhanced_report
    except Exception as e:
        st.warning(f"NLP enhancements failed: {str(e)}")
        return base_report

def analyze_compliance_text(text):
    """Analyze compliance-related text for key insights"""
    try:
        # Extract named entities
        doc = nlp(text)
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        
        # Find compliance-related terms
        compliance_terms = [
            "compliance", "regulation", "standard", "requirement", 
            "policy", "guideline", "certification", "audit"
        ]
        
        found_terms = [term for term in compliance_terms if term in text.lower()]
        
        return {
            "entities": entities,
            "compliance_terms": found_terms
        }
    except Exception as e:
        st.warning(f"Compliance text analysis failed: {str(e)}")
        return {"entities": [], "compliance_terms": []}

# Streamlit UI
st.title("🌍 ESG Compliance Prediction & Report Generator")
st.write("Upload your ESG data to generate AI-enhanced sustainability reports and compliance predictions.")

# Upload CSV file
uploaded_file = st.file_uploader("Upload ESG Data (CSV)", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    
    # Show data overview
   

    # Predict Compliance
    if st.button("🎯 Predict ESG Compliance"):
        with st.spinner("Analyzing compliance..."):
            X = df.drop(columns=["Company Name", "Industry", "Country", "Compliance Status", "Sustainability Initiatives"])
            predictions = model.predict(X)
            df["Predicted Compliance"] = label_encoder.inverse_transform(predictions)
            
            st.write("### 📋 ESG Compliance Predictions with Analysis")
            
            # Create columns for metrics
            total = len(df)
            compliant = sum(df["Predicted Compliance"] == "Compliant")
            non_compliant = total - compliant
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Companies", total)
            col2.metric("Compliant", compliant, f"{(compliant/total)*100:.1f}%")
            col3.metric("Non-Compliant", non_compliant, f"{(non_compliant/total)*100:.1f}%")
            
            # Show detailed analysis
            for _, row in df.iterrows():
                with st.expander(f"🏢 {row['Company Name']} - {row['Predicted Compliance']}"):
                    st.write(f"**Industry**: {row['Industry']}")
                    st.write(f"**Country**: {row['Country']}")
                    st.write(f"**ESG Score**: {row['ESG Score']}")
                    
                    # Add sentiment analysis for company description
                    if 'Sustainability Initiatives' in row:
                        sentiment, emoji, subjectivity = analyze_sentiment(row['Sustainability Initiatives'])
                        st.write(f"**Sustainability Sentiment**: {sentiment} {emoji}")
                       

    # Generate Reports
    if st.button("📝 Generate ESG Reports"):
        with st.spinner("Generating AI-enhanced ESG reports..."):
            df["Generated ESG Report"] = df.apply(generate_esg_report, axis=1)
            
            st.write("### 📊 Generated ESG Reports with AI Analysis")
            
            for _, row in df.iterrows():
                with st.expander(f"📄 ESG Report for {row['Company Name']}"):
                    st.markdown(row["Generated ESG Report"])
                    
                    # Add sustainability initiatives analysis if available
                    if 'Sustainability Initiatives' in row and row['Sustainability Initiatives']:
                        st.write("\n### 🌱 Sustainability Initiatives Analysis")
                        initiatives = row['Sustainability Initiatives']
                        
                        # Sentiment analysis
                        sentiment, emoji, subjectivity = analyze_sentiment(initiatives)
                        st.write(f"**Initiative Sentiment**: {sentiment} {emoji}")
                     
                        
                        # Key terms
                        keywords = extract_keywords(initiatives)
                        if keywords:
                            st.write("**Key Focus Areas**:", ", ".join(keywords))
                        
                        # Generate summary
                        if len(initiatives.split()) > 30:
                            summary = generate_summary(initiatives)
                            st.write("**Summary**:", summary)
