# GeoStatAI

A Python-based statistical assistant that uses MCP (Model Context Protocol) and the `llama3:8b` model from Ollama to analyze and provide insights on Georgian statistical data. The application processes data scraped from [საქსტატი (Geostat)](https://www.geostat.ge/ka), Georgia's National Statistics Office.

---

## Prerequisites

* Python 3.8 or higher
* `pip` (Python package installer)
* [Ollama](https://ollama.com/) installed and running
* AI model: `llama3:8b` pulled via Ollama

---

## Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

---

## Running the Application

1. Make sure [Ollama](https://ollama.com/) is installed and running:

   ```bash
   ollama serve
   ```

2. Pull the required AI model:

   ```bash
   ollama run llama3:8b
   ```

3. Navigate to the `data` folder and run the scraper to generate the required dataset:

   ```bash
   cd data
   python scrapper.py
   cd ..
   ```

4. Navigate to the `backend` directory and start the server:

   ```bash
   cd backend
   python start_server.py
   ```

The application will:

* Scrape statistical data using `scrapper.py`
* Load data from `data/scraped_data_mcp1.json`
* Start a Flask server
* Use the MCP system and `llama3:8b` model to handle queries

---

## Project Structure

* `backend/start_server.py`: Entry point to launch the backend server
* `data/scrapper.py`: Script to scrape data from Geostat
* `domain.py`: Domain-specific logic
* `llm/`: LLM-related functionality
* `mcp/`: Model Context Protocol implementation
* `data/`: Contains the scraped data
* `requirements.txt`: Python package dependencies

