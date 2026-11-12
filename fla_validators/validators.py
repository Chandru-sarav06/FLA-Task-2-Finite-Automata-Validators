"""Three syntax validators built on the automata toolkit:
   1. ATM PIN   2. E-mail address   3. Password policy
Each validator = classifier (char -> alphabet symbol) + minimal DFA."""
from __future__ import annotations

from dataclasses import dataclass, field

from .automata import DFA, regex_to_nfa, intersect_all, regex_to_dfa, from_finite_language, product

OTHER = "~"   # any character outside the policy's alphabet


@dataclass
class Result:
    ok: bool
    reason: str
    path: list = field(default_factory=list)   # [(state, symbol, next_state)]


class Validator:
    def __init__(self, name, dfa: DFA, classify, rule_text):
        self.name, self.dfa, self.classify, self.rule_text = name, dfa, classify, rule_text
        self._dead = dfa.dead_states()

    def validate(self, text: str) -> Result:
        word = [self.classify(c) for c in text]
        path = self.dfa.trace(word)
        for i, (q, a, r) in enumerate(path):
            if r in self._dead:
                return Result(False, f"rejected at position {i + 1} ({text[i]!r}): no continuation can make the input valid", path)
        end = self.dfa.run(word)
        if end in self.dfa.accepting:
            return Result(True, "accepted: final state is accepting", path)
        return Result(False, f"input ended in non-accepting state q{end} (a valid completion still exists, e.g. input is too short or missing a required part)", path)


# ------------------------------------------------------------------ 1. ATM PIN
PIN_ALPHABET = set("0123456789") | {OTHER}
WEAK_PINS = [d * 4 for d in "0123456789"] + ["1234", "4321", "0123", "3210"]


def _pin_classify(c):
    return c if c in "0123456789" else OTHER


def build_pin_nfa():
    return regex_to_nfa("[0-9]{4}|[0-9]{6}", PIN_ALPHABET, "ATM PIN")


def build_pin(with_denylist=False) -> Validator:
    dfa = build_pin_nfa().to_dfa().minimize()
    if with_denylist:
        weak = from_finite_language(WEAK_PINS, PIN_ALPHABET)
        dfa = product(dfa, weak.complement(), "and").minimize()
    return Validator("ATM PIN" + (" + deny-list" if with_denylist else ""), dfa, _pin_classify,
                     "4 or 6 decimal digits")


# ------------------------------------------------------------------ 2. e-mail
EMAIL_ALPHABET = set("abcdefghijklmnopqrstuvwxyz0123456789") | set("._-@") | {OTHER}
EMAIL_REGEX = (r"[a-z0-9](([._-])?[a-z0-9])*@"
               r"([a-z0-9]+(-[a-z0-9]+)*\.)+(com|org|edu|net|in)")
TLD_REGEX = "com|org|edu|net|in"


def _email_classify(c):
    c = c.lower()
    return c if c in EMAIL_ALPHABET and c != OTHER else OTHER


def build_email_nfa():
    return regex_to_nfa(EMAIL_REGEX, EMAIL_ALPHABET, "E-mail")


def build_email() -> Validator:
    return Validator("E-mail", build_email_nfa().to_dfa().minimize(), _email_classify,
                     "local@domain.tld : alphanumeric ends, single . _ - separators, tld in {com,org,edu,net,in}")


# ------------------------------------------------------------------ 3. password
PW_ALPHABET = set("aA0!") | {OTHER}
SPECIALS = "!@#$%^&*"
PW_REGEXES = {
    "length 8-16": ".{8,16}",
    "only allowed symbols": "[aA0!]*",
    "has lowercase": ".*a.*",
    "has uppercase": ".*A.*",
    "has digit": ".*0.*",
    "has special": ".*!.*",
}


def _pw_classify(c):
    if c.isascii() and c.islower():
        return "a"
    if c.isascii() and c.isupper():
        return "A"
    if c.isascii() and c.isdigit():
        return "0"
    if c in SPECIALS:
        return "!"
    return OTHER


def pw_component_dfas():
    return {k: regex_to_dfa(v, PW_ALPHABET, k) for k, v in PW_REGEXES.items()}


def build_password() -> Validator:
    comps = list(pw_component_dfas().values())
    return Validator("Password", intersect_all(comps), _pw_classify,
                     "8-16 chars from [A-Za-z0-9!@#$%^&*] with >=1 lower, upper, digit, special")
