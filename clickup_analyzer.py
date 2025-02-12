import requests
import streamlit as st
import time
import openai
import textwrap
import concurrent.futures
import logging
from openai import OpenAI



# Set up logging
logging.basicConfig(level=logging.INFO)

# Set page title and icon
st.set_page_config(page_title="ClickUp Workspace Analysis", page_icon="🚀", layout="wide")

# Retrieve API keys from Streamlit secrets
openai_api_key = st.secrets.get("OPENAI_API_KEY")
openai_org_id = st.secrets.get("OPENAI_ORG_ID")
deepseek_api_key = st.secrets.get("DEEPSEEK_API_KEY")

# Configure OpenAI if API keys are available
if openai_api_key:
    openai.organization = openai_org_id
    openai.api_key = openai_api_key

def get_company_info(company_name):
    """
    Generates a short company profile for the given company name using OpenAI.
    """
    if not company_name:
        return "No company information provided."
    
    prompt = textwrap.dedent(f"""
        Please build a short company profile for {company_name}. The profile should include the following sections in markdown:
        - **Mission:** A brief mission statement.
        - **Key Features:** List 3-5 key features of the company.
        - **Values:** Describe the core values of the company.
        - **Target Audience:** Describe who the company primarily serves.
        - **Overall Summary:** Provide an overall summary of what the company does.
    """)
    
    try:

if client = OpenAI(api_key="sk-2984c908d77a45e2aa3c776d6190be4c", base_url="https://api.deepseek.com")

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Hello"},
    ],
    stream=False
)

print(response.choices[0].message.content)
        else:
            return "No AI service available for generating company profile."
    except Exception as e:
        logging.error(f"Error fetching company details: {str(e)}")
        return f"Error fetching company details: {str(e)}"

def fetch_workspaces(api_key):
    """
    Fetches the list of workspaces from the ClickUp API.
    """
    url = "https://api.clickup.com/api/v2/team"
    headers = {"Authorization": api_key}

    try:
        start_time = time.time()
        response = requests.get(url, headers=headers)
        logging.info(f"API call to {url} took {time.time() - start_time:.2f} seconds")
        if response.status_code == 200:
            teams = response.json().get("teams", [])
            return {team["id"]: team["name"] for team in teams}
        else:
            return None
    except Exception as e:
        logging.error(f"Exception: {str(e)}")
        return None

def fetch_workspace_details(api_key, team_id):
    """
    Fetches workspace details including spaces, folders, lists, and tasks.
    """
    headers = {"Authorization": api_key}
    
    try:
        spaces_url = f"https://api.clickup.com/api/v2/team/{team_id}/space"
        spaces_response = make_api_call(spaces_url, headers)
        spaces = spaces_response.get("spaces", [])
        
        workspace_metrics = {
            "space_count": len(spaces),
            "folder_count": 0,
            "list_count": 0,
            "task_count": 0,
            "completed_tasks": 0,
            "overdue_tasks": 0,
            "high_priority_tasks": 0
        }

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_space = {executor.submit(fetch_space_details, api_key, space["id"]): space for space in spaces}
            for future in concurrent.futures.as_completed(future_to_space):
                space_result = future.result()
                for key in workspace_metrics:
                    workspace_metrics[key] += space_result.get(key, 0)
        
        workspace_metrics["task_completion_rate"] = (
            (workspace_metrics["completed_tasks"] / workspace_metrics["task_count"] * 100)
            if workspace_metrics["task_count"] > 0 else 0
        )
        
        return {
            "🪐 Spaces": workspace_metrics["space_count"],
            "📂 Folders": workspace_metrics["folder_count"],
            "🗂️ Lists": workspace_metrics["list_count"],
            "📝 Total Tasks": workspace_metrics["task_count"],
            "⚠️ Overdue Tasks": workspace_metrics["overdue_tasks"],
            "🔥 High Priority Tasks": workspace_metrics["high_priority_tasks"]
        }
    except Exception as e:
        logging.error(f"Exception: {str(e)}")
        return {"error": f"Exception: {str(e)}"}

def fetch_space_details(api_key, space_id):
    """
    Fetches details for a specific space including folders, lists, and tasks.
    """
    headers = {"Authorization": api_key}
    space_metrics = {
        "folder_count": 0,
        "list_count": 0,
        "task_count": 0,
        "completed_tasks": 0,
        "overdue_tasks": 0,
        "high_priority_tasks": 0
    }

    folders_url = f"https://api.clickup.com/api/v2/space/{space_id}/folder"
    folders_response = make_api_call(folders_url, headers)
    folders = folders_response.get("folders", [])
    space_metrics["folder_count"] += len(folders)
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_folder = {executor.submit(fetch_folder_details, api_key, folder["id"]): folder for folder in folders}
        for future in concurrent.futures.as_completed(future_to_folder):
            folder_result = future.result()
            for key in space_metrics:
                space_metrics[key] += folder_result.get(key, 0)
    
    return space_metrics

def fetch_folder_details(api_key, folder_id):
    """
    Fetches details for a specific folder including lists and tasks.
    """
    headers = {"Authorization": api_key}
    folder_metrics = {
        "list_count": 0,
        "task_count": 0,
        "completed_tasks": 0,
        "overdue_tasks": 0,
        "high_priority_tasks": 0
    }

    lists_url = f"https://api.clickup.com/api/v2/folder/{folder_id}/list"
    lists_response = make_api_call(lists_url, headers)
    lists = lists_response.get("lists", [])
    folder_metrics["list_count"] += len(lists)
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_list = {executor.submit(fetch_list_details, api_key, lst["id"]): lst for lst in lists}
        for future in concurrent.futures.as_completed(future_to_list):
            list_result = future.result()
            for key in folder_metrics:
                folder_metrics[key] += list_result.get(key, 0)
    
    return folder_metrics

def fetch_list_details(api_key, list_id):
    """
    Fetches details for a specific list including tasks.
    """
    headers = {"Authorization": api_key}
    list_metrics = {
        "task_count": 0,
        "completed_tasks": 0,
        "overdue_tasks": 0,
        "high_priority_tasks": 0
    }

    tasks_url = f"https://api.clickup.com/api/v2/list/{list_id}/task"
    params = {
        "archived": "false",
        "subtasks": "true"
    }
    tasks_response = make_api_call(tasks_url, headers, params)
    tasks = tasks_response.get("tasks", [])
    list_metrics["task_count"] += len(tasks)
    
    for task in tasks:
        status = task.get("status", {}).get("type", "").lower()
        logging.info(f"Task ID: {task['id']} - Status: {status}")
        list_metrics["completed_tasks"] += 1 if status in ["closed", "done", "completed"] else 0
        list_metrics["overdue_tasks"] += 1 if task.get("due_date") and int(task["due_date"]) < int(time.time() * 1000) else 0
        list_metrics["high_priority_tasks"] += 1 if task.get("priority", "") in ["urgent", "high"] else 0

    logging.info(f"Total tasks: {list_metrics['task_count']}, Completed tasks: {list_metrics['completed_tasks']}")
    
    return list_metrics

def make_api_call(url, headers, params=None):
    """
    Makes an API call and handles errors and logging.
    """
    try:
        start_time = time.time()
        response = requests.get(url, headers=headers, params=params)
        logging.info(f"API call to {url} took {time.time() - start_time:.2f} seconds")
        if response.status_code == 200:
            return response.json()
        else:
            logging.error(f"Error {response.status_code}: {response.text}")
            return {}
    except Exception as e:
        logging.error(f"Exception: {str(e)}")
        return {}

def get_ai_recommendations(use_case, company_profile, workspace_details):
    """
    Generates AI-powered recommendations based on workspace data, company profile, and use case.
    """
    prompt = textwrap.dedent(f"""
        Based on the following workspace data:
        {workspace_details if workspace_details else "(No workspace data available)"}
        
        Considering the company's use case: "{use_case}"
        And the following company profile:
        {company_profile}
        
        Please provide a detailed analysis.
        
        <h3>📈 Productivity Analysis</h3>
        Evaluate the current workspace structure and workflow. Provide insights on how to optimize productivity by leveraging the workspace metrics above and tailoring strategies to the specified use case.
        
        <h3>✅ Actionable Recommendations</h3>
        Suggest practical steps to improve efficiency and organization, addressing specific challenges highlighted by the workspace data and the unique requirements of the use case, along with considerations from the company profile.
        
        <h3>🏆 Best Practices & Tips</h3>
        Share industry-specific best practices and tips that can help maximize workflow efficiency for a company with this use case.
        
        <h3>🛠️ Useful ClickUp Templates & Resources</h3>
        Recommend relevant ClickUp templates and resources. Provide hyperlinks to useful resources on clickup.com, university.clickup.com, or help.clickup.com. Provide 5-8 links.
    """)
    
    try:
if client = OpenAI(api_key="sk-2984c908d77a45e2aa3c776d6190be4c", base_url="https://api.deepseek.com")

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Hello"},
    ],
    stream=False
)

print(response.choices[0].message.content)
    except Exception as e:
        logging.error(f"Error generating AI recommendations: {str(e)}")
        return f"⚠️ AI recommendations are not available: {str(e)}"

# ----------------------- #
# Streamlit UI
# ----------------------- #
st.title("🚀 ClickUp Workspace Analysis")

# Input fields available immediately
api_key = st.text_input("🔑 Enter ClickUp API Key: (Optional)", type="password")
if api_key:
    workspaces = fetch_workspaces(api_key)
    if workspaces:
        workspace_id = st.selectbox("💼 Select Workspace:", options=list(workspaces.keys()), format_func=lambda x: workspaces[x])
    else:
        st.error("Failed to fetch workspaces. Please check your API key.")
else:
    workspace_id = None

company_name = st.text_input("🏢 Enter Company Name (Optional):")
use_case = st.text_area("🧑‍💻 Describe your company's use case:")

if st.button("🚀 Let's Go!"):
    if api_key and workspace_id:
        workspace_data = None
        with st.spinner("Fetching workspace data, may take longer for larger Workspaces..."):
            workspace_data = fetch_workspace_details(api_key, workspace_id)
        if workspace_data is None:
            st.error("Failed to fetch workspace data.")
        elif "error" in workspace_data:
            st.error(workspace_data["error"])
        else:
            st.subheader("📊 Workspace Summary")
            # Display workspace data as tiles
            cols = st.columns(4)
            for idx, (key, value) in enumerate(workspace_data.items()):
                with cols[idx % 4]:
                    st.metric(label=key, value=value)
    else:
        workspace_data = None

    # Build and display company profile if a company name is provided
    if company_name:
        with st.spinner("Generating company profile..."):
            company_profile = get_company_info(company_name)
        st.subheader("🏢 Company Profile")
        st.markdown(company_profile, unsafe_allow_html=True)
    else:
        company_profile = "No company information provided."
    
    with st.spinner("Generating AI recommendations..."):
        recommendations = get_ai_recommendations(use_case, company_profile, workspace_data)
        st.markdown(recommendations, unsafe_allow_html=True)

st.markdown("<div style='position: fixed; bottom: 10px; left: 10px; font-size: 12px; color: orange; '>A little tool made by: Yul 😊</div>", unsafe_allow_html=True)
