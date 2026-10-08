import pytest
from app.tools import _safe_path, _validate_url, ToolError


def test_workspace_path_is_confined():
    assert _safe_path("notes.txt").name == "notes.txt"


def test_path_escape_is_rejected():
    for value in (
        "../../etc/passwd",
        "/etc/passwd",
        "..\\secret",
        "a\x00b",
        "~/.ssh/id_rsa",
    ):
        with pytest.raises(ToolError):
            _safe_path(value)


def test_ssrf_destinations_are_rejected():
    for url in (
        "http://127.0.0.1/",
        "http://localhost/",
        "http://169.254.169.254/latest",
        "http://[::1]/",
    ):
        with pytest.raises(ToolError):
            _validate_url(url)


def test_unsafe_url_shapes_are_rejected():
    for url in (
        "file:///etc/passwd",
        "http://user:pass@example.com/",
        "http://example.com:8080/",
    ):
        with pytest.raises(ToolError):
            _validate_url(url)
