import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from main import hello_world


def test_hello_world():
    result = hello_world()
    assert "Hello World" in result
    assert "RAT Project" in result
