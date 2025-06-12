import html
import json
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

def extractCharts(url):
    """Extract chart data from Geostat pages"""
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to fetch {url}: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    charts = soup.select("div.chart-rows")
    all_charts = []
    
    if not charts:
        return []

    for idx, chart_div in enumerate(charts, 1):
        raw_data = chart_div.get("data-chart")
        if not raw_data:
            continue

        try:
            chart_data = json.loads(html.unescape(raw_data))
            all_charts.append(chart_data)
        except json.JSONDecodeError as e:
            print(f"Chart {idx} - Failed to parse JSON: {e}")

    return all_charts

def extractFolders(url):
    """Extract subfolder URLs from archive pages"""
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return []

        soup = BeautifulSoup(response.content, 'html.parser')
        archive_div = soup.find('div', class_='archive-items mb-3')
        
        if not archive_div:
            return []
            
        urls = [a['href'] for a in archive_div.find_all('a', href=True)]
        return urls
    except Exception as e:
        print(f"Error extracting folders from {url}: {e}")
        return []

def extract_table_from_url(url):
    """Extract table data from Geostat pages"""
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.content, 'html.parser')
        table_div = soup.find("div", class_="value-databases-table")

        if not table_div:
            return None

        table = table_div.find("table")
        if not table:
            return None

        headers = []
        rows = []

        for tr_index, row in enumerate(table.find_all("tr")):
            cols = row.find_all(["td", "th"])
            text = [col.get_text(strip=True).replace("\xa0", " ") for col in cols]
            if tr_index == 0:
                headers = text
            else:
                rows.append(text)

        if not rows:
            return None

        # Ensure headers match row length
        max_cols = max(len(r) for r in rows) if rows else len(headers)
        if len(headers) < max_cols:
            headers.extend([f"Column_{i}" for i in range(len(headers), max_cols)])

        df = pd.DataFrame(rows, columns=headers[:max_cols])
        return df
    except Exception as e:
        print(f"Error extracting table from {url}: {e}")
        return None

def recursiveScrap(url, depth=0, max_depth=3):
    """Recursively scrape data from Geostat pages"""
    if depth > max_depth:
        return []
        
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to fetch {url}: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    time.sleep(1)  # Be respectful to the server

    name_tag = soup.find("h3", class_="current-page")
    name = name_tag.text.strip() if name_tag else url.split('/')[-1]

    folder_data = []

    # Get table data
    table = extract_table_from_url(url)
    if table is not None and not table.empty:
        table_data = {
            "name": f"{name} - ცხრილი",
            "url": url,
            "type": "table",
            "data": table.to_dict(orient="records")
        }
        folder_data.append(table_data)

    # Get chart data
    charts = extractCharts(url)
    if charts:
        chart_data = {
            "name": f"{name} - დიაგრამა",
            "url": url,
            "type": "chart",
            "data": charts
        }
        folder_data.append(chart_data)

    # Get subfolders recursively
    folders = extractFolders(url)
    for folder_url in folders[:5]:  # Limit to first 5 subfolders to avoid too much data
        sub_data = recursiveScrap(folder_url, depth + 1, max_depth)
        folder_data.extend(sub_data)

    return [{
        "name": name,
        "url": url,
        "type": "folder",
        "data": folder_data
    }] if folder_data else []

def scrapData(categories=None):
    """Main scraping function"""
    if not categories:
        categories = [
            "https://www.geostat.ge/en/modules/categories/195/business-statistics",
            "https://www.geostat.ge/en/modules/categories/92/monetary-statistics",
            "https://www.geostat.ge/en/modules/categories/64/business-register",
            "https://www.geostat.ge/en/modules/categories/56/education-and-culture",
            "https://www.geostat.ge/en/modules/categories/73/environment-statistics",
            "https://www.geostat.ge/en/modules/categories/37/employment-and-wages",
            "https://www.geostat.ge/en/modules/categories/22/national-accounts",
            "https://www.geostat.ge/en/modules/categories/387/service-statistics299",
        ]

    all_data = []

    for url in categories:
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Failed to fetch {url}: {e}")
            continue

        soup = BeautifulSoup(response.text, "html.parser")
        time.sleep(2)
        
        name_tag = soup.find("h3", class_="current-page")
        category_name = name_tag.text.strip() if name_tag else url.split('/')[-1]

        print(f"📁 Scraping category: {category_name}")
        result = recursiveScrap(url)
        
        if result:
            all_data.append({
                "name": category_name,
                "url": url,
                "type": "category",
                "data": result
            })

    # Save structured data
    with open("scraped_data_mcp2.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
        print(f"✅ Saved {len(all_data)} categories to data/scraped_data_mcp2.json")

if __name__ == "__main__":
    import os
    os.makedirs("data", exist_ok=True)
    scrapData()