#!/usr/bin/env python3
"""
Web Viewer for Social Agent Results
Displays article analysis and generated posts in a clean web interface
"""

import os
import json
import subprocess
import threading
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from pathlib import Path

app = Flask(__name__)

RESULTS_FILE = 'results.json'
scraper_status = {'running': False, 'output': '', 'error': ''}

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

def run_scraper_background(keyword, max_articles):
    """Run the scraper in background"""
    global scraper_status
    try:
        scraper_status['running'] = True
        scraper_status['output'] = 'Starting scraper...\n'
        scraper_status['error'] = ''

        # Run the scraper
        cmd = ['python', 'main.py', keyword, '--max-articles', str(max_articles), '--simple', '--quiet']
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        stdout, stderr = process.communicate()

        scraper_status['output'] = stdout
        if stderr:
            scraper_status['error'] = stderr

        scraper_status['running'] = False

    except Exception as e:
        scraper_status['error'] = str(e)
        scraper_status['running'] = False

@app.route('/api/run-scraper', methods=['POST'])
def run_scraper():
    """Run the article scraper"""
    global scraper_status

    if scraper_status['running']:
        return jsonify({'status': 'error', 'message': 'Scraper is already running'}), 400

    data = request.get_json()
    keyword = data.get('keyword', 'asteroid mining')
    max_articles = data.get('max_articles', 5)

    # Run in background thread
    thread = threading.Thread(target=run_scraper_background, args=(keyword, max_articles))
    thread.start()

    return jsonify({'status': 'success', 'message': 'Scraper started'})

@app.route('/api/scraper-status')
def get_scraper_status():
    """Get scraper status"""
    return jsonify(scraper_status)

if __name__ == '__main__':
    # Get port from environment (Replit sets this automatically)
    port = int(os.environ.get('PORT', 5000))

    print("\n" + "="*60)
    print("🚀 Social Agent Web Viewer")
    print("="*60)
    print(f"\n📁 Looking for results in: {os.path.abspath(RESULTS_FILE)}")

    if os.path.exists(RESULTS_FILE):
        print("✅ Results file found!")
    else:
        print("⚠️  No results file found yet.")
        print("   Run the scraper in Shell: python main.py 'asteroid mining'")
        print("   Or use the Run Scraper button on the web interface")

    print(f"\n🌐 Starting web server on port {port}...")
    print("   Replit will automatically open the preview")
    print("   Or click the 'Open in new tab' button")
    print("\n   Press Ctrl+C to stop the server\n")
    print("="*60 + "\n")

    # Disable debug mode in production (Replit)
    debug_mode = os.environ.get('REPL_ID') is None
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
