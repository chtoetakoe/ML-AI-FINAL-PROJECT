from flask_api import app, initialize_data

if __name__ == '__main__':
    print("=" * 60)
    print("🇬🇪 Georgian Statistical Assistant API Server")
    print("=" * 60)
    
    # Initialize data
    if initialize_data():
        print("🚀 Starting API server on http://localhost:5000")
        print("📡 Frontend can now connect to the API")
        print("💡 Use Ctrl+C to stop the server")
        print("=" * 60)
        
        # Start the Flask server
        app.run(
            host='127.0.0.1',
            port=5000,
            debug=True,
            use_reloader=False  # Disable reloader to prevent data reloading issues
        )
    else:
        print("❌ Failed to initialize server")
        print("Please check Ollama connection and data files")