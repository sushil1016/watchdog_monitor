import pytest


from interface.rule_engine.rule_engine import RulesEngine


def test_rule_engine():
    re=RulesEngine('test_attribute_error',1010,sadad)
    analyser_uri = re.get_analyser_uri()
    assert analyser_uri == 'error'

