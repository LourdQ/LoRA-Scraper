
# Production deployment version
import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from flask import Flask, jsonify, request, Response, stream_with_context
from flask_cors import CORS
from datetime import datetime
import threading
import time
import json
from lora_scraper import LoRAScraper


app = Flask(__name__)
CORS(app, origins=[
    "https://lora-scraper.vercel.app",  # Your Vercel domain
    "http://localhost:3000",  # Local development
    "*"  # For initial testing - we'll remove this later
])

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

# Global variables to track scan status
scan_status = {
    "status": "idle",
    "last_scan": None,
    "current_results": [],
    "is_scanning": False,
    "current_model": None,
    "scanned_ids": set(),  # Track scanned IDs
    "error": None
}

# Initialize scraper
scraper = LoRAScraper()

def check_existing_model(model_id):
    """Check if model exists in Airtable"""
    try:
        records = scraper.lora_table.all(formula=f"{{CivitAI ID}}='{str(model_id)}'")
        return len(records) > 0
    except Exception as e:
        print(f"Error checking Airtable: {e}")
        return False

def run_scan(model_id):
    print(f"=== Starting scan for model {model_id} ===")
    try:
        scan_status["is_scanning"] = True
        scan_status["status"] = "scanning"
        scan_status["current_model"] = model_id
        scan_status["error"] = None

        print("Fetching model data from CivitAI...")
        model_data = scraper.fetch_model(model_id)
        
        if model_data:
            print("Successfully fetched model data")
            print("Extracting LORA data...")
            lora_data, examples = scraper.extract_lora_data(model_data)
            print(f"Found {len(examples)} examples")
            
            print("Saving to Airtable...")
            success = scraper.save_to_airtable(lora_data, examples)
            
            if success:
                scan_status["scanned_ids"].add(model_id)
            
            result = {
                "id": str(len(scan_status["current_results"]) + 1),
                "timestamp": datetime.now().isoformat(),
                "modelId": model_id,
                "modelName": lora_data['Name'],
                "author": lora_data['Author'],
                "foundItems": len(examples),
                "status": "success" if success else "error"
            }
            
            scan_status["current_results"].append(result)
            print(f"Scan completed successfully for model {model_id}")
        else:
            error_msg = f"Failed to fetch model {model_id}"
            print(error_msg)
            scan_status["error"] = error_msg
            scan_status["current_results"].append({
                "id": str(len(scan_status["current_results"]) + 1),
                "timestamp": datetime.now().isoformat(),
                "modelId": model_id,
                "modelName": "Unknown",
                "author": "Unknown",
                "foundItems": 0,
                "status": "error"
            })
    
    except Exception as e:
        error_message = str(e)
        print(f"Error during scan: {error_message}")
        scan_status["error"] = error_message
        scan_status["current_results"].append({
            "id": str(len(scan_status["current_results"]) + 1),
            "timestamp": datetime.now().isoformat(),
            "modelId": model_id,
            "modelName": "Error",
            "author": "Unknown",
            "foundItems": 0,
            "status": "error"
        })
    
    finally:
        scan_status["is_scanning"] = False
        scan_status["status"] = "idle"
        scan_status["last_scan"] = datetime.now().isoformat()
        scan_status["current_model"] = None
        print("=== Scan process completed ===")

@app.route('/check-model', methods=['GET'])
def check_model():
    try:
        model_id = request.args.get('modelId')
        if not model_id:
            return jsonify({"error": "No model ID provided"}), 400
        
        model_id = int(model_id)
        
        # Check recent scans
        if model_id in scan_status["scanned_ids"]:
            return jsonify({
                "exists": True,
                "message": "Model was recently scanned"
            })
        
        # Check Airtable
        exists = check_existing_model(model_id)
        return jsonify({
            "exists": exists,
            "message": "Model already exists in database" if exists else "Model is new"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/start-scan', methods=['POST'])
def start_scan():
    if not scan_status["is_scanning"]:
        try:
            data = request.json
            model_id = data.get('modelId')
            
            if not model_id:
                return jsonify({"error": "No model ID provided"}), 400
            
            print(f"Received scan request for model {model_id}")
            # Start scan in background thread
            thread = threading.Thread(target=run_scan, args=(model_id,))
            thread.start()
            
            return jsonify({
                "message": "Scan started",
                "status": "scanning",
                "modelId": model_id
            })
        except Exception as e:
            return jsonify({
                "error": str(e),
                "status": "error"
            }), 500
    
    return jsonify({
        "message": "Scan already in progress",
        "status": "scanning",
        "modelId": scan_status["current_model"]
    })

@app.route('/scan-status', methods=['GET'])
def get_status():
    return jsonify({
        "status": scan_status["status"],
        "lastScan": scan_status["last_scan"],
        "currentModel": scan_status["current_model"],
        "results": scan_status["current_results"],
        "error": scan_status["error"]
    })

@app.route('/clear-status', methods=['POST'])
def clear_status():
    scan_status["status"] = "idle"
    scan_status["is_scanning"] = False
    scan_status["current_model"] = None
    scan_status["error"] = None
    return jsonify({"message": "Status cleared"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)


