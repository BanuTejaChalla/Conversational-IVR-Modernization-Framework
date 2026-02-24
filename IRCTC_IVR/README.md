# IRCTC Conversational IVR — Milestone 2: Backend Integration Layer

A FastAPI middleware that connects a Twilio telephony number to IRCTC-style railway services via keypad (DTMF) input.

---

## Project Structure

```
irctc_ivr/
├── main.py            # Module A — Webhook routing (FastAPI endpoints)
├── ivr_logic.py       # Module B — TwiML builders & menu structure
├── data_store.py      # Module C — Mock PNR & train schedule database
├── session_manager.py # In-memory session state tracker
├── requirements.txt
└── README.md
```

---

## Call Flow

```
User Dials Number
      │
      ▼
POST /voice ──────────────── Welcome + Main Menu
                                   │
              ┌────────────────────┤
              │                    │
         Press 1                Press 2
              │                    │
              ▼                    ▼
    POST /handle-menu        POST /handle-menu
              │                    │
              ▼                    ▼
  "Enter 10-digit PNR"   "Enter 5-digit Train No."
              │                    │
              ▼                    ▼
    POST /handle-pnr       POST /handle-train
              │                    │
              ▼                    ▼
     PNR Status Read        Train Schedule Read
              │                    │
              └────────┬───────────┘
                       ▼
             Option: Repeat / Main Menu / Goodbye
                       │
                  Press 9 / Goodbye
                       │
                       ▼
                    <Hangup/>
```

---

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the server

```bash
python main.py
# or
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Expose via ngrok

```bash
ngrok http 8000
```

Copy the HTTPS URL (e.g. `https://abc123.ngrok.io`) and configure it in your Twilio Console:

```
Voice Webhook → https://abc123.ngrok.io/voice   (HTTP POST)
```

---

## Twilio Configuration

| Setting | Value |
|---|---|
| **A Call Comes In** | Webhook → `POST https://<ngrok>/voice` |
| **Voice** | `Polly.Aditi` (Indian English) |
| **Input Digits** | PNR: `numDigits=10` / Train: `numDigits=5` |
| **Fallback** | `<Redirect>` to `/voice` on invalid input |

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/voice` | Entry point — greeting + main menu |
| `POST` | `/handle-menu` | Process main menu choice (1/2/9) |
| `POST` | `/handle-pnr` | Receive 10-digit PNR, return status |
| `POST` | `/handle-train` | Receive 5-digit train number, return schedule |
| `GET` | `/health` | Service health check |

---

## Sample TwiML Output

### `/voice`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Gather action="/handle-menu" method="POST" numDigits="1" timeout="10" finishOnKey="#">
        <Say voice="Polly.Aditi">Namaste! Welcome to I.R.C.T.C. Passenger Services.
            Press 1 for P.N.R. Status.
            Press 2 for Train Information.
            Press 9 to exit.</Say>
    </Gather>
    <Redirect method="POST">/voice</Redirect>
</Response>
```

### `/handle-pnr` (PNR found)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Aditi">P.N.R. number 2 1 5 4 6 7 3 8 9 0.
        Train: Rajdhani Express, number 12952.
        Status: Confirmed. Coach: A1, Berth: 23, Lower.
        Journey date: 25 February 2026.
        From New Delhi to Mumbai Central.</Say>
    <Pause length="1"/>
    <Gather action="/handle-pnr-options" method="POST" numDigits="1" timeout="10" finishOnKey="#">
        <Say voice="Polly.Aditi">To check another P.N.R., press 1.
            To return to the main menu, press 2. To exit, press 9.</Say>
    </Gather>
    <Redirect method="POST">/voice</Redirect>
</Response>
```

---

## Mock Data Available

### PNR Numbers (10-digit)

| PNR | Train | Status |
|---|---|---|
| `2154673890` | 12952 Rajdhani Express | Confirmed — A1/23L |
| `4521987630` | 12001 Shatabdi Express | Waitlisted WL4 |
| `7893214560` | 12213 Duronto Express | Confirmed — B3/47SU |
| `3347821905` | 22439 Vande Bharat | RAC 2 |
| `9012345678` | 12216 Garib Rath | Confirmed — GR3/12U |

### Train Numbers (5-digit)

| Number | Name | Route |
|---|---|---|
| `12952` | Mumbai Rajdhani Express | New Delhi → Mumbai Central |
| `12001` | Bhopal Shatabdi Express | New Delhi → Bhopal |
| `12213` | Patna Duronto Express | Patna → Mumbai LTT |
| `22439` | Vande Bharat Express | New Delhi → Varanasi |
| `12216` | Garib Rath Express | Chandigarh → Mumbai Bandra |

---

## Error Recovery

All invalid inputs return:
```xml
<Say voice="Polly.Aditi">Sorry, I did not understand your input. Please try again.</Say>
<Redirect method="POST">/voice</Redirect>
```

This **prevents abrupt hang-ups** by looping back to the welcome menu.

---

## Extending to Azure ACS

Replace TwiML strings in `ivr_logic.py` with Azure Communication Services call-control instructions. Set `AZURE_VOICE = "en-IN-NeerjaNeural"` as the TTS voice and use the ACS SDK's `play_media` / `recognize_dtmf` primitives.

---

## Success Metrics (Milestone 2)

- [x] Backend receives POST from Twilio's telephony cloud at `/voice`
- [x] System accurately retrieves PNR status from `data_store` based on user-entered digits
- [x] Call follows logical flow: **Welcome → Selection → Inquiry → Goodbye**
- [x] Invalid input redirects back to main menu (no hang-ups)
- [x] Indian English voice (`Polly.Aditi`) configured throughout
- [x] Session state tracked per `CallSid` across menu levels
