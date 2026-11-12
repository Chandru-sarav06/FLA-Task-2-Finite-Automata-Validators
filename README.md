# FLA Task 2 - Finite Automata for Real-Time Input Validation

**CLA-2, Task 2 - 21CSC301T Formal Language and Automata (SRM IST, Tiruchirappalli)**
Author: **Chandru M S** (RA2411026050028) - individual work

Three validation applications modelled as regular languages and implemented from scratch
(no regex engine is used for the validators themselves):

| Application | Language | Technique |
|---|---|---|
| ATM PIN | exactly 4 or 6 decimal digits | regex -> epsilon-NFA (Thompson) -> subset DFA -> minimal DFA |
| E-mail address | `local@domain.tld`, no leading/trailing/double separators, tld in {com, org, edu, net, in} | epsilon-NFA with 82 states -> 32 subset states -> 16 minimal states |
| Password policy | 8-16 chars, only `[A-Za-z0-9!@#$%^&*]`, >=1 lower, upper, digit, special | **intersection (product) of six DFAs**, then minimised |

Syntax (automaton) vs semantics (database / policy) is separated: see `fla_validators/semantic.py`.

## Run
```bash
pip install -r requirements.txt
python -m fla_validators.cli pin 4829 --trace
python -m fla_validators.cli email chandru.ms@srmist.edu.in --semantic
python -m fla_validators.cli password 'Chandru@2026' --trace
python -m pytest -q                 # 52 tests
python tools/verify.py              # ~1.9 M strings vs independent oracles -> results/verification.json
python tools/make_figures.py        # needs Graphviz `dot` on PATH
```

## Layout
```
fla_validators/automata.py    DFA, eps-NFA, regex parser, Thompson, subset construction, Moore minimisation, product, equivalence
fla_validators/validators.py  the three validators (classifier + minimal DFA + explanations)
fla_validators/semantic.py    business rules that a finite automaton cannot express
fla_validators/cli.py         demo CLI
tests/                        >=5 accepted and >=5 rejected examples per application + oracle tests
tools/verify.py, make_figures.py
results/verification.json     numbers quoted in the report
docs/figures/                 DFA/NFA diagrams (PNG + Graphviz .dot)
```

## Verified results (from `results/verification.json`)
* PIN: 97,656 strings (alphabet `0123x`, length <= 7) - 0 mismatches
* E-mail: 1,111,111 strings (10 symbols, length <= 6) vs Python `re` - 0 mismatches
* Password: 688,281 strings (all class strings <= 8 + 200,000 random) vs look-ahead `re` - 0 mismatches
* Product construction: naive product of component sizes 576, minimal DFA 197 states.

Assumption: e-mail input is case-normalised (lower-cased) before the automaton runs.
