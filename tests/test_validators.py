import itertools, re, random
import pytest
from fla_validators.validators import build_pin, build_email, build_password, build_pin_nfa, build_email_nfa
from tests.examples import *

PIN, EMAIL, PW = build_pin(), build_email(), build_password()


@pytest.mark.parametrize("s", PIN_OK)
def test_pin_accepts(s): assert PIN.validate(s).ok

@pytest.mark.parametrize("s", PIN_BAD)
def test_pin_rejects(s): assert not PIN.validate(s).ok

@pytest.mark.parametrize("s", EMAIL_OK)
def test_email_accepts(s): assert EMAIL.validate(s).ok

@pytest.mark.parametrize("s", EMAIL_BAD)
def test_email_rejects(s): assert not EMAIL.validate(s).ok

@pytest.mark.parametrize("s", PW_OK)
def test_pw_accepts(s): assert PW.validate(s).ok, s

@pytest.mark.parametrize("s", PW_BAD)
def test_pw_rejects(s): assert not PW.validate(s).ok

def test_state_counts_are_stable():
    assert len(PIN.dfa) == 8          # q0..q6 + trap
    assert len(build_pin(True).dfa) > len(PIN.dfa)   # deny-list costs states

def test_pin_vs_oracle_exhaustive():
    for n in range(0, 8):
        for t in itertools.product("01x", repeat=n):
            s = "".join(t)
            assert PIN.validate(s).ok == (s.isdigit() and len(s) in (4, 6))

EMAIL_RE = re.compile(r"[a-z0-9]([._-]?[a-z0-9])*@([a-z0-9]+(-[a-z0-9]+)*\.)+(com|org|edu|net|in)", re.A)

def test_email_vs_re_oracle_bounded():
    for n in range(0, 6):
        for t in itertools.product("a1.@-inc", repeat=n):
            s = "".join(t)
            assert EMAIL.validate(s).ok == bool(EMAIL_RE.fullmatch(s)), s

PW_RE = re.compile(r"(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#$%^&*])[A-Za-z0-9!@#$%^&*]{8,16}", re.A)

def test_password_vs_re_oracle_random():
    rnd = random.Random(7)
    pool = "abcXYZ0159!@#$ é_"
    for _ in range(20000):
        s = "".join(rnd.choice(pool) for _ in range(rnd.randint(0, 20)))
        assert PW.validate(s).ok == bool(PW_RE.fullmatch(s)), s
