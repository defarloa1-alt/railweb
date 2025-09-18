from tools.parse_kerml import parse_requirements


def test_parse_requirements_basic():
    sample = '''requirement REQ TYPE id="REQ-1" {\ntext = "Short requirement text";\nsource = "spec.doc";\n}'''
    out = parse_requirements(sample)
    assert isinstance(out, list)
    assert len(out) == 1
    assert out[0]['id'] == 'REQ-1'
    assert out[0]['text'].startswith('Short requirement')
