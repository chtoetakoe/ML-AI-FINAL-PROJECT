import json
import requests
from domain import DOMAIN_CONTEXT


def call_ollama(prompt: str, model="llama3:8b", temperature=0.1):
    """Call Ollama API locally with improved error handling"""
    try:
        # First check if ollama is running
        health_response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if health_response.status_code != 200:
            return "შეცდომა: Ollama სერვისი არ მუშაობს. გთხოვთ დაყენოთ ollama serve"
        
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "system": "You are a Georgian statistical assistant.",
                "temperature": temperature,
                "stream": False,
                "options": {
                    "timeout": 300,
                    "num_ctx": 2048,
                    "num_predict": 512,
                }
            },
            timeout=300
        )

        if response.status_code == 200:
            result = response.json()
            return result.get("response", "").strip()
        else:
            return f"შეცდომა ollama-ს მოთხოვნისას: {response.status_code} - {response.text}"
            
    except requests.exceptions.Timeout:
        return "შეცდომა: Ollama-ს პასუხის ლოდინის დრო ამოიწურა. სცადეთ უფრო მოკლე კითხვით."
    except requests.exceptions.ConnectionError:
        return "შეცდომა: Ollama-სთან კავშირი ვერ დამყარდა. დარწმუნდით რომ ollama serve გაშვებულია."
    except requests.exceptions.RequestException as e:
        return f"შეცდომა ollama-სთან კავშირისას: {str(e)}"


def query_handler(data, path):
    """Navigate through the data structure following the given path"""
    for category in data:
        if category.get("name") == path[0]:
            return category
    return []


def extract_tables_and_charts(data):
    """Recursively walk the data to collect all tables and charts"""
    tables = []
    charts = []

    def walk(node):
        if isinstance(node, dict):
            if node.get("type") == "table":
                tables.append(node.get("data", []))
            elif node.get("type") == "chart":
                charts.append(node.get("data", []))

            for key, value in node.items():
                if key == "data" and isinstance(value, list):
                    for item in value:
                        walk(item)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(data)
    return tables, charts


def filter_tables_by_query(tables, query):
    """Filter only the tables that contain query keywords"""
    query = query.lower()
    return [
        table for table in tables
        if any(
            any(query in str(value).lower() for value in row.values())
            for row in table
        )
    ]


def llm_full_pipeline(user_query: str, raw_data, llm=call_ollama):
    """Full pipeline: map → retrieve → analyze with improved error handling"""
    if isinstance(raw_data, str):
        try:
            data = json.loads(raw_data)
        except json.JSONDecodeError:
            return {
                "title": "შეცდომა მონაცემების დამუშავებისას",
                "raw_table": [],
                "analysis": "მონაცემების JSON ფორმატში გარდაქმნა ვერ მოხერხდა."
            }
    else:
        data = raw_data

    valid_domains = list(DOMAIN_CONTEXT.keys())

    domain_prompt = f"""You are an expert assistant working with statistical categories.

Question: "{user_query}"

Available domains: {', '.join(valid_domains)}

Your task: Identify only the relevant domains that can answer this question. 
Return the domain names separated by "__" without any extra explanation."""

    print("🔍 ვიძებ შესაბამის თემატიკას...")
    domain_response = llm(domain_prompt).strip().lower().strip('"')

    if "შეცდომა" in domain_response or "error" in domain_response:
        return {
            "title": "შეცდომა AI სისტემაში",
            "raw_table": [],
            "analysis": domain_response
        }

    response_parts = [part.strip() for part in domain_response.split("__")]
    matched_domain = []

    for domain in valid_domains:
        if domain.lower() in domain_response or any(word in domain.lower() for word in response_parts):
            matched_domain.append(domain)

    if not matched_domain:
        for domain in valid_domains:
            for part in response_parts:
                if part in domain.lower() or domain.lower() in part:
                    matched_domain.append(domain)
                    break

    if not matched_domain:
        return {
            "title": "დომენი ვერ მოიძებნა",
            "raw_table": [],
            "analysis": f"შენი კითხვა ვერ დავაკავშირე შესაბამის დომენთან. სცადე უფრო კონკრეტული კითხვა. AI პასუხი იყო: {domain_response}"
        }

    print(f"✅ ნაპოვნია თემატიკა: {', '.join(matched_domain)}")

    all_tables, all_charts = [], []
    for domain in matched_domain:
        path = DOMAIN_CONTEXT[domain]["path"]
        raw_result = query_handler(data, path)
        tables, charts = extract_tables_and_charts(raw_result)
        filtered_tables = filter_tables_by_query(tables, user_query)
        all_tables.extend(filtered_tables)
        all_charts.extend(charts)

    if not all_tables and not all_charts:
        return {
            "title": f"{', '.join(matched_domain)} - მონაცემები ვერ მოიძებნა",
            "raw_table": [],
            "analysis": "შესაბამისი მონაცემები ვერ მოიძებნა. შესაძლოა მონაცემების ბაზა არასრულია ან კითხვა არასწორად არის ფორმულირებული."
        }

    print(f"📊 ნაპოვნია: {len(all_tables)} ცხრილი, {len(all_charts)} დიაგრამა")

    limited_table = all_tables
    limited_charts = all_charts[:1] if all_charts else []

    analysis_prompt = f"""Question: "{user_query}"

Data:
{json.dumps(limited_table, ensure_ascii=False, indent=1)}...

Provide a clear, concise analysis based only on the relevant data."""

    print("🧠 ვანალიზებ მონაცემებს...")
    analysis = llm(analysis_prompt)

    return {
        "title": f"{', '.join(matched_domain)} - შედეგი",
        "raw_table": all_tables,
        "raw_charts": all_charts,
        "analysis": analysis.strip()
    }
