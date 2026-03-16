import builtins

import psyplot_gui

from straditize import widgets


def test_should_auto_show_docs_disabled_during_unit_testing(monkeypatch):
    monkeypatch.delenv("QT_QPA_PLATFORM", raising=False)
    monkeypatch.setattr(psyplot_gui, "UNIT_TESTING", True, raising=False)

    assert widgets.should_auto_show_docs() is False


def test_should_auto_show_docs_disabled_for_offscreen(monkeypatch):
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    monkeypatch.setattr(psyplot_gui, "UNIT_TESTING", False, raising=False)

    assert widgets.should_auto_show_docs() is False


def test_read_doc_file_uses_cache(monkeypatch):
    widgets.read_doc_file.cache_clear()

    target = widgets.get_doc_file("straditize.rst")
    calls = []
    real_open = builtins.open

    def counting_open(*args, **kwargs):
        if args and args[0] == target:
            calls.append(args[0])
        return real_open(*args, **kwargs)

    monkeypatch.setattr(builtins, "open", counting_open)

    first = widgets.read_doc_file("straditize.rst")
    second = widgets.read_doc_file("straditize.rst")

    assert first == second
    assert len(calls) == 1
