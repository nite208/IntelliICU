import sys
print("Step 1: Starting imports...", flush=True)
import app.main, asyncio
print("Step 2: app.main imported.", flush=True)
from fastapi.testclient import TestClient
print("Step 3: TestClient imported.", flush=True)

app = app.main.app
app.state.startup_complete = True
print("Step 4: Initializing TestClient...", flush=True)
client = TestClient(app)
print("Step 5: TestClient initialized. Making get /api/dashboard/summary...", flush=True)

r1 = client.get('/api/dashboard/summary')
print('Summary API:', r1.json(), flush=True)

print("Step 6: Making get /api/hospital-assistant/snapshot...", flush=True)
r2 = client.get('/api/hospital-assistant/snapshot')
print('Hospital Snapshot:', r2.json().get('summary'), flush=True)
print("Step 7: Finished!", flush=True)
