# Production deployment version
import os
import sys
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import threading
from typing import Dict, Set, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from lora_scraper import LoRAScraper

# Type definitions for better code clarity
ScanResult = Dict[str, str]
ScanStatus = Dict[str, any]

class APIServer:
    def __init__(self):
        self.app = Flask(__name__)
        self.setup_cors()
        self.setup_routes()
        self.scraper = LoRAScraper()
        
        # Initialize scan status
        self.scan_status: ScanStatus = {
            "status": "idle",
            "last_scan": None,
            "current_results": [],
            "is_scanning": False,
            "current_model": None,
            "scanned_ids": set(),
            "error": None
        }

    def setup_cors(self):
        """Configure CORS settings"""
        CORS(self.app, origins=[
            "https://lora-scraper.vercel.app",
            "http://localhost:3000",
            "*"  # Remove in production
        ])

    def setup_routes(self):
        """Register all API routes"""
        routes = [
            ('/api/health', 'health', ['GET']),
            ('/api/check-model', 'check_model', ['GET']),
            ('/api/start-scan', 'start_scan', ['POST']),
            ('/api/scan-status', 'get_status', ['GET']),
            ('/api/clear-status', 'clear_status', ['POST'])
        ]
        
        for path, func_name, methods in routes:
            self.app.add_url_rule(
                path,
                view_func=getattr(self, func_name),
                methods=methods
            )

    def health(self):
        """Health check endpoint"""
        return jsonify({"status": "healthy"}), 200

    def check_model(self):
        """Check if model exists in database"""
        try:
            model_id = request.args.get('modelId')
            if not model_id:
                return jsonify({"error": "No model ID provided"}), 400

            model_id = int(model_id)
            
            # Check recent scans
            if model_id in self.scan_status["scanned_ids"]:
                return jsonify({
                    "exists": True,
                    "message": "Model was recently scanned"
                })

            # Check Airtable
            exists = self._check_existing_model(model_id)
            return jsonify({
                "exists": exists,
                "message": "Model already exists in database" if exists else "Model is new"
            })
            
        except ValueError:
            return jsonify({"error": "Invalid model ID format"}), 400
        except Exception as e:
            logger.error(f"Error checking model: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500

    def start_scan(self):
        """Start a new model scan"""
        if self.scan_status["is_scanning"]:
            return jsonify({
                "message": "Scan already in progress",
                "status": "scanning",
                "modelId": self.scan_status["current_model"]
            })

        try:
            data = request.json
            model_id = data.get('modelId')
            
            if not model_id:
                return jsonify({"error": "No model ID provided"}), 400

            logger.info(f"Starting scan for model {model_id}")
            thread = threading.Thread(
                target=self._run_scan,
                args=(model_id,)
            )
            thread.start()

            return jsonify({
                "message": "Scan started",
                "status": "scanning",
                "modelId": model_id
            })

        except Exception as e:
            logger.error(f"Error starting scan: {str(e)}")
            return jsonify({
                "error": str(e),
                "status": "error"
            }), 500

    def get_status(self):
        """Get current scan status"""
        return jsonify({
            "status": self.scan_status["status"],
            "lastScan": self.scan_status["last_scan"],
            "currentModel": self.scan_status["current_model"],
            "results": self.scan_status["current_results"],
            "error": self.scan_status["error"]
        })

    def clear_status(self):
        """Clear current scan status"""
        self.scan_status.update({
            "status": "idle",
            "is_scanning": False,
            "current_model": None,
            "error": None
        })
        return jsonify({"message": "Status cleared"})

    def _check_existing_model(self, model_id: int) -> bool:
        """Check if model exists in Airtable"""
        try:
            records = self.scraper.lora_table.all(
                formula=f"{{CivitAI ID}}='{str(model_id)}'"
            )
            return len(records) > 0
        except Exception as e:
            logger.error(f"Error checking Airtable: {str(e)}")
            return False

    def _run_scan(self, model_id: int):
        """Execute the scan process"""
        logger.info(f"=== Starting scan for model {model_id} ===")
        try:
            self.scan_status.update({
                "is_scanning": True,
                "status": "scanning",
                "current_model": model_id,
                "error": None
            })

            logger.info("Fetching model data from CivitAI...")
            model_data = self.scraper.fetch_model(model_id)

            if not model_data:
                raise Exception(f"Failed to fetch model {model_id}")

            logger.info("Extracting LORA data...")
            lora_data, examples = self.scraper.extract_lora_data(model_data)
            logger.info(f"Found {len(examples)} examples")

            logger.info("Saving to Airtable...")
            success = self.scraper.save_to_airtable(lora_data, examples)

            if success:
                self.scan_status["scanned_ids"].add(model_id)

            self._add_scan_result(model_id, lora_data, len(examples), success)
            logger.info(f"Scan completed successfully for model {model_id}")

        except Exception as e:
            error_message = str(e)
            logger.error(f"Error during scan: {error_message}")
            self.scan_status["error"] = error_message
            self._add_scan_result(model_id, None, 0, False)

        finally:
            self.scan_status.update({
                "is_scanning": False,
                "status": "idle",
                "last_scan": datetime.now().isoformat(),
                "current_model": None
            })
            logger.info("=== Scan process completed ===")

    def _add_scan_result(self, model_id: int, lora_data: Optional[Dict], 
                        num_examples: int, success: bool):
        """Add a new scan result to the status"""
        result = {
            "id": str(len(self.scan_status["current_results"]) + 1),
            "timestamp": datetime.now().isoformat(),
            "modelId": model_id,
            "modelName": lora_data.get('Name', 'Unknown') if lora_data else 'Error',
            "author": lora_data.get('Author', 'Unknown') if lora_data else 'Unknown',
            "foundItems": num_examples,
            "status": "success" if success else "error"
        }
        self.scan_status["current_results"].append(result)

    def run(self, host='0.0.0.0', port=None):
        """Run the Flask application"""
        port = int(port or os.environ.get('PORT', 8000))
        self.app.run(host=host, port=port)

# Application instance
app = APIServer().app

if __name__ == '__main__':
    server = APIServer()
    server.run()
