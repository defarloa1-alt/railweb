from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/llm/summarizeRun', methods=['POST'])
def summarize():
    return jsonify({'ok': True, 'text': 'SIMULATED SUMMARY'})

@app.route('/api/llm/explainChange', methods=['POST'])
def explain():
    return jsonify({'ok': True, 'text': '{"summary": "OK", "score": 0.5, "actions": ["Do B"]}'})

if __name__ == '__main__':
    app.run(port=3001)
