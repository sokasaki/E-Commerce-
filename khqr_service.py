import hashlib
import os
import subprocess
import json
import requests

import time

class KHQRService:
    _demo_timers = {}

    def __init__(self):
        self.token = os.getenv("BAKONG_API_TOKEN", "").strip()
        # No longer using the Python bakong_khqr library directly for QR generation

    def generate_qr_string(self, bank_account, merchant_name, amount, bill_number, 
                           currency='USD', merchant_city='Phnom Penh', 
                           store_label='MShop', phone_number='', terminal_label='Cashier-01'):
        
        # Prepare data for the Node.js generator
        data = {
            "bakongAccountId": bank_account,
            "merchantName": merchant_name,
            "merchantCity": merchant_city,
            "amount": amount,
            "currency": currency,
            "storeLabel": store_label,
            "phoneNumber": phone_number,
            "billNumber": bill_number,
            "terminalLabel": terminal_label
        }
        
        try:
            # Call the Node.js script
            node_script = os.path.join(os.path.dirname(__file__), 'khqr_generator.js')
            result_json = subprocess.check_output(
                ['node', node_script, json.dumps(data)],
                stderr=subprocess.STDOUT,
                text=True
            )
            
            result = json.loads(result_json.strip())
            return result # returns {"qr": "...", "md5": "..."}
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to generate KHQR via Node SDK: {e.output}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error during KHQR generation: {str(e)}")

    def generate_md5(self, qr_string_or_data):
        # If input is a dict from generate_qr_string, use its md5
        if isinstance(qr_string_or_data, dict) and qr_string_or_data.get('md5'):
            return qr_string_or_data['md5']
        
        # Otherwise calculate it manually (fallback)
        qr_string = qr_string_or_data['qr'] if isinstance(qr_string_or_data, dict) else qr_string_or_data
        return hashlib.md5(qr_string.encode()).hexdigest()

    def check_transaction(self, md5):
        if not md5:
            return {"responseCode": 1, "message": "Missing md5"}
        if not self.token:
            return {
                "responseCode": 1,
                "message": "BAKONG_API_TOKEN is missing. Set the environment variable before checking payments."
            }

        response = requests.post(
            'https://api-bakong.nbc.gov.kh/v1/check_transaction_by_md5',
            json={'md5': md5},
            headers={
                'authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json'
            },
            timeout=10
        )
        try:
            payload = response.json()
            # Debug log to terminal
            print(f"DEBUG: Bakong API check response for MD5 {md5}: {payload}")
        except ValueError:
            # --- RENDER DEMO BYPASS ---
            if os.getenv("RENDER"):
                if md5 not in KHQRService._demo_timers:
                    KHQRService._demo_timers[md5] = time.time()
                
                elapsed = time.time() - KHQRService._demo_timers[md5]
                if elapsed > 12:
                    print(f"DEBUG: Render Demo Mode - Auto-approving MD5 {md5}")
                    return {
                        "responseCode": 0,
                        "responseMessage": "Success (Render Demo Bypass)",
                        "data": {"status": "SUCCESS"}
                    }
                else:
                    return {
                        "responseCode": 1,
                        "message": f"Demo Mode: Auto-approving in {int(12 - elapsed)} seconds..."
                    }
            # --------------------------
            
            payload = {
                "responseCode": response.status_code,
                "message": "Bakong API returned a non-JSON response.",
                "raw_text": response.text
            }

        if isinstance(payload, dict):
            payload.setdefault("httpStatus", response.status_code)
            payload.setdefault("httpOk", response.ok)

        if not response.ok and isinstance(payload, dict):
            payload.setdefault("message", f"Bakong API request failed with HTTP {response.status_code}.")

        return payload
