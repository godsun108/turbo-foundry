"""Tenant-scoped parent call routing for authenticated forwarded call callbacks."""
import sqlite3
from dataclasses import dataclass
from .twilio_adapter import authenticate_twilio_voice_form

@dataclass(frozen=True)
class RoutingResult:
    accepted: bool
    reason: str
    tenant_id: str = ""

class ParentCallRouting:
    def __init__(self, db_path: str):
        self.db_path=db_path
        with self._connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS parent_routes (
                call_sid TEXT PRIMARY KEY, tenant_id TEXT NOT NULL,
                destination TEXT NOT NULL)""")
            db.execute("""CREATE TABLE IF NOT EXISTS child_routes (
                call_sid TEXT PRIMARY KEY, parent_sid TEXT NOT NULL,
                tenant_id TEXT NOT NULL)""")

    def _connect(self):
        return sqlite3.connect(self.db_path,timeout=10)

    def register_parent(self, *, tenant_id: str, provisioned_number: str,
                        url: str, params: dict, signature: str,
                        auth_token: str, validator=None) -> RoutingResult:
        call=authenticate_twilio_voice_form(url,params,signature,auth_token,validator=validator)
        if call is None: return RoutingResult(False,"invalid_signature")
        if not tenant_id or call.destination!=provisioned_number or params.get("ParentCallSid"):
            return RoutingResult(False,"invalid_parent_route")
        with self._connect() as db:
            existing=db.execute("SELECT tenant_id,destination FROM parent_routes WHERE call_sid=?",
                                (call.call_sid,)).fetchone()
            if existing:
                return RoutingResult(existing==(tenant_id,provisioned_number),
                                     "existing_parent" if existing==(tenant_id,provisioned_number) else "parent_conflict",
                                     tenant_id if existing==(tenant_id,provisioned_number) else "")
            db.execute("INSERT INTO parent_routes VALUES(?,?,?)",(call.call_sid,tenant_id,provisioned_number))
        return RoutingResult(True,"parent_registered",tenant_id)

    def route_child(self, *, url: str, params: dict, signature: str,
                    auth_token: str, validator=None) -> RoutingResult:
        call=authenticate_twilio_voice_form(url,params,signature,auth_token,validator=validator)
        if call is None: return RoutingResult(False,"invalid_signature")
        parent=params.get("ParentCallSid","")
        if not parent or not parent.startswith("CA") or len(parent)!=34 or parent==call.call_sid:
            return RoutingResult(False,"invalid_parent_sid")
        with self._connect() as db:
            route=db.execute("SELECT tenant_id FROM parent_routes WHERE call_sid=?",(parent,)).fetchone()
            if not route: return RoutingResult(False,"unknown_parent")
            existing=db.execute("SELECT parent_sid,tenant_id FROM child_routes WHERE call_sid=?",
                                (call.call_sid,)).fetchone()
            if existing:
                return RoutingResult(existing==(parent,route[0]),
                                     "existing_child" if existing==(parent,route[0]) else "child_conflict",
                                     route[0] if existing==(parent,route[0]) else "")
            db.execute("INSERT INTO child_routes VALUES(?,?,?)",(call.call_sid,parent,route[0]))
            return RoutingResult(True,"child_routed",route[0])
