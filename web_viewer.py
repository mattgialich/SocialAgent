#!/usr/bin/env python3
"""
Web Viewer for Social Agent Results
Displays article analysis and generated posts in a clean web interface
"""

import os
import json
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from pathlib import Path

app = Flask(__name__)

RESULTS_FILE = 'results.json'

def load_results():
    """Load the latest results from JSON file"""
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def format_timestamp(timestamp_str):
    """Format timestamp to readable format"""
    try:
        dt = datetime.fromisoformat(timestamp_str)
        return dt.strftime('%B %d, %Y at %I:%M %p')
    except:
        return timestamp_str

@app.route('/')
def index():
    """Main page showing results"""
    results = load_results()

    if not results:
        return render_template('index.html',
                             no_results=True,
                             message="No results found. Run the scraper first: python main.py 'your keyword'")

    # Add formatted timestamp
    if 'timestamp' in results:
        results['formatted_timestamp'] = format_timestamp(results['timestamp'])

    return render_template('index.html',
                         results=results,
                         no_results=False)

@app.route('/api/results')
def api_results():
    """API endpoint to get results as JSON"""
    results = load_results()
    if results:
        return jsonify(results)
    return jsonify({'error': 'No results found'}), 404

@app.route('/api/refresh')
def api_refresh():
    """Refresh results from file"""
    results = load_results()
    if results:
        return jsonify({'status': 'success', 'results': results})
    return jsonify({'status': 'error', 'message': 'No results found'}), 404

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 Social Agent Web Viewer")
    print("="*60)
    print(f"\n📁 Looking for results in: {os.path.abspath(RESULTS_FILE)}")

    if os.path.exists(RESULTS_FILE):
        print("✅ Results file found!")
    else:
        print("⚠️  No results file found yet.")
        print("   Run the scraper first: python main.py 'asteroid mining'")

    print("\n🌐 Starting web server...")
    print("   Open your browser to: http://localhost:5000")
    print("\n   Press Ctrl+C to stop the server\n")
    print("="*60 + "\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
