import json

from tools.responses_api_expert_debate import clean_json_content, parse_response


def test_clean_json_content_strips_code_fences():
    raw = "```json\n{\"a\": 1}\n```"
    assert clean_json_content(raw) == '{"a": 1}'


def test_parse_response_handles_invalid_json():
    analysis = parse_response("Test Expert", "not-json")
    assert analysis["parse_status"] == "fallback"
    assert analysis["expert"] == "Test Expert"
    assert analysis["analysis"] == "not-json"


def test_parse_response_normalises_required_fields():
    payload = {
        "analysis": "deep dive",
        "key_concerns": "security",
        "recommendations": "test more",
        "confidence": "0.8",
    }
    wrapped = f"```json\n{json.dumps(payload)}\n```"
    analysis = parse_response("Another Expert", wrapped)

    assert analysis["parse_status"] == "success"
    assert analysis["key_concerns"] == ["security"]
    assert analysis["recommendations"] == ["test more"]
    assert isinstance(analysis["confidence"], float)
