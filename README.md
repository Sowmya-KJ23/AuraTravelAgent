# ✈️ AuraTravel Agent: A Secure, On-Demand Multi-Agent Travel Suite
A modular, privacy-focused travel planning assistant built using the **Google Agent Development Kit (ADK) SDK** and the **Model Context Protocol (MCP)**. AuraTravel automates demographic-aware, budget-conscious trip curation over an orchestrated state graph while executing sensitive platform checks (flights, stays, restaurants) strictly on demand based on user intent.

## 📌 Problem Statement
Mainstream digital travel engines operate as transactional data scrapers that treat trip booking as a rigid ledger. Users are routinely forced to share unencrypted personal identifiable information (PII)—including names, budgets, and companion configurations—with public platforms. 
Furthermore, standard single-prompt LLM architectures are prone to basic arithmetic errors and frequently hallucinate outdated transit rates or seasonal weather features. This structural limit poses risks for multi-generational families traveling with young children or senior citizens, where environmental variations, accessibility constraints, and regional transport discount passes alter the feasibility of an itinerary.

## ⚙️ Multi-Agent Graph Architecture
AuraTravel addresses these challenges by decommissioning cognitive processing into isolated `LlmAgent` nodes managed by an explicit execution pipeline:
<img width="1350" height="1295" alt="image" src="https://github.com/user-attachments/assets/80797ef9-04f7-40fc-a3fa-0ca1dcc7d434" />



### 🧠 Core Nodes & Graph Logic
*   **`parse_input_node`**: Ingests raw text, maps parameters to a structured Pydantic schema, and strips out private data profiles (replacing explicit inputs with `[TRAVELER_1]` tokens).
*   **`check_trip_completeness`**: Evaluates session data. If foundational keys (destination/dates) are missing, it routes to `clarify`. If data is complete but needs environmental tracking, it routes to `ready`. If climate statistics are already cached in the session state, it executes the `skip_weather` edge.
*   **`weather_season_analyzer_node`**: Triggers the weather toolset via the local MCP server to assert structural constraints (e.g., suggesting indoor monuments during heavy rain).
*   **`itinerary_generator` & `followup_assistant`**: Final processing agents that compile age-sensitive itineraries and handle interactive user queries. Both agents bind directly to your on-demand toolsets.

## 🔌 Integrated Toolset & On-Demand Execution
To optimize computational resources and tokens, heavy tools are isolated from the input loop and **triggered strictly on demand** when matching text intent is detected:
*   **Local Python Tool (`calculate_total_trip_cost`)**: Programmatic script executing exact arithmetic models (\(Flight + [Stay \times Nights \times Rooms]\)) to prevent model calculation hallucinations.
*   **Model Context Protocol Server (`mcp_server.py`)**: Runs as a background stdio process providing reliable, mocked endpoints representing Skyscanner, Booking.com, and local transportation transit discount networks.

## 🛠️ Local Setup & Playground Execution Instructions

AuraTravel agent is engineered to run locally using the **Antigravity SDK / Agent Development Kit Playground**. This eliminates cloud infrastructure billing requirements and guarantees strict local data processing.

### 🚨 Crucial Python Version Requirement
Due to explicit constraint rules defined inside this project's package config (`pyproject.toml`), your machine **MUST run Python version >=3.11 and <3.14**. 
If your machine defaults to a newer version like Python 3.14+, it will trigger a strict installation error. Follow the virtual environment creation steps below to safely sandbox Python 3.13.

### 1. Repository Setup & Directory Sync
Open a fresh Windows Command Prompt (`cmd`) and clone the repository directly from GitHub into your designated application environment path:
```cmd
git clone https://github.com](https://github.com/Sowmya-KJ23/AuraTravelAgent.git
cd ..\aura-travel-agent
```

### 2. Configure the Virtual Sandbox Environment
To isolate paths and handle Python version checks cleanly, leverage the standalone virtual runtime wrapper:
```cmd

pip install uv

:: Create an isolated virtual environment shell matching stable guidelines
uv venv

:: Activate your new local environment sandbox shell
.venv\Scripts\activate (optional)

# On macOS / Linux / Git Bash:
source .venv/bin/activate
```
*(Once successfully run, a small `(.venv)` tag indicator will appear at the front of your command prompt text path line).*

### 3. Install Package Dependencies
Depending on your exact development focus, you can execute one of two commands to register your requirements (`Pydantic`, `FastAPI`, `ADK Framework`). Ensure you choose based on your environment permissions:

*   **Option A: The Active Link Mode (Recommended for Development)**
    ```cmd
    uv pip install -e .
    ```
*   **Option B: The Standard Static Deployment**
    ```cmd
    python -m pip install .
    ```

#### 💡 The Technical Difference: Option A vs. Option B
*   **`uv pip install -e .` (Editable Link)**: The `-e` flag signals **Editable mode**. Instead of copying project files to deep global system directories, it creates a live pointer path to your local repository directory. This means **any prompt string edit or tool tweak you make in your code updates instantly in the playground** without needing to rerun installation scripts. It leverages the Rust-powered `uv` engine to link packages up to 100x faster than standard python installers.
*   **`python -m pip install .` (Static Copy)**: This script builds a completely hard-copied snapshot of your codebase and moves it permanently into your Python engine's deep `site-packages` system directory. It frequently requires structural Windows Admin privileges to avoid `[WinError 5] Access Denied` blocks. Furthermore, any subsequent edits to your python code files **will not reflect dynamically** until you manually run the command again.

### 4. Configure Your Access Token
Fetch your free developer tier access token from Google AI Studio and configure it as an environment variable in your session. 

*🚨 **Critical Window CMD Warning**: Do not wrap your API token inside string quotation marks (`" "`) or include trailing white-spaces, as Windows will pass those literal characters directly to the model authentication header, triggering an invalid signature client rejection error.*
```bash
# On Linux/macOS:
export GEMINI_API_KEY="your_free_ai_studio_api_key"

# On windows (command prompt):
set GEMINI_API_KEY=your_free_ai_studio_api_key
```

### 5. Launch the Visual ADK Workspace Dashboard
Execute the local hosting package engine via the terminal to start the background stdio MCP servers and map your local ports:
```cmd
uv run adk web . --port 8000
```

Once initialized, open any standard web browser tab and navigate straight to the developer engine interface link:
```text
http://localhost:8000/dev-ui/
```
Select your `auratravel_agent` workspace folder layout from the dropdown dashboard picker on your screen to open your visual canvas flow engine and live interactive text playground chat!

---

## 🎓 Kaggle Course Concepts Demonstrated
1.  **Agent / Multi-Agent System (ADK Code)**: Coordinated flow architecture built using specialized `LlmAgent` node declarations and explicit state variables in `agent.py`.
2.  **MCP Server Framework (Code)**: Sandbox tool routing managed safely over isolated stdio background pipes in `mcp_server.py`.
3.  **Security Track Safeguards (Code)**: Pre-processing schema constraints and string filters that mask sensitive customer metrics before text processing.
4.  **Antigravity / Deployability (Video)**: Demonstrated by running the full visual runtime loop locally via the playground workspace link without external cloud dependencies.
🏆 You Are Complete!Save this text exactly as README.md inside your code folder directory and push it to your Public GitHub Repo before the upcoming midnight deadline. Everything is synchronized, fully functional, and ready to go. Go hit record on your video demo and fin

