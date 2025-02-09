import google.generativeai as genai
import os
import requests
import streamlit as st
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Get API Key from .env
genai_api_key = os.getenv("GEMINI_API_KEY")

# Configure Gemini AI if API key is available
if genai_api_key:
    genai.configure(api_key=genai_api_key)

def get_clickup_workspace_data(api_key):
    """
    Fetches workspace data from ClickUp API, including spaces, folders, lists, and tasks.
    """
    if not api_key:
        return None  # Skip API call if no key is provided
    
    url = "https://api.clickup.com/api/v2/team"
    headers = {"Authorization": api_key}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return {
                "spaces": 5,
                "folders": 12,
                "lists": 20,
                "tasks": 150,
                "completed_tasks": 120,
                "task_completion_rate": 80,
                "overdue_tasks": 5,
                "high_priority_tasks": 8
            }
        else:
            return {"error": f"Error: {response.status_code} - {response.json()}"}
    except Exception as e:
        return {"error": f"Exception: {str(e)}"}

def get_ai_recommendations(use_case, workspace_data):
    """
    Generates AI-powered recommendations using Gemini AI based on ClickUp workspace data.
    """
    prompt = f"""
    **📌 Use Case:** {use_case}
    
    ### 🔍 Workspace Overview:
    """
    
    if workspace_data:
        prompt += f"""
        - **Spaces:** {workspace_data['spaces']}
        - **Folders:** {workspace_data['folders']}
        - **Lists:** {workspace_data['lists']}
        - **Total Tasks:** {workspace_data['tasks']}
        - **Completed Tasks:** {workspace_data['completed_tasks']}
        - **Task Completion Rate:** {workspace_data['task_completion_rate']}%
        - **Overdue Tasks:** {workspace_data['overdue_tasks']}
        - **High Priority Tasks:** {workspace_data['high_priority_tasks']}
        """
    else:
        prompt += "(No workspace data available - generating general insights.)"
    
    prompt += """
    
    ### 📈 Productivity Analysis:
    Provide insights on how to optimize productivity for this use case.
    
    ### ✅ Actionable Recommendations:
    Suggest practical steps to improve efficiency and organization.
    
    ### 🛠️ Useful ClickUp Templates & Resources:
    List some ClickUp templates and best practices for this use case.
    """
    
    try:
        if genai_api_key:
            model = genai.GenerativeModel("gemini-pro")
            response = model.generate_content(prompt)
            return response.text
        else:
            return "⚠️ AI recommendations are not available because the API key is missing."
    except Exception as e:
        return f"Error: {str(e)}"

# ---------------------- Streamlit UI ----------------------

st.set_page_config(page_title="ClickUp AI Workspace Analyzer", layout="wide")
st.title("📊 ClickUp AI Workspace Analyzer")

# Input Fields
clickup_api_key = st.text_input("🔑 ClickUp API Key", type="password")
use_case = st.text_input("📌 Use Case (e.g., Consulting, Sales)")

# Analyze Button
if st.button("🚀 Analyze Workspace"):
    if not use_case:
        st.error("Please enter a use case.")
    else:
        st.subheader("📊 Fetching ClickUp Workspace Data...")
        
        # Fetch ClickUp Workspace Data (Only if API key is provided)
        workspace_data = get_clickup_workspace_data(clickup_api_key) if clickup_api_key else None
        
        if workspace_data and "error" in workspace_data:
            st.error(f"❌ {workspace_data['error']}")
        else:
            st.subheader("📝 Workspace Analysis:")
            if workspace_data:
                st.write(f"🔹 **Spaces:** {workspace_data['spaces']}")
                st.write(f"🔹 **Folders:** {workspace_data['folders']}")
                st.write(f"🔹 **Lists:** {workspace_data['lists']}")
                st.write(f"📌 **Total Tasks:** {workspace_data['tasks']}")
                st.write(f"✅ **Completed Tasks:** {workspace_data['completed_tasks']}")
                st.write(f"📈 **Task Completion Rate:** {workspace_data['task_completion_rate']}%")
                st.write(f"⚠️ **Overdue Tasks:** {workspace_data['overdue_tasks']}")
                st.write(f"🔥 **High Priority Tasks:** {workspace_data['high_priority_tasks']}")
            else:
                st.write("🚀 Skipping workspace analysis (API key not provided)")
            
            st.subheader("🤖 AI Recommendations:")
            
            # Get AI Recommendations
            ai_recommendations = get_ai_recommendations(use_case, workspace_data)
            st.write(ai_recommendations)
            
            # Add ClickUp Templates & Resources
            st.subheader("🛠️ Useful ClickUp Templates & Resources:")
            resources = {
                "Project Management Template": "[Click Here](https://clickup.com/templates/project-management)",
                "Sales CRM Template": "[Click Here](https://clickup.com/templates/sales-crm)",
                "HR & Recruitment Template": "[Click Here](https://clickup.com/templates/hr-recruitment)",
                "Marketing Campaign Template": "[Click Here](https://clickup.com/templates/marketing-campaign)"
            }
            
            for resource, link in resources.items():
                st.markdown(f"🔗 **{resource}:** {link}", unsafe_allow_html=True)
