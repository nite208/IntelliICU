import uuid
from datetime import datetime
import io
import csv
import json
import os
import asyncio

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

from app.websocket.manager import manager as ws_manager
from app.database.session import SessionLocal
from app.database.models import DBTimelineEvent

class TimelineEngine:
    def __init__(self):
        self._events = {}
        self._seed_mock = os.getenv("ICU_SEED_MOCK_DATA", "true").lower() == "true"
        if self._seed_mock:
            self._seed_mock_data()

    def _seed_mock_data(self):
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._events["ICU-10248"] = [
            {
                "id": "mock-ev-1",
                "patient_id": "ICU-10248",
                "timestamp": now_str,
                "time": "07:45",
                "type": "Clinical",
                "title": "Admission",
                "description": "Patient admitted to Medical ICU.",
                "actor": "System",
                "metadata": {"diagnosis": "Septic Shock", "bed": "MICU-04"}
            },
            {
                "id": "mock-ev-2",
                "patient_id": "ICU-10248",
                "timestamp": now_str,
                "time": "08:10",
                "type": "Clinical",
                "title": "Medication",
                "description": "Meropenem initiated.",
                "actor": "Nurse Kelly",
                "metadata": {"route": "IV", "dose": "1g"}
            },
            {
                "id": "mock-ev-3",
                "patient_id": "ICU-10248",
                "timestamp": now_str,
                "time": "08:40",
                "type": "Alerts",
                "title": "Hypotension Alert",
                "description": "Systolic Blood Pressure critically low: 82 mmHg",
                "actor": "System",
                "metadata": {"vitals": {"systolic_bp": 82, "diastolic_bp": 48}}
            }
        ]
        self._events["ICU-10251"] = [
            {
                "id": "mock-ev-4",
                "patient_id": "ICU-10251",
                "timestamp": now_str,
                "time": "09:15",
                "type": "Clinical",
                "title": "Admission",
                "description": "Patient admitted to Medical ICU.",
                "actor": "System",
                "metadata": {"diagnosis": "Pneumonia", "bed": "MICU-07"}
            },
            {
                "id": "mock-ev-5",
                "patient_id": "ICU-10251",
                "timestamp": now_str,
                "time": "09:30",
                "type": "Clinical",
                "title": "Assessment",
                "description": "Initial ICU vitals taken.",
                "actor": "Dr. Miller",
                "metadata": {"vitals": {"heart_rate": 108, "spo2": 95}}
            }
        ]
        self._events["ICU-10263"] = [
            {
                "id": "mock-ev-6",
                "patient_id": "ICU-10263",
                "timestamp": now_str,
                "time": "10:00",
                "type": "Clinical",
                "title": "Admission",
                "description": "Patient admitted to Medical ICU.",
                "actor": "System",
                "metadata": {"diagnosis": "Post-Op Monitoring", "bed": "MICU-11"}
            }
        ]

    def add_event(self, patient_id: str, event_type: str, title: str, description: str, actor: str = "System", metadata: dict = None) -> dict:
        now = datetime.now()
        event_id = f"ev-{str(uuid.uuid4())[:8]}"

        # Persist to PostgreSQL
        try:
            db = SessionLocal()
            try:
                db_event = DBTimelineEvent(
                    id=event_id,
                    patient_id=patient_id,
                    timestamp=now,
                    time=now.strftime("%H:%M"),
                    type=event_type,
                    title=title,
                    description=description,
                    actor=actor,
                    metadata_json=metadata or {}
                )
                db.add(db_event)
                db.commit()
            finally:
                db.close()
        except Exception:
            pass

        # In-memory backup
        if patient_id not in self._events:
            self._events[patient_id] = []
        event = {
            "id": event_id,
            "patient_id": patient_id,
            "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
            "time": now.strftime("%H:%M"),
            "type": event_type,
            "title": title,
            "description": description,
            "actor": actor,
            "metadata": metadata or {}
        }
        self._events[patient_id].insert(0, event)

        # Broadcast live timeline updates to WebSocket patient stream
        try:
            loop = asyncio.get_running_loop()
            if loop.is_running():
                asyncio.create_task(
                    ws_manager.broadcast_patient(
                        patient_id,
                        {
                            "type": "timeline_event",
                            "data": event,
                            "timestamp": event["timestamp"],
                        }
                    )
                )
        except RuntimeError:
            pass

        return event

    def get_patient_timeline(self, patient_id: str, event_type: str = None, search: str = None) -> list:
        try:
            db = SessionLocal()
            try:
                query = db.query(DBTimelineEvent).filter(DBTimelineEvent.patient_id == patient_id)
                if event_type and event_type.lower() != "all":
                    query = query.filter(DBTimelineEvent.type.ilike(event_type))
                if search:
                    term = f"%{search}%"
                    query = query.filter(
                        (DBTimelineEvent.title.ilike(term)) |
                        (DBTimelineEvent.description.ilike(term)) |
                        (DBTimelineEvent.actor.ilike(term))
                    )
                db_events = query.order_by(DBTimelineEvent.timestamp.desc()).all()
                if db_events:
                    return [
                        {
                            "id": ev.id,
                            "patient_id": ev.patient_id,
                            "timestamp": ev.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                            "time": ev.time,
                            "type": ev.type,
                            "title": ev.title,
                            "description": ev.description,
                            "actor": ev.actor,
                            "metadata": ev.metadata_json or {}
                        }
                        for ev in db_events
                    ]
            finally:
                db.close()
        except Exception:
            pass

        # Fallback to local memory cache
        patient_events = self._events.get(patient_id, [])

        filtered = []
        for e in patient_events:
            if event_type and event_type.lower() != "all":
                if e["type"].lower() != event_type.lower():
                    continue

            if search:
                term = search.lower()
                in_title = term in e["title"].lower()
                in_desc = term in e["description"].lower()
                in_actor = term in e["actor"].lower()
                if not (in_title or in_desc or in_actor):
                    continue

            filtered.append(e)

        return filtered

    def export_csv(self, patient_id: str, events: list) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["ID", "Timestamp", "Time", "Category", "Title", "Description", "Actor"])
        for e in events:
            writer.writerow([
                e["id"],
                e["timestamp"],
                e["time"],
                e["type"],
                e["title"],
                e["description"],
                e["actor"]
            ])
        return output.getvalue()

    def export_json(self, patient_id: str, events: list) -> str:
        return json.dumps(events, indent=2)

    def export_pdf(self, patient_id: str, events: list, patient_name: str = "Unknown") -> bytes:
        if REPORTLAB_AVAILABLE:
            buffer = io.BytesIO()
            p = canvas.Canvas(buffer, pagesize=letter)
            width, height = letter

            p.setFont("Helvetica-Bold", 18)
            p.drawString(40, height - 50, f"Clinical Timeline Report: {patient_name} ({patient_id})")
            
            p.setFont("Helvetica", 10)
            p.drawString(40, height - 70, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            p.line(40, height - 75, width - 40, height - 75)

            y = height - 100
            for idx, e in enumerate(events):
                if y < 60:
                    p.showPage()
                    p.setFont("Helvetica-Bold", 12)
                    p.drawString(40, height - 40, f"Clinical Timeline Report: {patient_name} - Page {p.getPageNumber()}")
                    p.line(40, height - 45, width - 40, height - 45)
                    y = height - 70

                p.setFont("Helvetica-Bold", 11)
                p.drawString(40, y, f"[{e['time']}] {e['title']} ({e['type']})")
                p.setFont("Helvetica-Oblique", 9)
                p.drawRightString(width - 40, y, f"Actor: {e['actor']}")
                
                y -= 15
                p.setFont("Helvetica", 10)
                p.drawString(50, y, e['description'])
                
                y -= 25

            p.save()
            return buffer.getvalue()
        else:
            output = io.StringIO()
            output.write(f"CLINICAL TIMELINE REPORT: {patient_name} ({patient_id})\n")
            output.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            output.write("="*60 + "\n\n")

            for e in events:
                output.write(f"[{e['timestamp']}] {e['title'].upper()} ({e['type']})\n")
                output.write(f"Actor: {e['actor']}\n")
                output.write(f"Description: {e['description']}\n")
                if e.get("metadata"):
                    output.write(f"Metadata: {json.dumps(e['metadata'])}\n")
                output.write("-" * 40 + "\n\n")

            return output.getvalue().encode("utf-8")

timeline_engine = TimelineEngine()
