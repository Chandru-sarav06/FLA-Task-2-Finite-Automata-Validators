"""Semantic / business rules. These need data the automaton does not have,
so they run only AFTER the syntax DFA has accepted the string."""
from __future__ import annotations

WEAK_PINS = {"0000", "1111", "2222", "3333", "4444", "5555", "6666", "7777", "8888", "9999",
             "1234", "4321", "0123", "3210"}
BREACHED = {"Password@123", "Welcome@2024", "Qwerty@12345"}


def pin_semantics(pin: str, birth_year: str | None = None, failed_attempts: int = 0):
    if failed_attempts >= 3:
        return False, "card blocked: three wrong attempts (state held by the bank, not by an automaton)"
    if pin in WEAK_PINS:
        return False, "weak PIN (deny-list lookup)"
    if birth_year and birth_year in pin:
        return False, "PIN contains the holder's birth year (needs customer record)"
    return True, "PIN acceptable"


def email_semantics(address: str, registered: set[str]):
    if address.lower() in registered:
        return False, "address already registered (database lookup)"
    return True, "address available (MX / deliverability still unchecked)"


def password_semantics(pw: str, username: str, history: list[str]):
    if username and username.lower() in pw.lower():
        return False, "password contains the username"
    if pw in BREACHED:
        return False, "password appears in a breached-password list"
    if pw in history:
        return False, "password was used before"
    return True, "password acceptable"
