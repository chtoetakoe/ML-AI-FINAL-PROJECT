#!/usr/bin/env python3
"""
Georgian Statistical Assistant
Uses Ollama for local LLM processing without API keys
"""

import json
import os
import requests
from llm.llm import llm_full_pipeline, call_ollama
from deep_translator import GoogleTranslator

def load_data():
    """Load scraped statistical data"""
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    data_file = os.path.join(base_dir, "data", "scraped_data_mcp2.json")

    print(f"🔍 Loading from: {data_file}")  # debug

    if not os.path.exists(data_file):
        print(f"❌ მონაცემების ფაილი ვერ მოიძებნა: {data_file}")
        print("გთხოვთ ჯერ გაუშვათ scraper.py მონაცემების ჩამოსატვირთად")
        return None

    try:
        with open(data_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ მონაცემების ფაილის წაკითხვის შეცდომა: {e}")
        return None




def handle_user_query(query, data):
    """Process user query through LLM pipeline"""
    translator = GoogleTranslator(source="ka", target="en")
    query = translator.translate(query)

    
    print(query)
    return llm_full_pipeline(query, data, call_ollama)

def print_banner():
    """Print application banner"""
    print("=" * 60)
    print("🇬🇪 ქართული სტატისტიკური ასისტენტი")
    print("   Georgian Statistical Assistant")
    print("=" * 60)
    print("📊 საქსტატის მონაცემების ანალიზი AI-ის საშუალებით")
    print("🤖 იყენებს Ollama-ს (API გასაღები არ არის საჭიროო)")
    print("=" * 60)

def check_ollama_connection():
    """Check if Ollama is running and accessible"""
    try:
        # Check if ollama service is running
        response = requests.get("http://localhost:11434/api/tags", timeout=10)
        if response.status_code == 200:
            models = response.json().get("models", [])
            if models:
                model_names = [model["name"] for model in models]
                print(f"✅ Ollama მუშაობს. ხელმისაწვდომი მოდელები: {', '.join(model_names)}")
                
                # Check for recommended models
                recommended = ["llama3.2", "llama3.2:1b", "llama3"]
                available_recommended = [m for m in model_names if any(r in m for r in recommended)]
                
                if available_recommended:
                    print(f"🎯 რეკომენდებული მოდელი ნაპოვნია: {available_recommended[0]}")
                    return True
                else:
                    print("⚠️  რეკომენდებული მოდელი არ არის. გაუშვით:")
                    print("   ollama pull llama3.2:1b")
                    return False
            else:
                print("⚠️  Ollama მუშაობს, მაგრამ მოდელები არ არის დაინსტალირებული")
                print("გაუშვით: ollama pull llama3.2:1b")
                return False
        else:
            print(f"❌ Ollama API პასუხობს შეცდომით: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Ollama-სთან კავშირი ვერ დამყარდა.")
        print("დარწმუნდით, რომ Ollama გაშვებულია:")
        print("1. დააინსტალირეთ Ollama: https://ollama.ai")
        print("2. გაუშვით ტერმინალში: ollama serve")
        print("3. ახალ ტერმინალში: ollama pull llama3.2:1b")
        return False
    except Exception as e:
        print(f"❌ Ollama შემოწმების შეცდომა: {e}")
        return False

def test_ollama_simple():
    """Test ollama with a simple request"""
    print("\n🧪 Ollama-ს ტესტირება...")
    test_result = call_ollama("გამარჯობა")
    if "შეცდომა" in test_result:
        print(f"❌ ტესტი ვერ ჩაიარა: {test_result}")
        return False
    else:
        print(f"✅ ტესტი წარმატებულია: {test_result[:50]}...")
        return True

def main():
    """Main application loop"""
    print_banner()
     
    # Check Ollama connection
    if not check_ollama_connection():
        return
    
    # Test Ollama with simple request
    if not test_ollama_simple():
        return
    
    # Load data
    print("\n📂 მონაცემების ჩატვირთვა...")
    data = load_data()
    if not data:
        return
    
    categories = [item["name"] for item in data]
    print(f"✅ ჩაიტვირთა {len(data)} კატეგორია: {', '.join(categories)}")
    
    print("\n" + "=" * 60)
    print("💬 მზად ვარ კითხვებისთვის!")
    print("მაგალითი: 'რამდენი კომპანიაა რეგისტრირებული?'")
    print("💡 რჩევა: მოკლე და კონკრეტული კითხვები უკეთესად მუშაობს")
    print("გასასვლელად დაწერეთ: exit, quit, ან გასვლა")
    print("=" * 60 + "\n")
    
    while True:
        try:
            query = input("❓ კითხვა: ").strip()
            
            if query.lower() in {"exit", "quit", "გასვლა", "q"}:
                print("👋 ნახვამდის!")
                break
            
            if not query:
                print("⚠️  გთხოვთ, შეიყვანოთ კითხვა\n")
                continue
            
            print("\n🤖 ვანალიზებ მონაცემებს... (შეიძლება რამდენიმე წუთი დასჭირდეს)")
            result = handle_user_query(query, data)
            
            print(f"\n📌 {result['title']}")
            print("-" * 50)

            if result.get('raw_table'):
                print(f"📊 ნაპოვნი მონაცემები: {len(result['raw_table'])} ცხრილი")

            if result.get('raw_charts'):
                print(f"📈 ნაპოვნი დიაგრამები: {len(result['raw_charts'])}")

            
            print(f"\n🧠 ანალიზი:")
            print(result['analysis'])
            print("\n" + "=" * 60 + "\n")
            
        except KeyboardInterrupt:
            print("\n👋 დასრულდა.")
            break
        except Exception as e:
            print(f"❌ შეცდომა: {e}\n")
            continue

if __name__ == "__main__":
    main()
