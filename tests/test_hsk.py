"""Tests for HSK application"""

from hsk import __version__


def test_version():
    """Test that version is defined"""
    assert __version__ == "0.1.0"
