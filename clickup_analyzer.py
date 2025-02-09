import google.generativeai as genai
import os
import requests
import streamlit as st
import time
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
    Fetches real workspace data from ClickUp API, including spaces, folders, lists, and tasks.
    """
    if not api_key:
        return None  # Skip API call if no key is provided
    
    url = "https://api.clickup.com/api/v2/team"
    headers = {"Authorization": api_key}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            teams = response.json().get("teams", [])
            if teams:
                team_id = teams[0]["id"]
                return fetch_workspace_details(api_key, team_id)
            else:
                return {"error": "No teams found in ClickUp workspace."}
        else:
            return {"error": f"Error: {response.status_code} - {response.json()}"}
    except Exception as e:
        return {"error": f"Exception: {str(e)}"}

def fetch_workspace_details(api_key, team_id):
    """Fetches workspace details including spaces, folders, lists, and tasks."""
    headers = {"Authorization": api_key}
    
    try:
        # Get spaces
        spaces_url = f"https://api.clickup.com/api/v2/team/{team_id}/space"
        spaces_response = requests.get(spaces_url, headers=headers).json()
        spaces = spaces_response.get("spaces", [])
        
        space_count = len(spaces)
        folder_count, list_count, task_count, completed_tasks, overdue_tasks, high_priority_tasks = 0, 0, 0, 0, 0, 0
        
        for space in spaces:
            space_id = space["id"]
            
            # Get folders
            folders_url = f"https://api.clickup.com/api/v2/space/{space_id}/folder"
            folders_response = requests.get(folders_url, headers=headers).json()
            folders = folders_response.get("folders", [])
            folder_count += len(folders)
            
            for folder in folders:
                folder_id = folder["id"]
                
                # Get lists
                lists_url = f"https://api.clickup.com/api/v2/folder/{folder_id}/list"
                lists_response = requests.get(lists_url, headers=headers).json()
                lists = lists_response.get("lists", [])
                list_count += len(lists)
                
                for lst in lists:
                    list_id = lst["id"]
                    
                    # Get tasks
                    tasks_url = f"https://api.clickup.com/api/v2/list/{list_id}/task"
                    tasks_response = requests.get(tasks_url, headers=headers).json()
                    tasks = tasks_response.get("tasks", [])
                    
                    task_count += len(tasks)
                    completed_tasks += sum(1 for task in tasks if task.get("status", "") == "complete")
                    overdue_tasks += sum(1 for task in tasks if task.get("due_date") and int(task["due_date"]) < int(time.time() * 1000))
                    high_priority_tasks += sum(1 for task in tasks if task.get("priority", "") in ["urgent", "high"])
        
        task_completion_rate = (completed_tasks / task_count * 100) if task_count > 0 else 0
        
        return {
            "spaces": space_count,
            "folders": folder_count,
            "lists": list_count,
            "tasks": task_count,
            "completed_tasks": completed_tasks,
            "task_completion_rate": round(task_completion_rate, 2),
            "overdue_tasks": overdue_tasks,
            "high_priority_tasks": high_priority_tasks
        }
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

st.set_page_config(page_title="ClickUp AI Workspace Analyzer", layout="wide")
st.title("📊 ClickUp AI Workspace Analyzer")

clickup_api_key = st.text_input("🔑 ClickUp API Key", type="password")
use_case = st.text_input("📌 Use Case (e.g., Consulting, Sales)")

if st.button("🚀 Analyze Workspace"):
    if not use_case:
        st.error("Please enter a use case.")
    else:
        st.subheader("📊 Fetching ClickUp Workspace Data...")
        workspace_data = get_clickup_workspace_data(clickup_api_key) if clickup_api_key else None
        
        if workspace_data and "error" in workspace_data:
            st.error(f"❌ {workspace_data['error']}")
        else:
            st.subheader("📝 Workspace Analysis:")
            cols = st.columns(4)
            keys = list(workspace_data.keys())
            
            for i, key in enumerate(keys):
                with cols[i % 4]:
                    st.metric(label=key.replace("_", " ").title(), value=workspace_data[key])
            
            st.subheader("🤖 AI Recommendations:")
            st.write(get_ai_recommendations(use_case, workspace_data))
            
            st.subheader("🛠️ Useful ClickUp Templates & Resources:")
            resources = {
                "[Project Management Template](https://clickup.com/templates/project-management)": "Project Management",
                "[Sales CRM Template](https://clickup.com/templates/sales-crm)": "Sales CRM",
                "[HR & Recruitment Template](https://clickup.com/templates/hr-recruitment)": "HR & Recruitment",
                "[Marketing Campaign Template](https://clickup.com/templates/marketing-campaign)": "Marketing Campaign"
            }
            for link, label in resources.items():
                st.markdown(f"🔗 {link}", unsafe_allow_html=True)
