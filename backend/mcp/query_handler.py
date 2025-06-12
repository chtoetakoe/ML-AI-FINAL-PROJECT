from backend.domain import DOMAIN_CONTEXT
from deep_translator import GoogleTranslator

def query_handler(query, data):
    matches = []

    # Auto-translate English query to Georgian for better data matching
    try:
        translated_query = GoogleTranslator(source="auto", target="ka").translate(query)
    except:
        translated_query = query

    query = translated_query.lower()

    # Boost matching priority for known topics
    topic_keywords = {
        "განათლება": ["კურსდამთავრებულ", "სტუდენტ", "სკოლა", "უნივერსიტეტი", "განათლება"],
        "დასაქმება და ხელფასები": ["დასაქმება", "უმუშევრობა", "ხელფასი", "ხელფასები"],
        "ბიზნესის რეესტრი": ["რეგისტრირებული", "კომპანია", "ბიზნესი", "სუბიექტი"],
        "ფულადი სტატისტიკა": ["ინფლაცია", "გაყიდვა", "ფასები", "თანხა", "ანგარიშები"],
    }

    def topic_boost(category_name):
        for topic, keywords in topic_keywords.items():
            if topic in category_name:
                for k in keywords:
                    if k in query:
                        return 10  # max score
        return 0

    def search(name, content, score=0):
        base_score = score + topic_boost(name)

        if query in name.lower():
            matches.append({"score": base_score + 3, "match": {name: content}})

        # Check inside charts
        if content.get("charts"):
            for chart in content["charts"]:
                if "title" in chart and query in chart["title"].lower():
                    matches.append({"score": base_score + 2, "match": {"chart": chart}})

        # Check inside tables
        if content.get("table"):
            for row in content["table"]:
                if any(query in str(val).lower() for val in row.values()):
                    matches.append({"score": base_score + 2, "match": {"table_row": row}})

        # Search nested folders
        for folder in content.get("folders", []):
            for sub_name, sub_content in folder.items():
                search(sub_name, sub_content, base_score)

    for category in data:
        name = category.get("name", "")
        content = category.get("data", {})
        search(name, content)

    # Sort by score
    matches.sort(key=lambda x: x["score"], reverse=True)
    return [m["match"] for m in matches] or [{"message": "❌ ვერ მოიძებნა შესაბამისი ინფორმაცია"}]
