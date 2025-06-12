import json
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import sys

from deep_translator import GoogleTranslator

from mcp.app import handle_user_query, check_ollama_connection,load_data
from flask import render_template
import time


def initialize_data():
    """Initialize the statistical data on server startup"""
    global statistical_data
    print("🔄 Initializing API server...")
    
    # Check Ollama connection
    if not check_ollama_connection():
        print("❌ Ollama connection failed - server will still start but queries will fail")
        # Don't return False here, let server start anyway
    
    # Load statistical data
    statistical_data = load_data()
    if not statistical_data:
        print("❌ Failed to load statistical data")
        print("💡 შეგიძლიათ შექმნათ ტესტური მონაცემები:")
        print("   python create_test_data.py")
        return False
    
    print(f"✅ Loaded {len(statistical_data)} statistical categories")
    return True


# Add the backend directory to Python path
# Setup Flask to find templates in frontend/
app = Flask(__name__, template_folder='../frontend')
CORS(app)

# Serve index.html using Jinja
@app.route('/')
def serve_index():
    return render_template('index.html')
# Import the functions we need from the mcp module
CORS(app)  # Enable CORS for frontend communication

# Global variable to store data

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'data_loaded': statistical_data is not None,
        'categories_count': len(statistical_data) if statistical_data else 0
    })

@app.route('/api/query', methods=['POST'])
def process_query():
    """Process user query and return analysis"""
    global statistical_data
    
    try:
        llm_start_time = time.time()
        # Get query from request
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({
                'success': False,
                'error': 'Query is required'
            }), 400
        
        user_query = data['query'].strip()
        if not user_query:
            return jsonify({
                'success': False,
                'error': 'Query cannot be empty'
            }), 400
        
        # Check if data is loaded
        if not statistical_data:
            return jsonify({
                'success': False,
                'error': 'Statistical data not loaded. Please restart the server.'
            }), 500
        
        print(f"📝 Processing query: {user_query}")
        
        # Process query through LLM pipeline
        result = handle_user_query(user_query, statistical_data)
        translator = GoogleTranslator(source="auto", target="ka")



        llm_end_time = time.time()
        llm_duration = round(llm_end_time - llm_start_time, 2)
        start_time = time.time()

        # Format response for frontend
        response_text = f"📌 {result['title']}\n\n"
        
        if result.get('raw_table'):
            response_text += f"📊 Found {len(result['raw_table'])} tables\n"
        
        if result.get('raw_charts'):
            response_text += f"📈 Found {len(result['raw_charts'])} charts\n"

        end_time = time.time()
        duration = round(end_time - start_time, 2)
        response_text += f"\n🧠 Analysis:\n{result['analysis']}"
        response_text = translator.translate(response_text)

        print(f"\n\n⏱️ Response time: {llm_duration} seconds, Output time: {duration}")

        return jsonify({
            'success': True,
            'reply': response_text,
            'data': {
                'title': result['title'],
                'analysis': result['analysis'],
                'tables_count': len(result.get('raw_table', [])),
                'charts_count': len(result.get('raw_charts', []))
            }
        })
        
    except Exception as e:
        error_msg = f"Error processing query: {str(e)}"
        print(f"❌ {error_msg}")
        return jsonify({
            'success': False,
            'error': 'An error occurred while processing your query. Please try again.'
        }), 500


@app.route('/api/categories', methods=['GET'])
def get_categories():
    """Get available statistical categories"""
    global statistical_data
    
    if not statistical_data:
        return jsonify({
            'success': False,
            'error': 'Data not loaded'
        }), 500
    
    categories = [item["name"] for item in statistical_data]
    return jsonify({
        'success': True,
        'categories': categories
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

