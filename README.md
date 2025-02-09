# ClickUp-Workspace-Analyzer
Analyzes your ClickUp workspace with the help of AI

# ClickUp AI Workspace Analyzer

## 📌 Overview
ClickUp AI Workspace Analyzer is a **Streamlit-based** web application that integrates with **ClickUp API** and **Gemini AI** to analyze workspace productivity and provide AI-driven recommendations.

## 🚀 Features
- **Fetch Workspace Data**: Retrieves information about spaces, folders, lists, and tasks from ClickUp.
- **AI-Powered Recommendations**: Uses **Gemini AI** to analyze workspace performance and provide insights.
- **ClickUp Templates & Resources**: Suggests relevant templates to optimize workflow.
- **User-Friendly UI**: Modern **Streamlit** interface for easy interaction.

## 🛠️ Setup Instructions

### 1️⃣ Prerequisites
- Install **Python 3.10+**
- Create a ClickUp API Key from [ClickUp API Docs](https://clickup.com/api)
- Obtain a **Gemini AI API Key** from [Google AI](https://ai.google.dev)

### 2️⃣ Install Dependencies
Run the following command to install required Python libraries:
```bash
pip install -r requirements.txt
```

### 3️⃣ Create a `.env` File
Create a `.env` file in the project directory and add:
```
GEMINI_API_KEY=your_gemini_api_key
```

### 4️⃣ Run the Application
Launch the Streamlit app with:
```bash
streamlit run clickup_analyzer.py
```

## 🎯 Usage
1. Enter your **ClickUp API Key**.
2. Specify the **use case** (e.g., Project Management, Sales, HR).
3. Click **"Analyze Workspace"** to fetch data and receive AI recommendations.
4. Browse suggested **ClickUp templates & resources** to improve productivity.

## 📚 Resources & Templates
- [ClickUp Project Management](https://clickup.com/templates/project-management)
- [ClickUp Sales CRM](https://clickup.com/templates/sales-crm)
- [ClickUp HR & Recruitment](https://clickup.com/templates/hr-recruitment)
- [ClickUp Marketing Campaign](https://clickup.com/templates/marketing-campaign)

## 🤝 Contributions
Feel free to submit issues or feature requests via GitHub.

## 📜 License
This project is open-source under the **MIT License**.

