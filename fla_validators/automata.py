"""Core finite-automata toolkit: DFA, epsilon-NFA, regex->NFA (Thompson),
subset construction, Moore minimisation, product construction, equivalence."""
from __future__ import annotations

from collections import defaultdict, deque

EPS = ""


# --------------------------------------------------------------------------- DFA
class DFA:
    """Complete DFA. States may be any hashable objects."""

    def __init__(self, states, alphabet, delta, start, accepting, name=""):
        self.states = set(states)
        self.alphabet = tuple(sorted(alphabet))
        self.delta = dict(delta)
        self.start = start
        self.accepting = set(accepting)
        self.name = name

    # -- running -----------------------------------------------------------
    def run(self, word):
        q = self.start
        for a in word:
            q = self.delta[(q, a)]
        return q

    def accepts(self, word) -> bool:
        return self.run(word) in self.accepting

    def trace(self, word):
        """Return [(state, symbol, next_state), ...] for the whole word."""
        q, steps = self.start, []
        for a in word:
            r = self.delta[(q, a)]
            steps.append((q, a, r))
            q = r
        return steps

    # -- structure ---------------------------------------------------------
    def reachable(self) -> "DFA":
        seen, todo = {self.start}, deque([self.start])
        while todo:
            q = todo.popleft()
            for a in self.alphabet:
                r = self.delta[(q, a)]
                if r not in seen:
                    seen.add(r)
                    todo.append(r)
        delta = {(q, a): self.delta[(q, a)] for q in seen for a in self.alphabet}
        return DFA(seen, self.alphabet, delta, self.start, self.accepting & seen, self.name)

    def dead_states(self):
        """States from which no accepting state is reachable (trap states)."""
        rev = defaultdict(set)
        for (q, a), r in self.delta.items():
            rev[r].add(q)
        live, todo = set(self.accepting), deque(self.accepting)
        while todo:
            r = todo.popleft()
            for q in rev[r]:
                if q not in live:
                    live.add(q)
                    todo.append(q)
        return self.states - live

    def minimize(self) -> "DFA":
        d = self.reachable()
        states = sorted(d.states, key=repr)
        part = {q: int(q in d.accepting) for q in states}
        count = len(set(part.values()))
        while True:
            sig = {q: (part[q], tuple(part[d.delta[(q, a)]] for a in d.alphabet)) for q in states}
            ids = {}
            new = {q: ids.setdefault(sig[q], len(ids)) for q in states}
            if len(ids) == count:
                break
            part, count = new, len(ids)
        # renumber classes in BFS order from the start state
        order, todo = {}, deque([part[d.start]])
        rep = {}
        for q in states:
            rep.setdefault(part[q], q)
        order[part[d.start]] = 0
        while todo:
            c = todo.popleft()
            for a in d.alphabet:
                c2 = part[d.delta[(rep[c], a)]]
                if c2 not in order:
                    order[c2] = len(order)
                    todo.append(c2)
        delta = {(order[c], a): order[part[d.delta[(rep[c], a)]]] for c in order for a in d.alphabet}
        acc = {order[c] for c in order if rep[c] in d.accepting}
        return DFA(set(order.values()), d.alphabet, delta, 0, acc, self.name)

    # -- language operations ------------------------------------------------
    def complement(self) -> "DFA":
        return DFA(self.states, self.alphabet, self.delta, self.start, self.states - self.accepting, self.name)

    def shortest_accepted(self):
        """Shortest accepted word (BFS) or None."""
        seen, todo = {self.start: ""}, deque([self.start])
        while todo:
            q = todo.popleft()
            if q in self.accepting:
                return seen[q]
            for a in self.alphabet:
                r = self.delta[(q, a)]
                if r not in seen:
                    seen[r] = seen[q] + a
                    todo.append(r)
        return None

    def __len__(self):
        return len(self.states)


def product(d1: DFA, d2: DFA, mode="and") -> DFA:
    assert d1.alphabet == d2.alphabet, "alphabets must match"
    ops = {
        "and": lambda x, y: x and y,
        "or": lambda x, y: x or y,
        "diff": lambda x, y: x and not y,
        "xor": lambda x, y: x != y,
    }
    f = ops[mode]
    start = (d1.start, d2.start)
    seen, todo, delta, acc = {start}, deque([start]), {}, set()
    while todo:
        p = todo.popleft()
        if f(p[0] in d1.accepting, p[1] in d2.accepting):
            acc.add(p)
        for a in d1.alphabet:
            r = (d1.delta[(p[0], a)], d2.delta[(p[1], a)])
            delta[(p, a)] = r
            if r not in seen:
                seen.add(r)
                todo.append(r)
    return DFA(seen, d1.alphabet, delta, start, acc)


def intersect_all(dfas):
    result = dfas[0].minimize()
    for d in dfas[1:]:
        result = product(result, d, "and").minimize()
    return result


def equivalent(d1: DFA, d2: DFA):
    """Language equivalence by reachability of an 'xor' state.
    Returns (True, None) or (False, shortest_distinguishing_word)."""
    x = product(d1, d2, "xor")
    w = x.shortest_accepted()
    return (w is None), w


def from_finite_language(words, alphabet) -> DFA:
    """Trie DFA (with an explicit trap state) for a finite set of words."""
    trie = {(): 0}
    delta, acc, n = {}, set(), 1
    for w in words:
        node = ()
        for ch in w:
            nxt = node + (ch,)
            if nxt not in trie:
                trie[nxt] = n
                n += 1
            node = nxt
        acc.add(trie[node])
    trap = n
    for node, q in trie.items():
        for a in sorted(alphabet):
            delta[(q, a)] = trie.get(node + (a,), trap)
    for a in alphabet:
        delta[(trap, a)] = trap
    return DFA(set(trie.values()) | {trap}, alphabet, delta, 0, acc)


# --------------------------------------------------------------------------- NFA
class NFA:
    """epsilon-NFA; delta maps (state, symbol-or-EPS) -> set of states."""

    def __init__(self, states, alphabet, delta, start, accepting, name=""):
        self.states = set(states)
        self.alphabet = tuple(sorted(alphabet))
        self.delta = {k: set(v) for k, v in delta.items()}
        self.start = start
        self.accepting = set(accepting)
        self.name = name

    def eclosure(self, qs):
        out, todo = set(qs), deque(qs)
        while todo:
            q = todo.popleft()
            for r in self.delta.get((q, EPS), ()):
                if r not in out:
                    out.add(r)
                    todo.append(r)
        return frozenset(out)

    def accepts(self, word) -> bool:
        cur = self.eclosure({self.start})
        for a in word:
            nxt = set()
            for q in cur:
                nxt |= self.delta.get((q, a), set())
            cur = self.eclosure(nxt)
        return bool(cur & self.accepting)

    def to_dfa(self) -> DFA:
        """Subset construction (reachable subsets only; the empty set is the trap)."""
        start = self.eclosure({self.start})
        seen, todo, delta = {start}, deque([start]), {}
        while todo:
            S = todo.popleft()
            for a in self.alphabet:
                nxt = set()
                for q in S:
                    nxt |= self.delta.get((q, a), set())
                T = self.eclosure(nxt)
                delta[(S, a)] = T
                if T not in seen:
                    seen.add(T)
                    todo.append(T)
        acc = {S for S in seen if S & self.accepting}
        return DFA(seen, self.alphabet, delta, start, acc, self.name)

    def transition_count(self):
        return sum(len(v) for v in self.delta.values())


# --------------------------------------------------------------------------- regex
class RegexError(ValueError):
    pass


class _Parser:
    def __init__(self, pat, alphabet):
        self.p, self.i, self.alpha = pat, 0, frozenset(alphabet)

    def peek(self):
        return self.p[self.i] if self.i < len(self.p) else None

    def nxt(self):
        c = self.peek()
        if c is None:
            raise RegexError("unexpected end of pattern")
        self.i += 1
        return c

    def parse(self):
        ast = self.alt()
        if self.i != len(self.p):
            raise RegexError(f"unexpected {self.peek()!r} at {self.i}")
        return ast

    def alt(self):
        parts = [self.cat()]
        while self.peek() == "|":
            self.nxt()
            parts.append(self.cat())
        return ("alt", parts) if len(parts) > 1 else parts[0]

    def cat(self):
        items = []
        while self.peek() not in (None, "|", ")"):
            items.append(self.rep())
        if not items:
            return ("eps",)
        return ("cat", items) if len(items) > 1 else items[0]

    def rep(self):
        a = self.atom()
        while self.peek() in ("*", "+", "?", "{"):
            c = self.nxt()
            if c == "*":
                a = ("star", a)
            elif c == "+":
                a = ("plus", a)
            elif c == "?":
                a = ("opt", a)
            else:
                m = self.number()
                n = m
                if self.peek() == ",":
                    self.nxt()
                    n = self.number() if self.peek() != "}" else None
                if self.nxt() != "}":
                    raise RegexError("expected }")
                a = ("rep", a, m, n)
        return a

    def number(self):
        s = ""
        while self.peek() is not None and self.peek().isdigit():
            s += self.nxt()
        if not s:
            raise RegexError("expected number")
        return int(s)

    def atom(self):
        c = self.nxt()
        if c == "(":
            a = self.alt()
            if self.nxt() != ")":
                raise RegexError("expected )")
            return a
        if c == "[":
            return self.cls()
        if c == ".":
            return ("set", self.alpha)
        if c == "\\":
            c = self.nxt()
        if c not in self.alpha:
            raise RegexError(f"symbol {c!r} not in alphabet")
        return ("set", frozenset({c}))

    def cls(self):
        neg = self.peek() == "^"
        if neg:
            self.nxt()
        chars = set()
        while self.peek() != "]":
            c = self.nxt()
            if c == "\\":
                c = self.nxt()
            if self.peek() == "-" and self.p[self.i + 1 : self.i + 2] not in ("]", ""):
                self.nxt()
                d = self.nxt()
                if d == "\\":
                    d = self.nxt()
                chars |= {chr(x) for x in range(ord(c), ord(d) + 1)}
            else:
                chars.add(c)
        self.nxt()
        chars &= self.alpha
        return ("set", frozenset(self.alpha - chars if neg else chars))


class _Builder:
    def __init__(self):
        self.n, self.delta = 0, defaultdict(set)

    def new(self):
        self.n += 1
        return self.n - 1

    def add(self, q, a, r):
        self.delta[(q, a)].add(r)

    def build(self, ast):
        kind = ast[0]
        if kind == "eps":
            s, e = self.new(), self.new()
            self.add(s, EPS, e)
            return s, e
        if kind == "set":
            s, e = self.new(), self.new()
            for a in sorted(ast[1]):
                self.add(s, a, e)
            return s, e
        if kind == "cat":
            parts = [self.build(x) for x in ast[1]]
            for (s1, e1), (s2, e2) in zip(parts, parts[1:]):
                self.add(e1, EPS, s2)
            return parts[0][0], parts[-1][1]
        if kind == "alt":
            s, e = self.new(), self.new()
            for x in ast[1]:
                s1, e1 = self.build(x)
                self.add(s, EPS, s1)
                self.add(e1, EPS, e)
            return s, e
        if kind == "star":
            s, e = self.new(), self.new()
            s1, e1 = self.build(ast[1])
            self.add(s, EPS, e)
            self.add(s, EPS, s1)
            self.add(e1, EPS, s1)
            self.add(e1, EPS, e)
            return s, e
        if kind == "plus":
            return self.build(("cat", [ast[1], ("star", ast[1])]))
        if kind == "opt":
            return self.build(("alt", [ast[1], ("eps",)]))
        if kind == "rep":
            _, x, m, n = ast
            items = [x] * m + ([("opt", x)] * (n - m) if n is not None else [("star", x)])
            return self.build(("cat", items) if len(items) > 1 else (items[0] if items else ("eps",)))
        raise RegexError(kind)


def regex_to_nfa(pattern: str, alphabet, name="") -> NFA:
    """Thompson construction. Syntax: | * + ? {m,n} ( ) [a-z] [^..] . \\x"""
    ast = _Parser(pattern, alphabet).parse()
    b = _Builder()
    s, e = b.build(ast)
    return NFA(range(b.n), alphabet, b.delta, s, {e}, name or pattern)


def regex_to_dfa(pattern: str, alphabet, name="") -> DFA:
    return regex_to_nfa(pattern, alphabet, name).to_dfa().minimize()


# --------------------------------------------------------------------------- export
def _compress(symbols):
    s = sorted(symbols)
    out, i = [], 0
    while i < len(s):
        j = i
        while j + 1 < len(s) and ord(s[j + 1]) == ord(s[j]) + 1:
            j += 1
        out.append(s[i] if j == i else (s[i] + s[j] if j == i + 1 else f"{s[i]}-{s[j]}"))
        i = j + 1
    return ",".join(out)


def to_dot(dfa: DFA, hide_dead=True, rankdir="LR", name_fn=None) -> str:
    dead = dfa.dead_states() if hide_dead else set()
    name_fn = name_fn or (lambda q: f"q{q}")
    lines = [f"digraph G {{ rankdir={rankdir}; node [shape=circle, fontsize=11]; edge [fontsize=10];",
             '__s [shape=point, width=0.1];']
    for q in sorted(dfa.states, key=repr):
        if q in dead:
            continue
        shape = "doublecircle" if q in dfa.accepting else "circle"
        lines.append(f'"{q}" [label="{name_fn(q)}", shape={shape}];')
    lines.append(f'__s -> "{dfa.start}";')
    grp = defaultdict(list)
    for (q, a), r in dfa.delta.items():
        if q in dead or r in dead:
            continue
        grp[(q, r)].append(a)
    for (q, r), syms in sorted(grp.items(), key=lambda kv: repr(kv[0])):
        lines.append(f'"{q}" -> "{r}" [label="{_compress(syms)}"];')
    lines.append("}")
    return "\n".join(lines)


def nfa_to_dot(nfa: NFA, rankdir="LR") -> str:
    lines = [f"digraph G {{ rankdir={rankdir}; node [shape=circle, fontsize=10]; edge [fontsize=9];",
             '__s [shape=point, width=0.1];']
    for q in sorted(nfa.states):
        lines.append(f'"{q}" [label="{q}", shape={"doublecircle" if q in nfa.accepting else "circle"}];')
    lines.append(f'__s -> "{nfa.start}";')
    grp = defaultdict(list)
    for (q, a), rs in nfa.delta.items():
        for r in rs:
            grp[(q, r)].append(a)
    for (q, r), syms in sorted(grp.items()):
        labels = [("ε" if x == EPS else x) for x in syms]
        non_eps = [x for x in syms if x != EPS]
        lab = _compress(non_eps) if non_eps else ""
        if EPS in syms:
            lab = (lab + "," if lab else "") + "ε"
        lines.append(f'"{q}" -> "{r}" [label="{lab}"];')
    lines.append("}")
    return "\n".join(lines)
