"""
IRCTC Conversational IVR - Module A: Webhook Routing
FastAPI middleware layer connecting Twilio telephony to IRCTC logic.
"""

from fastapi import FastAPI, Form, Request
from fastapi.responses import Response
from typing import Optional
import uvicorn

from ivr_logic import (
    build_welcome_twiml,
    build_main_menu_twiml,
    build_pnr_gather_twiml,
    build_pnr_result_twiml,
    build_train_gather_twiml,
    build_train_result_twiml,
    build_invalid_input_twiml,
    build_goodbye_twiml,
)
from session_manager import SessionManager

app = FastAPI(title="IRCTC IVR Backend", version="1.0.0")
session_manager = SessionManager()


# ─────────────────────────────────────────────
# POST /voice  — Entry point (Twilio webhook)
# ─────────────────────────────────────────────
@app.post("/voice")
async def voice_entry(
    CallSid: Optional[str] = Form(None),
    From: Optional[str] = Form(None),
):
    """
    Twilio calls this endpoint when a user dials the number.
    Greets the caller and presents the main menu.
    """
    call_sid = CallSid or "unknown"

    # Initialise a fresh session for this call
    session_manager.create_session(call_sid, caller=From)

    twiml = build_welcome_twiml()
    return Response(content=twiml, media_type="application/xml")


# ─────────────────────────────────────────────
# POST /handle-menu  — Main menu choice
# ─────────────────────────────────────────────
@app.post("/handle-menu")
async def handle_menu(
    CallSid: Optional[str] = Form(None),
    Digits: Optional[str] = Form(None),
):
    """
    Processes the caller's top-level menu choice:
        1 → PNR Status inquiry
        2 → Train Schedule / Info inquiry
        9 → Goodbye
    """
    call_sid = CallSid or "unknown"
    digits = (Digits or "").strip()

    session_manager.update_session(call_sid, last_menu="main", last_digit=digits)

    if digits == "1":
        session_manager.update_session(call_sid, flow="pnr")
        twiml = build_pnr_gather_twiml()

    elif digits == "2":
        session_manager.update_session(call_sid, flow="train")
        twiml = build_train_gather_twiml()

    elif digits == "9":
        session_manager.end_session(call_sid)
        twiml = build_goodbye_twiml()

    else:
        # Invalid input → redirect back to main menu
        twiml = build_invalid_input_twiml(redirect_to="/voice")

    return Response(content=twiml, media_type="application/xml")


# ─────────────────────────────────────────────
# POST /handle-pnr  — PNR digits received
# ─────────────────────────────────────────────
@app.post("/handle-pnr")
async def handle_pnr(
    CallSid: Optional[str] = Form(None),
    Digits: Optional[str] = Form(None),
):
    """
    Receives a 10-digit PNR number, queries the mock data store,
    and reads back the booking status, coach, and berth.
    """
    from data_store import get_pnr_status

    call_sid = CallSid or "unknown"
    pnr = (Digits or "").strip()

    if len(pnr) != 10 or not pnr.isdigit():
        twiml = build_invalid_input_twiml(redirect_to="/voice")
        return Response(content=twiml, media_type="application/xml")

    session_manager.update_session(call_sid, last_pnr=pnr)
    result = get_pnr_status(pnr)
    twiml = build_pnr_result_twiml(pnr, result)
    return Response(content=twiml, media_type="application/xml")


# ─────────────────────────────────────────────
# POST /handle-train  — Train number received
# ─────────────────────────────────────────────
@app.post("/handle-train")
async def handle_train(
    CallSid: Optional[str] = Form(None),
    Digits: Optional[str] = Form(None),
):
    """
    Receives a 5-digit train number, queries the mock data store,
    and reads back the train schedule.
    """
    from data_store import get_train_info

    call_sid = CallSid or "unknown"
    train_number = (Digits or "").strip()

    if len(train_number) != 5 or not train_number.isdigit():
        twiml = build_invalid_input_twiml(redirect_to="/voice")
        return Response(content=twiml, media_type="application/xml")

    session_manager.update_session(call_sid, last_train=train_number)
    result = get_train_info(train_number)
    twiml = build_train_result_twiml(train_number, result)
    return Response(content=twiml, media_type="application/xml")


# ─────────────────────────────────────────────
# POST /handle-pnr-options  — After PNR result
# ─────────────────────────────────────────────
@app.post("/handle-pnr-options")
async def handle_pnr_options(
    CallSid: Optional[str] = Form(None),
    Digits: Optional[str] = Form(None),
):
    digits = (Digits or "").strip()

    if digits == "1":
        twiml = build_pnr_gather_twiml()
    elif digits == "2":
        twiml = build_main_menu_twiml()
    elif digits == "9":
        session_manager.end_session(CallSid or "unknown")
        twiml = build_goodbye_twiml()
    else:
        twiml = build_invalid_input_twiml(redirect_to="/voice")

    return Response(content=twiml, media_type="application/xml")


# ─────────────────────────────────────────────
# POST /handle-train-options — After train result
# ─────────────────────────────────────────────
@app.post("/handle-train-options")
async def handle_train_options(
    CallSid: Optional[str] = Form(None),
    Digits: Optional[str] = Form(None),
):
    digits = (Digits or "").strip()

    if digits == "1":
        twiml = build_train_gather_twiml()
    elif digits == "2":
        twiml = build_main_menu_twiml()
    elif digits == "9":
        session_manager.end_session(CallSid or "unknown")
        twiml = build_goodbye_twiml()
    else:
        twiml = build_invalid_input_twiml(redirect_to="/voice")

    return Response(content=twiml, media_type="application/xml")


# ─────────────────────────────────────────────
# Health check
# ─────────────────────────────────────────────
@app.get("/health")
async def health():
    return {"status": "ok", "service": "IRCTC IVR Backend", "version": "1.0.0"}


# ─────────────────────────────────────────────
# Dev server entry point
# ─────────────────────────────────────────────
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
