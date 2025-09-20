from tools.yaml_to_md import to_md


def test_yaml_to_md_basic():
    data = {'a': 1, 'b': {'c': 2}, 'd': [1,2,'x']}
    md = to_md(data)
    s = '\n'.join(md)
    assert '- **a**' in s
    assert '- **b**' in s
    assert '- `x`' in s
