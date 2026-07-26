import sys
import logging
logging.basicConfig(level=logging.INFO)

print("1. Importing app.main...")
import app.main
from fastapi.testclient import TestClient

print("2. Setting startup_complete...")
app = app.main.app
app.state.startup_complete = True

print("3. Initializing TestClient...")
client = TestClient(app)

print("4. Testing endpoints...")
print("Checking available routes matching copilot or hospital...")
for route in app.routes:
    if hasattr(route, 'path'):
        if 'copilot' in route.path or 'hospital' in route.path:
            print("Route:", route.path, route.methods if hasattr(route, 'methods') else '')

print("\n--- Trying r1: POST /api/copilot/query ---")
try:
    r1 = client.post('/api/copilot/query', json={'patient_id': 'ICU-10248', 'question': 'What are the key physiological findings for Amelia Chen?'})
    print("r1 status:", r1.status_code)
    print("r1 json:", r1.json())
except Exception as e:
    print("r1 error:", e)

print("\n--- Trying alternative r1: POST /api/clinical-copilot/chat ---")
try:
    r1_alt = client.post('/api/clinical-copilot/chat', json={'patient_id': 'ICU-10248', 'question': 'What are the key physiological findings for Amelia Chen?'})
    print("r1_alt status:", r1_alt.status_code)
    print("r1_alt json keys:", r1_alt.json().keys() if isinstance(r1_alt.json(), dict) else r1_alt.json())
    print("--- CLINICAL COPILOT (Amelia Chen) ---")
    print(r1_alt.json().get('answer', {}).get('clinical_reasoning') or r1_alt.json().get('clinical_reasoning') or r1_alt.json().get('reasoning'))
except Exception as e:
    print("r1_alt error:", e)

print("\n--- Trying r2: POST /api/hospital-assistant/query ---")
try:
    r2 = client.post('/api/hospital-assistant/query', json={'question': 'Give me an ICU summary right now'})
    print("r2 status:", r2.status_code)
    print("r2 json:", r2.json())
except Exception as e:
    print("r2 error:", e)

print("\n--- Trying alternative r2: POST /api/hospital-assistant/chat ---")
try:
    r2_alt = client.post('/api/hospital-assistant/chat', json={'question': 'Give me an ICU summary right now'})
    print("r2_alt status:", r2_alt.status_code)
    print("r2_alt json keys:", r2_alt.json().keys() if isinstance(r2_alt.json(), dict) else r2_alt.json())
    print("--- HOSPITAL ASSISTANT ---")
    print(r2_alt.json().get('answer', {}).get('reasoning') or r2_alt.json().get('reasoning'))
except Exception as e:
    print("r2_alt error:", e)
