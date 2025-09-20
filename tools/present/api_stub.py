from flask import Flask, jsonify
from pathlib import Path
import yaml

app = Flask(__name__)
ROOT = Path(__file__).resolve().parents[2]

@app.route('/api/run/example')
def get_example():
    meta = (ROOT / 'runs' / 'example_run' / 'meta.example.yaml')
    if not meta.exists():
        return jsonify({'error': 'example meta not found'}), 404
    with open(meta, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    return jsonify(data)

if __name__ == '__main__':
    app.run(port=4001)
