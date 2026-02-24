"""
IRCTC Conversational IVR - Module C: Data Source
Mock database for PNR records and train schedules.

In production, replace the dictionary lookups with actual DB / IRCTC API calls.
"""

from typing import Optional

# ─────────────────────────────────────────────
# Mock PNR Database
# Keys are 10-digit PNR strings.
# ─────────────────────────────────────────────
_PNR_DB: dict[str, dict] = {
    "2154673890": {
        "pnr":           "2154673890",
        "train_name":    "Rajdhani Express",
        "train_number":  "12952",
        "from_station":  "New Delhi",
        "to_station":    "Mumbai Central",
        "journey_date":  "25 February 2026",
        "status":        "Confirmed",
        "coach":         "A1",
        "berth":         "23, Lower",
        "passenger":     "Mr. Ramesh Sharma",
        "class":         "1A",
    },
    "4521987630": {
        "pnr":           "4521987630",
        "train_name":    "Shatabdi Express",
        "train_number":  "12001",
        "from_station":  "Bhopal Junction",
        "to_station":    "New Delhi",
        "journey_date":  "26 February 2026",
        "status":        "Waitlisted — WL 4",
        "coach":         "Not Assigned",
        "berth":         "Not Assigned",
        "passenger":     "Ms. Priya Verma",
        "class":         "CC",
    },
    "7893214560": {
        "pnr":           "7893214560",
        "train_name":    "Duronto Express",
        "train_number":  "12213",
        "from_station":  "Patna Junction",
        "to_station":    "Mumbai LTT",
        "journey_date":  "28 February 2026",
        "status":        "Confirmed",
        "coach":         "B3",
        "berth":         "47, Side Upper",
        "passenger":     "Mr. Anil Kumar",
        "class":         "SL",
    },
    "3347821905": {
        "pnr":           "3347821905",
        "train_name":    "Vande Bharat Express",
        "train_number":  "22439",
        "from_station":  "Varanasi Junction",
        "to_station":    "New Delhi",
        "journey_date":  "27 February 2026",
        "status":        "RAC — RAC 2",
        "coach":         "C1",
        "berth":         "RAC 2",
        "passenger":     "Dr. Sunita Patel",
        "class":         "CC",
    },
    "9012345678": {
        "pnr":           "9012345678",
        "train_name":    "Garib Rath Express",
        "train_number":  "12216",
        "from_station":  "Chandigarh",
        "to_station":    "Mumbai Bandra Terminus",
        "journey_date":  "01 March 2026",
        "status":        "Confirmed",
        "coach":         "GR-3",
        "berth":         "12, Upper",
        "passenger":     "Mr. Vikas Singh",
        "class":         "3A",
    },
}


# ─────────────────────────────────────────────
# Mock Train Schedule Database
# Keys are 5-digit train number strings.
# ─────────────────────────────────────────────
_TRAIN_DB: dict[str, dict] = {
    "12952": {
        "number":      "12952",
        "name":        "Mumbai Rajdhani Express",
        "source":      "New Delhi",
        "destination": "Mumbai Central",
        "departure":   "4:55 PM",
        "arrival":     "8:35 AM (next day)",
        "days":        "Monday, Wednesday, Friday, Saturday",
        "duration":    "15 hours 40 minutes",
        "stops": [
            {"station": "Kota Junction",   "arrival": "9:40 PM",  "departure": "9:45 PM"},
            {"station": "Vadodara Junction","arrival": "4:20 AM",  "departure": "4:25 AM"},
            {"station": "Surat",           "arrival": "5:55 AM",  "departure": "5:57 AM"},
        ],
    },
    "12001": {
        "number":      "12001",
        "name":        "Bhopal Shatabdi Express",
        "source":      "New Delhi",
        "destination": "Bhopal Junction",
        "departure":   "6:00 AM",
        "arrival":     "2:30 PM",
        "days":        "Daily except Tuesday",
        "duration":    "8 hours 30 minutes",
        "stops": [
            {"station": "Agra Cantt",      "arrival": "8:19 AM",  "departure": "8:22 AM"},
            {"station": "Gwalior",         "arrival": "9:27 AM",  "departure": "9:29 AM"},
            {"station": "Jhansi",          "arrival": "10:29 AM", "departure": "10:32 AM"},
            {"station": "Lalitpur",        "arrival": "11:05 AM", "departure": "11:07 AM"},
        ],
    },
    "12213": {
        "number":      "12213",
        "name":        "Patna Duronto Express",
        "source":      "Patna Junction",
        "destination": "Mumbai LTT",
        "departure":   "3:30 PM",
        "arrival":     "10:00 AM (next day)",
        "days":        "Tuesday, Thursday, Sunday",
        "duration":    "18 hours 30 minutes",
        "stops": [],  # Duronto — no intermediate commercial halts
    },
    "22439": {
        "number":      "22439",
        "name":        "Vande Bharat Express",
        "source":      "New Delhi",
        "destination": "Varanasi Junction",
        "departure":   "8:00 AM",
        "arrival":     "2:00 PM",
        "days":        "Daily except Wednesday",
        "duration":    "8 hours",
        "stops": [
            {"station": "Prayagraj Junction","arrival": "12:48 PM", "departure": "12:50 PM"},
        ],
    },
    "12216": {
        "number":      "12216",
        "name":        "Garib Rath Express",
        "source":      "Chandigarh",
        "destination": "Mumbai Bandra Terminus",
        "departure":   "9:10 PM",
        "arrival":     "11:50 PM (next day)",
        "days":        "Monday, Friday",
        "duration":    "26 hours 40 minutes",
        "stops": [
            {"station": "Ambala Cantt",    "arrival": "10:09 PM", "departure": "10:12 PM"},
            {"station": "New Delhi",       "arrival": "12:55 AM", "departure": "1:10 AM"},
            {"station": "Mathura Junction","arrival": "3:00 AM",  "departure": "3:02 AM"},
            {"station": "Kota Junction",   "arrival": "7:15 AM",  "departure": "7:18 AM"},
            {"station": "Vadodara Junction","arrival": "3:40 PM",  "departure": "3:45 PM"},
        ],
    },
}


# ─────────────────────────────────────────────
# Public data-access functions
# ─────────────────────────────────────────────

def get_pnr_status(pnr: str) -> Optional[dict]:
    """
    Look up a PNR record by its 10-digit number.

    Args:
        pnr: Exactly 10 numeric characters.

    Returns:
        A dict with booking details, or None if not found.
    """
    return _PNR_DB.get(pnr.strip())


def get_train_info(train_number: str) -> Optional[dict]:
    """
    Look up a train schedule by its 5-digit number.

    Args:
        train_number: Exactly 5 numeric characters.

    Returns:
        A dict with schedule details, or None if not found.
    """
    return _TRAIN_DB.get(train_number.strip())


def list_all_pnrs() -> list[str]:
    """Return all known PNR numbers (useful for testing)."""
    return list(_PNR_DB.keys())


def list_all_trains() -> list[str]:
    """Return all known train numbers (useful for testing)."""
    return list(_TRAIN_DB.keys())
