import sys
from pathlib import Path
repo = Path(__file__).resolve().parents[2]
if str(repo) not in sys.path:
    sys.path.insert(0, str(repo))

from tools.debate.run_real_debate import run_real_debate

if __name__ == '__main__':
    run_real_debate()
