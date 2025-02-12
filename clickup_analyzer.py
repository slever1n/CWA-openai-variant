import requests
import streamlit as st
import time
import openai
import textwrap
import concurrent.futures
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

# Set page title and icon
st.set_page_config(page_title="ClickUp Workspace Analysis", page_icon="🚀", layout="wide")

# Retrieve API keys from Streamlit secrets
openai_api_key = st.secrets.get("OPENAI_API_KEY")
openai_org_id = st.secrets.get("OPENAI_ORG_ID")

# Configure OpenAI if API keys are available
if openai_api_key:
    openai.organization = openai_org_id
    openai.api_key = openai_api_key

def get_company_info(company_name):
    if not company_name:
        return "No company information provided."
    
    prompt = textwrap.dedent(f"""
        Please build a short company profile for {company_name}. The profile should include:
        - **Mission:** A brief mission statement.
        - **Key Features:** List 3-5 key features.
        - **Values:** Describe the core values.
        - **Target Audience:** Describe the target audience.
        - **Overall Summary:** Provide an overview.
    """)
    
    try:
        if openai_api_key:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        else:
            return "No AI service available for generating company profile."
    except Exception as e:
        logging.error(f"Error fetching company details: {str(e)}")
        return f"Error: {str(e)}"

def fetch_workspaces(api_key):
    url = "https://api.clickup.com/api/v2/team"
    headers = {"Authorization": api_key}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            teams = response.json().get("teams", [])
            return {team["id"]: team["name"] for team in teams}
        else:
            return None
    except Exception as e:
        logging.error(f"Exception: {str(e)}")
        return None

def fetch_workspace_details(api_key, team_id):
    headers = {"Authorization": api_key}
    spaces_url = f"https://api.clickup.com/api/v2/team/{team_id}/space"
    
    try:
        spaces_response = make_api_call(spaces_url, headers)
        spaces = spaces_response.get("spaces", [])
        
        return {"Spaces": len(spaces)}
    except Exception as e:
        logging.error(f"Exception: {str(e)}")
        return {"error": f"Exception: {str(e)}"}

def make_api_call(url, headers):
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            logging.error(f"Error {response.status_code}: {response.text}")
            return {}
    except Exception as e:
        logging.error(f"Exception: {str(e)}")
        return {}

st.title("🚀 ClickUp Workspace Analysis")

api_key = st.text_input("Enter ClickUp API Key:", type="password")
if api_key:
    workspaces = fetch_workspaces(api_key)
    if workspaces:
        workspace_id = st.selectbox("Select Workspace:", options=list(workspaces.keys()), format_func=lambda x: workspaces[x])
    else:
        st.error("Failed to fetch workspaces. Check API key.")
else:
    workspace_id = None

company_name = st.text_input("Enter Company Name (Optional):")
use_case = st.text_area("Describe your company's use case:")

if st.button("Analyze"):
    if api_key and workspace_id:
        workspace_data = fetch_workspace_details(api_key, workspace_id)
        if "error" in workspace_data:
            st.error(workspace_data["error"])
        else:
            st.subheader("Workspace Summary")
            for key, value in workspace_data.items():
                st.metric(label=key, value=value)
    
    if company_name:
        company_profile = get_company_info(company_name)
        st.subheader("Company Profile")
        st.markdown(company_profile, unsafe_allow_html=True)

st.markdown("<div style='position: fixed; bottom: 10px; left: 10px; font-size: 12px; color: orange;'>Built by: Yul 😊</div>", unsafe_allow_html=True)
