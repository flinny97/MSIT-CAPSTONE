"""
Gives every test a level marker based on where it lives, so one level can be run
on its own, for example:  pytest -m unit   or   pytest -m system
"""

import pytest

INTEGRATION_FILES = {"test_webapp_api.py", "test_integration_flow.py"}


def pytest_collection_modifyitems(items):
    for item in items:
        path = item.path
        if "system" in path.parts:
            item.add_marker(pytest.mark.system)
        elif "acceptance" in path.parts:
            item.add_marker(pytest.mark.acceptance)
        elif path.name in INTEGRATION_FILES:
            item.add_marker(pytest.mark.integration)
        else:
            item.add_marker(pytest.mark.unit)
