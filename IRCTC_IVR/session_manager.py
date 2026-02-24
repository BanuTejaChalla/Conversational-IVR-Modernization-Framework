"""
IRCTC Conversational IVR - Session Manager
Tracks the user's position and context across menu levels within a call.
In production, back this with Redis or another distributed store.
"""

import time
from typing import Optional

# Session TTL: discard stale sessions after 30 minutes
_SESSION_TTL_SECONDS = 30 * 60


class SessionManager:
    """
    In-memory key-value session store keyed by Twilio's CallSid.

    Session schema:
        created_at  : float          — Unix timestamp of creation
        updated_at  : float          — Unix timestamp of last update
        caller      : str | None     — Caller's phone number from Twilio
        flow        : str | None     — Current sub-flow ('pnr', 'train', …)
        last_menu   : str | None     — Last menu the caller was presented
        last_digit  : str | None     — Last digit(s) the caller pressed
        last_pnr    : str | None     — Most recently queried PNR
        last_train  : str | None     — Most recently queried train number
        ended       : bool           — Whether the call has ended
    """

    def __init__(self):
        self._store: dict[str, dict] = {}

    # ── Lifecycle ─────────────────────────────

    def create_session(self, call_sid: str, caller: Optional[str] = None) -> dict:
        """Initialise a new session for a call. Overwrites any stale session."""
        now = time.time()
        session = {
            "created_at": now,
            "updated_at": now,
            "caller":     caller,
            "flow":       None,
            "last_menu":  None,
            "last_digit": None,
            "last_pnr":   None,
            "last_train": None,
            "ended":      False,
        }
        self._store[call_sid] = session
        self._purge_stale()
        return session

    def get_session(self, call_sid: str) -> Optional[dict]:
        """Retrieve a session, or None if it does not exist / has expired."""
        session = self._store.get(call_sid)
        if session is None:
            return None
        if time.time() - session["updated_at"] > _SESSION_TTL_SECONDS:
            del self._store[call_sid]
            return None
        return session

    def update_session(self, call_sid: str, **kwargs) -> dict:
        """
        Update specific fields in an existing session.
        Creates a minimal session if one does not exist (graceful degradation).
        """
        session = self.get_session(call_sid)
        if session is None:
            session = self.create_session(call_sid)

        session.update(kwargs)
        session["updated_at"] = time.time()
        self._store[call_sid] = session
        return session

    def end_session(self, call_sid: str) -> None:
        """Mark a session as ended (caller hung up or said goodbye)."""
        session = self.get_session(call_sid)
        if session:
            session["ended"] = True
            session["updated_at"] = time.time()

    # ── Internal helpers ──────────────────────

    def _purge_stale(self) -> None:
        """Remove expired sessions to prevent unbounded memory growth."""
        cutoff = time.time() - _SESSION_TTL_SECONDS
        stale = [sid for sid, s in self._store.items() if s["updated_at"] < cutoff]
        for sid in stale:
            del self._store[sid]

    # ── Diagnostics ───────────────────────────

    def active_sessions(self) -> int:
        """Return the number of currently active (non-ended) sessions."""
        self._purge_stale()
        return sum(1 for s in self._store.values() if not s.get("ended"))
