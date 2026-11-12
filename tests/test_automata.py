import pytest
from fla_validators.automata import *

AB = "ab"

def test_regex_nfa_accepts_like_dfa():
    nfa = regex_to_nfa("(a|b)*abb", AB)
    dfa = nfa.to_dfa()
    for n in range(8):
        import itertools
        for t in itertools.product(AB, repeat=n):
            w = "".join(t)
            assert nfa.accepts(w) == dfa.accepts(w) == w.endswith("abb")

def test_minimize_known_size():
    # classic: strings over {a,b} ending in abb -> minimal DFA has 4 states
    assert len(regex_to_dfa("(a|b)*abb", AB)) == 4

def test_minimize_preserves_language():
    d = regex_to_nfa("(a|b)*a(a|b)(a|b)", AB).to_dfa()
    m = d.minimize()
    assert len(m) <= len(d) and equivalent(d, m)[0]

def test_equivalence_and_witness():
    ok, w = equivalent(regex_to_dfa("(a|b)*", AB), regex_to_dfa("a*b*", AB))
    assert not ok and w == "ba"
    assert equivalent(regex_to_dfa("a(ba)*", AB), regex_to_dfa("(ab)*a", AB))[0]

def test_closure_ops():
    d = regex_to_dfa("a*", AB)
    assert not d.complement().accepts("aaa") and d.complement().accepts("ab")
    assert product(d, regex_to_dfa("aa*", AB), "and").accepts("aa")

def test_repetition_syntax():
    d = regex_to_dfa("a{2,3}", AB)
    assert [d.accepts(w) for w in ["a", "aa", "aaa", "aaaa"]] == [False, True, True, False]

def test_bad_regex():
    with pytest.raises(RegexError): regex_to_nfa("(a", AB)
    with pytest.raises(RegexError): regex_to_nfa("c", AB)
