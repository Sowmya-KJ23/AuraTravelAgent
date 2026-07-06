# ✈️ AuraTravel Agent: A Secure, On-Demand Multi-Agent Travel Suite
A modular, privacy-focused travel planning assistant built using the **Google Agent Development Kit (ADK) SDK** and the **Model Context Protocol (MCP)**. AuraTravel automates demographic-aware, budget-conscious trip curation over an orchestrated state graph while executing sensitive platform checks (flights, stays, restaurants) strictly on demand based on user intent.

## 📌 Problem Statement
Mainstream digital travel engines operate as transactional data scrapers that treat trip booking as a rigid ledger. Users are routinely forced to share unencrypted personal identifiable information (PII)—including names, budgets, and companion configurations—with public platforms. 
Furthermore, standard single-prompt LLM architectures are prone to basic arithmetic errors and frequently hallucinate outdated transit rates or seasonal weather features. This structural limit poses risks for multi-generational families traveling with young children or senior citizens, where environmental variations, accessibility constraints, and regional transport discount passes alter the feasibility of an itinerary.

## ⚙️ Multi-Agent Graph Architecture
AuraTravel addresses these challenges by decommissioning cognitive processing into isolated `LlmAgent` nodes managed by an explicit execution pipeline:

