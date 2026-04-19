from pipeline.differ import compute_diff


def test_diff_hides_identical_content():
    d = compute_diff("Hello world.\nSecond line.", "Hello world.\nSecond line.")
    assert d.has_changes is False
    assert d.unified_diff == ""


def test_diff_shows_added_and_removed_lines():
    a = "Line one.\nLine two.\nLine three."
    b = "Line one.\nLine two CHANGED.\nLine three.\nLine four added."
    d = compute_diff(a, b)
    assert d.has_changes is True
    assert "-Line two." in d.unified_diff
    assert "+Line two CHANGED." in d.unified_diff
    assert "+Line four added." in d.unified_diff


def test_diff_normalizes_whitespace_but_preserves_semantics():
    a = "Hello   world.\n\n\nSame."
    b = "Hello world.\nSame."
    d = compute_diff(a, b)
    assert d.has_changes is False
