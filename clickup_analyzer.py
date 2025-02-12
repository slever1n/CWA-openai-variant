import streamlit as st
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Streamlit UI
st.set_page_config(page_title="ClickUp Workspace Analyzer", layout="wide")
st.title("🚀 ClickUp Workspace Analyzer")
st.markdown("Get insights and recommendations based on your ClickUp workspace!")

# --- User Inputs ---
clickup_api_key = st.text_input("🔑 Enter your ClickUp API Key:", type="password")
company_name = st.text_input("🏢 Enter your Company Name:")
use_case = st.text_area("🎯 Describe Your Use Case:")

# Function to get workspace details from ClickUp API
def get_workspace_details(api_key):
    url = "https://api.clickup.com/api/v2/team"
    headers = {"Authorization": api_key}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            teams = response.json().get("teams", [])
            return teams if teams else "No teams found."
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        logging.error(f"ClickUp API error: {str(e)}")
        return "Error fetching workspace details."

# Function to generate company profile using DeepSeek API
def get_company_info(company_name):
    if not company_name:
        return "No company information provided."
    
    prompt = f"""
    Please build a short company profile for {company_name}. The profile should include:
    - **Mission**
    - **Key Features**
    - **Values**
    - **Target Audience**
    - **Overall Summary**
    """
    
    api_url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {st.secrets.get('DEEPSEEK_API_KEY')}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}]
    }
    
    try:
        response = requests.post(api_url, headers=headers, json=data)
        response_json = response.json()
        return response_json.get("choices", [{}])[0].get("message", {}).get("content", "No response.")
    except Exception as e:
        logging.error(f"Error fetching company details: {str(e)}")
        return f"Error: {str(e)}"

# Function to generate AI-based recommendations
def get_ai_recommendations(use_case, company_profile, workspace_details):
    prompt = f"""
    Analyze the following workspace data:
    {workspace_details}
    
    Company use case: "{use_case}"
    Company profile: {company_profile}
    
    Provide:
    - 📈 Productivity Analysis
    - ✅ Actionable Recommendations
    - 🏆 Best Practices & Tips
    - 🛠️ Useful ClickUp Templates & Resources
    """
    
    api_url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {st.secrets.get('DEEPSEEK_API_KEY')}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}]
    }
    
    try:
        response = requests.post(api_url, headers=headers, json=data)
        response_json = response.json()
        return response_json.get("choices", [{}])[0].get("message", {}).get("content", "No response.")
    except Exception as e:
        logging.error(f"Error generating AI recommendations: {str(e)}")
        return f"⚠️ AI recommendations are not available: {str(e)}"

# Run Analysis
if st.button("🔍 Analyze Workspace"):
    if clickup_api_key and company_name and use_case:
        with st.spinner("Fetching workspace details..."):
            workspace_details = get_workspace_details(clickup_api_key)
        
        with st.spinner("Generating company profile..."):
            company_profile = get_company_info(company_name)
        
        with st.spinner("Generating AI recommendations..."):
            recommendations = get_ai_recommendations(use_case, company_profile, workspace_details)
        
        st.subheader("📊 ClickUp Workspace Details:")
        st.json(workspace_details)
        
        st.subheader("🏢 Company Profile:")
        st.write(company_profile)
        
        st.subheader("🤖 AI-Powered Recommendations:")
        st.write(recommendations)
    else:
        st.warning("Please fill in all fields before analyzing!")
