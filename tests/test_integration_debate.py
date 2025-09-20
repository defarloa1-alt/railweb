import threading
import time
import io
import sys
from tools.debate import mock_adapter
from tools.debate.run_real_debate import run_real_debate


def start_mock_in_thread():
    # Start Flask mock adapter in a background daemon thread
    t = threading.Thread(
        target=lambda: mock_adapter.app.run(port=3001, use_reloader=False),
        daemon=True,
    )
    t.start()
    # give Flask a moment to bind
    time.sleep(0.6)
    return t


def test_integration_debate_runs_and_returns_expected():
    t = start_mock_in_thread()
    # capture stdout from the runner
    old = sys.stdout
    buf = io.StringIO()
    sys.stdout = buf
    try:
        run_real_debate()
    finally:
        sys.stdout = old
    out = buf.getvalue()
    assert 'Round 1' in out
    assert 'SIMULATED SUMMARY' in out
