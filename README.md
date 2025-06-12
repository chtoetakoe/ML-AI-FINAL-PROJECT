# GeoStatAI

A Python-based statistical assistant that uses GPT-4 and MCP (Model Context Protocol) to analyze and provide insights on Georgian statistical data. The application processes data scraped from [საქსტატი (Geostat)](https://www.geostat.ge/ka), Georgia's National Statistics Office, and uses advanced AI to provide meaningful analysis and insights from the statistical data.



## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Installation

Install the required dependencies:
```bash
pip install -r requirements.txt
```

The `requirements.txt` file contains all necessary Python packages for the project.


## Configuration

1. Create a `.env` file in the root directory of the project
2. Add your OpenAI API key to the `.env` file:
```
OPENAI_API_KEY=your_api_key_here
```

## Running the Application

To start the application, run:
```bash
python app.py
```

The application will:
1. Load the data from `data/scraped_data_mcp1.json`
2. Present you with a prompt where you can enter your questions
3. Use GPT-4 to analyze the data and provide insights
4. Display the results including:
   - A title
   - Raw data statistics
   - Analysis of the data

To exit the application, type "exit", "quit", or "გასვლა" (in Georgian).

## Project Structure

- `app.py`: Main application file
- `domain.py`: Domain-specific logic
- `llm/`: LLM-related functionality
- `mcp/`: Model Context Protocol implementation for managing data context and analysis flow
- `data/`: Contains the data files
- `.env`: Environment variables (API keys)
- `requirements.txt`: List of Python package dependencies

## Notes

- Always ensure you have the latest dependencies installed by running `pip install -r requirements.txt` after pulling new changes 
