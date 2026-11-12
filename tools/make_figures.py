import json, subprocess, sys
sys.path.insert(0, ".")
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from fla_validators.validators import *
from fla_validators.automata import to_dot, nfa_to_dot, regex_to_nfa

FIG = "docs/figures/"
def render(dot, name, dpi=150):
    open(FIG + name + ".dot", "w").write(dot)
    subprocess.run(["dot", "-Tpng", f"-Gdpi={dpi}", FIG + name + ".dot", "-o", FIG + name + ".png"], check=True)

render(to_dot(build_pin().dfa), "fig1_pin_dfa")
render(to_dot(build_email().dfa), "fig2_email_dfa")
tld = regex_to_nfa(TLD_REGEX, EMAIL_ALPHABET)
render(nfa_to_dot(tld), "fig3_tld_nfa")
render(to_dot(tld.to_dfa().minimize()), "fig4_tld_min_dfa")
render("""digraph G { rankdir=LR; node [shape=box, style=rounded, fontsize=11];
 in [label="password string", shape=plaintext];
 c [label="classifier\\nchar -> {a, A, 0, !, ~}"];
 d1 [label="D1: length 8-16\\n(18 states)"]; d2 [label="D2: only allowed\\n(2)"]; d3 [label="D3: has lower\\n(2)"];
 d4 [label="D4: has upper\\n(2)"]; d5 [label="D5: has digit\\n(2)"]; d6 [label="D6: has special\\n(2)"];
 p [label="product (AND) + minimise\\n197 states", style="rounded,filled", fillcolor="#e8f0fe"];
 out [label="ACCEPT / REJECT", shape=plaintext];
 in -> c; c -> d1; c -> d2; c -> d3; c -> d4; c -> d5; c -> d6;
 d1 -> p; d2 -> p; d3 -> p; d4 -> p; d5 -> p; d6 -> p; p -> out; }""", "fig5_password_product")
v = json.load(open("results/verification.json"))["sizes"]
labels = ["PIN\nNFA", "PIN\nmin DFA", "PIN + deny-list\nmin DFA", "E-mail\nNFA", "E-mail\nsubset DFA", "E-mail\nmin DFA", "Password\nnaive product", "Password\nmin DFA"]
vals = [v["pin_nfa"], v["pin_min"], v["pin_with_denylist_min"], v["email_nfa"], v["email_subset_dfa"], v["email_min"], v["password_naive_product"], v["password_min"]]
fig, ax = plt.subplots(figsize=(9, 3.8))
bars = ax.bar(labels, vals, color=["#9bb7e8", "#4472c4", "#4472c4", "#9bb7e8", "#7a9fd9", "#4472c4", "#9bb7e8", "#4472c4"])
for b, x in zip(bars, vals): ax.text(b.get_x() + b.get_width() / 2, x + 5, str(x), ha="center", fontsize=9)
ax.set_ylabel("number of states"); ax.set_title("State counts read from the generated machines"); ax.tick_params(axis="x", labelsize=8)
plt.tight_layout(); plt.savefig(FIG + "fig6_state_counts.png", dpi=150)
print("figures ok")

# abstract (phase-level) e-mail diagram for the report; the full 16-state machine is in fig2
render("""digraph G { rankdir=LR; node [shape=circle, fontsize=11]; edge [fontsize=10];
 s [shape=point,width=0.1]; s -> L0;
 L0 [label="L0\\nstart"]; L1 [label="L1\\nlocal\\nalnum"]; L2 [label="L2\\nafter . _ -"];
 D0 [label="D0\\nafter @"]; D1 [label="D1\\nlabel"]; D2 [label="D2\\nafter -"]; D3 [label="D3\\nafter ."];
 T [label="TLD\\nmatch", shape=doublecircle];
 L0 -> L1 [label="alnum"]; L1 -> L1 [label="alnum"]; L1 -> L2 [label=". _ -"]; L2 -> L1 [label="alnum"];
 L1 -> D0 [label="@"]; D0 -> D1 [label="alnum"]; D1 -> D1 [label="alnum"]; D1 -> D2 [label="-"]; D2 -> D1 [label="alnum"];
 D1 -> D3 [label="."]; D3 -> D1 [label="alnum"]; D3 -> T [label="com | org | edu | net | in"]; T -> D3 [label="."];
 }""", "fig2b_email_abstract")
