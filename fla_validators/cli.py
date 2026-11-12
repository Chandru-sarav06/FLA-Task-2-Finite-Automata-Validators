"""Usage:  python -m fla_validators.cli pin 4829
          python -m fla_validators.cli email alice.k@srmist.edu.in --trace
          python -m fla_validators.cli password 'Chandru@2026'
"""
import argparse
import sys

from .validators import build_pin, build_email, build_password
from . import semantic


def main(argv=None):
    ap = argparse.ArgumentParser(prog="fla_validators")
    ap.add_argument("kind", choices=["pin", "email", "password"])
    ap.add_argument("text")
    ap.add_argument("--trace", action="store_true", help="print every DFA transition")
    ap.add_argument("--semantic", action="store_true", help="also run the semantic layer if syntax passes")
    a = ap.parse_args(argv)
    v = {"pin": build_pin, "email": build_email, "password": build_password}[a.kind]()
    res = v.validate(a.text)
    print(f"[{v.name}] rule: {v.rule_text}")
    print(f"  states in minimal DFA : {len(v.dfa)}")
    print(f"  syntax verdict        : {'ACCEPT' if res.ok else 'REJECT'} - {res.reason}")
    if a.trace:
        for i, (q, s, r) in enumerate(res.path):
            print(f"    step {i + 1:>2}: q{q} --{s}--> q{r}")
    if a.semantic and res.ok:
        if a.kind == "pin":
            print("  semantic verdict      :", *semantic.pin_semantics(a.text))
        elif a.kind == "email":
            print("  semantic verdict      :", *semantic.email_semantics(a.text, {"demo@srmist.edu.in"}))
        else:
            print("  semantic verdict      :", *semantic.password_semantics(a.text, "chandru", []))
    return 0 if res.ok else 1


if __name__ == "__main__":
    sys.exit(main())
