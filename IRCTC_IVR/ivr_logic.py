"""
IRCTC Conversational IVR - Module B: Logic Engine
Defines menu structure and TwiML response builders.

Voice: en-IN (Polly.Aditi for Twilio / en-IN-NeerjaNeural for Azure)
"""

from typing import Optional

# ─────────────────────────────────────────────
# Voice configuration
# ─────────────────────────────────────────────
TWILIO_VOICE = "Polly.Aditi"   # Indian English — Amazon Polly via Twilio
AZURE_VOICE  = "en-IN-NeerjaNeural"  # Indian English — Azure Cognitive Services

# ─────────────────────────────────────────────
# Dictionary-based menu structure
# ─────────────────────────────────────────────
MENU_STRUCTURE = {
    "main": {
        "prompt": (
            "Welcome to I.R.C.T.C. Passenger Services. "
            "Press 1 for P.N.R. Status. "
            "Press 2 for Train Information. "
            "Press 9 to exit."
        ),
        "options": {
            "1": "pnr_gather",
            "2": "train_gather",
            "9": "goodbye",
        },
        "action": "/handle-menu",
        "num_digits": 1,
    },
    "pnr_gather": {
        "prompt": (
            "Please enter your 10-digit P.N.R. number, followed by the hash key."
        ),
        "action": "/handle-pnr",
        "num_digits": 10,
    },
    "train_gather": {
        "prompt": (
            "Please enter the 5-digit train number, followed by the hash key."
        ),
        "action": "/handle-train",
        "num_digits": 5,
    },
}


# ─────────────────────────────────────────────
# Internal helper
# ─────────────────────────────────────────────
def _xml_escape(text: str) -> str:
    """Minimal XML escaping for TwiML Say bodies."""
    return (
        text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
    )


def _say(text: str, voice: str = TWILIO_VOICE) -> str:
    """Return a TwiML <Say> element."""
    return f'<Say voice="{voice}">{_xml_escape(text)}</Say>'


def _pause(length: int = 1) -> str:
    """Return a TwiML <Pause> element."""
    return f'<Pause length="{length}"/>'


def _gather(
    action: str,
    num_digits: int,
    timeout: int = 10,
    finish_on_key: str = "#",
    inner_xml: str = "",
) -> str:
    """Return a TwiML <Gather> element."""
    return (
        f'<Gather action="{action}" method="POST" '
        f'numDigits="{num_digits}" timeout="{timeout}" '
        f'finishOnKey="{finish_on_key}">'
        f"{inner_xml}"
        f"</Gather>"
    )


def _redirect(url: str) -> str:
    """Return a TwiML <Redirect> element."""
    return f'<Redirect method="POST">{url}</Redirect>'


def _twiml_response(*elements: str) -> str:
    """Wrap elements in a TwiML <Response> envelope."""
    body = "\n    ".join(elements)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        "<Response>\n"
        f"    {body}\n"
        "</Response>"
    )


# ─────────────────────────────────────────────
# Public TwiML builder functions
# ─────────────────────────────────────────────

def build_welcome_twiml() -> str:
    """
    Entry greeting followed immediately by the main menu Gather.
    Keeps the call alive; no abrupt hang-up on silence.
    """
    menu = MENU_STRUCTURE["main"]
    welcome_say = _say(
        "Namaste! " + menu["prompt"]
    )
    gather = _gather(
        action=menu["action"],
        num_digits=menu["num_digits"],
        inner_xml=welcome_say,
    )
    # Fallback: if no input, redirect back to entry
    redirect = _redirect("/voice")
    return _twiml_response(gather, redirect)


def build_main_menu_twiml() -> str:
    """Standalone main menu (used after returning from a sub-flow)."""
    menu = MENU_STRUCTURE["main"]
    say = _say(menu["prompt"])
    gather = _gather(
        action=menu["action"],
        num_digits=menu["num_digits"],
        inner_xml=say,
    )
    redirect = _redirect("/voice")
    return _twiml_response(gather, redirect)


def build_pnr_gather_twiml() -> str:
    """Prompt the user to enter their 10-digit PNR."""
    menu = MENU_STRUCTURE["pnr_gather"]
    say = _say(menu["prompt"])
    gather = _gather(
        action=menu["action"],
        num_digits=menu["num_digits"],
        inner_xml=say,
    )
    redirect = _redirect("/voice")
    return _twiml_response(gather, redirect)


def build_pnr_result_twiml(pnr: str, result: Optional[dict]) -> str:
    """
    Read back PNR status details.
    After reading, offer the main menu again or goodbye.
    """
    if result:
        spaced_pnr = " ".join(pnr)  # e.g. "1 2 3 4..." for clearer speech
        status_text = (
            f"P.N.R. number {spaced_pnr}. "
            f"Train: {result['train_name']}, number {result['train_number']}. "
            f"Status: {result['status']}. "
            f"Coach: {result['coach']}, Berth: {result['berth']}. "
            f"Journey date: {result['journey_date']}. "
            f"From {result['from_station']} to {result['to_station']}."
        )
    else:
        status_text = (
            f"Sorry, no record was found for the P.N.R. number you entered. "
            "Please check the number and try again."
        )

    result_say  = _say(status_text)
    options_say = _say(
        "To check another P.N.R., press 1. "
        "To return to the main menu, press 2. "
        "To exit, press 9."
    )
    gather = _gather(
        action="/handle-pnr-options",
        num_digits=1,
        inner_xml=options_say,
    )
    redirect = _redirect("/voice")
    return _twiml_response(result_say, _pause(), gather, redirect)


def build_train_gather_twiml() -> str:
    """Prompt the user to enter a 5-digit train number."""
    menu = MENU_STRUCTURE["train_gather"]
    say = _say(menu["prompt"])
    gather = _gather(
        action=menu["action"],
        num_digits=menu["num_digits"],
        inner_xml=say,
    )
    redirect = _redirect("/voice")
    return _twiml_response(gather, redirect)


def build_train_result_twiml(train_number: str, result: Optional[dict]) -> str:
    """Read back train schedule information."""
    if result:
        stops_text = ". ".join(
            f"Halt {i+1}: {s['station']}, arrives {s['arrival']}, departs {s['departure']}"
            for i, s in enumerate(result.get("stops", []))
        )
        train_text = (
            f"Train number {train_number}, {result['name']}. "
            f"Runs from {result['source']} to {result['destination']}. "
            f"Departure: {result['departure']}. Arrival: {result['arrival']}. "
            f"Days of operation: {result['days']}. "
            + (f"Schedule: {stops_text}." if stops_text else "")
        )
    else:
        train_text = (
            "Sorry, no information was found for the train number you entered. "
            "Please verify the number and try again."
        )

    result_say  = _say(train_text)
    options_say = _say(
        "To check another train, press 1. "
        "To return to the main menu, press 2. "
        "To exit, press 9."
    )
    gather = _gather(
        action="/handle-train-options",
        num_digits=1,
        inner_xml=options_say,
    )
    redirect = _redirect("/voice")
    return _twiml_response(result_say, _pause(), gather, redirect)


def build_invalid_input_twiml(redirect_to: str = "/voice") -> str:
    """
    Inform the user of invalid input and loop back to a given endpoint.
    Prevents abrupt hang-up per spec §Error Recovery.
    """
    say = _say(
        "Sorry, I did not understand your input. Please try again."
    )
    redirect = _redirect(redirect_to)
    return _twiml_response(say, _pause(), redirect)


def build_goodbye_twiml() -> str:
    """Thank the caller and hang up gracefully."""
    say = _say(
        "Thank you for using I.R.C.T.C. Passenger Services. "
        "Have a comfortable journey. Goodbye!"
    )
    hangup = "<Hangup/>"
    return _twiml_response(say, hangup)
