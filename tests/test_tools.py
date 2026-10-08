import pytest
from app.tools import _safe_path, ToolError

def test_workspace_path_is_confined():
    assert _safe_path('notes.txt').name == 'notes.txt'

def test_path_escape_is_rejected():
    with pytest.raises(ToolError):
        _safe_path('../../etc/passwd')
