import pytest

from tools.debate.manager import DebateManager
from tools.debate.agents import EchoAgent


def test_register_and_run():
    dm = DebateManager()
    a = EchoAgent("A", prefix="A->")
    b = EchoAgent("B", prefix="B->")
    dm.register(a)
    dm.register(b)
    hist = dm.run_rounds("ctx", rounds=2)
    assert len(hist) == 2
    assert hist[0][0].startswith("A: A->ctx")
    assert hist[0][1].startswith("B: B->ctx")


def test_duplicate_agent():
    dm = DebateManager()
    a1 = EchoAgent("A")
    a2 = EchoAgent("A")
    dm.register(a1)
    with pytest.raises(ValueError):
        dm.register(a2)


def test_invalid_rounds():
    dm = DebateManager()
    a = EchoAgent("A")
    dm.register(a)
    with pytest.raises(ValueError):
        dm.run_rounds("ctx", rounds=0)
