"""
Event tracer and logger for GUARDIAN-AGENT.
Records every step for observability.
"""
import os
import json
import time
from dataclasses import dataclass, asdict
from typing import Optional, List
from security.privacy import scrub_text

@dataclass
class TraceEvent:
    step: int
    timestamp: float
    event_type: str # REASON, ACTION, OBSERVATION
    content: str
    status: Optional[str] = "OK"
    tokens: Optional[int] = 0

class Tracer:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.filename = f"trace_{session_id}.json"
        self.events: List[TraceEvent] = []
        self._load_existing()

    def _load_existing(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r") as f:
                    data = json.load(f)
                    self.events = [TraceEvent(**e) for e in data]
            except Exception as e:
                print(f"⚠️ TRACER LOAD ERROR: {e}")

    def log(self, event_type: str, content: str, step: int, status: str = "OK", tokens: int = 0):
        # SECURITY: Scrub sensitive info before logging
        safe_content = scrub_text(content)
        
        event = TraceEvent(
            step=step,
            timestamp=time.time(),
            event_type=event_type,
            content=safe_content,
            status=status,
            tokens=tokens
        )
        self.events.append(event)
        self._save()

    def _save(self):
        with open(self.filename, "w") as f:
            json.dump([asdict(e) for e in self.events], f, indent=2)

    @classmethod
    def load_session(cls, session_id: str):
        filename = f"trace_{session_id}.json"
        try:
            with open(filename, "r") as f:
                return json.load(f)
        except:
            return []
