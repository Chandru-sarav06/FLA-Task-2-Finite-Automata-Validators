"""Bounded-exhaustive + randomised verification against independent oracles.
Writes results/verification.json."""
import itertools, json, random, re, sys, time
sys.path.insert(0, ".")
from fla_validators.validators import *
from fla_validators.automata import equivalent

out = {}
PIN = build_pin()
t = time.time(); n = bad = 0
for L in range(0, 8):
    for tup in itertools.product("0123x", repeat=L):
        s = "".join(tup); n += 1
        bad += PIN.validate(s).ok != (s.isdigit() and len(s) in (4, 6))
out["pin"] = dict(strings=n, mismatches=bad, alphabet="0123x", max_len=7)

EM = build_email()
ER = re.compile(r"[a-z0-9]([._-]?[a-z0-9])*@([a-z0-9]+(-[a-z0-9]+)*\.)+(com|org|edu|net|in)", re.A)
n = bad = 0
for L in range(0, 7):
    for tup in itertools.product("a1.@-incom", repeat=L):
        s = "".join(tup); n += 1
        bad += EM.validate(s).ok != bool(ER.fullmatch(s))
out["email"] = dict(strings=n, mismatches=bad, alphabet="a1.@-incom", max_len=6)

PW = build_password()
PR = re.compile(r"(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#$%^&*])[A-Za-z0-9!@#$%^&*]{8,16}", re.A)
rep = {"a": "a", "A": "Q", "0": "7", "!": "@", "~": " "}
n = bad = 0
for L in range(0, 9):
    for tup in itertools.product("aA0!~", repeat=L):
        s = "".join(rep[c] for c in tup); n += 1
        bad += PW.validate(s).ok != bool(PR.fullmatch(s))
rnd = random.Random(2026); pool = "abcXYZ0159!@#$%^&* é_-"
rand_n = 200000
for _ in range(rand_n):
    s = "".join(rnd.choice(pool) for _ in range(rnd.randint(0, 20))); n += 1
    bad += PW.validate(s).ok != bool(PR.fullmatch(s))
out["password"] = dict(strings=n, mismatches=bad, note="all class strings len<=8 + 200000 random len<=20")

# machine sizes
nfa = build_email_nfa(); pin_nfa = build_pin_nfa()
comps = pw_component_dfas()
naive = 1
for d in comps.values(): naive *= len(d)
out["sizes"] = dict(
    pin_nfa=len(pin_nfa.states), pin_subset_dfa=len(pin_nfa.to_dfa()), pin_min=len(PIN.dfa),
    pin_with_denylist_min=len(build_pin(True).dfa),
    email_nfa=len(nfa.states), email_nfa_transitions=nfa.transition_count(),
    email_subset_dfa=len(nfa.to_dfa()), email_min=len(EM.dfa),
    password_components={k: len(v) for k, v in comps.items()},
    password_naive_product=naive, password_min=len(PW.dfa))
json.dump(out, open("results/verification.json", "w"), indent=2)
print(json.dumps(out, indent=2)); print("total mismatches:", sum(v["mismatches"] for k, v in out.items() if "mismatches" in v))
