from types import SimpleNamespace

import numpy as np
import pandas as pd
import psyplot_gui
from PIL import Image

from straditize.cross_mark import CrossMarks
from straditize.binary import DataReader
from straditize.straditizer import Straditizer, should_use_headless_figure


def test_should_use_headless_figure_during_unit_testing(monkeypatch):
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    monkeypatch.setattr(psyplot_gui, "UNIT_TESTING", True, raising=False)

    assert should_use_headless_figure() is True


def test_add_mark_event_supports_headless_figures(monkeypatch):
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    monkeypatch.setattr(psyplot_gui, "UNIT_TESTING", True, raising=False)

    stradi = Straditizer(np.zeros((8, 8, 4), dtype=np.uint8))
    stradi.marks = []

    event_handler = stradi._add_mark_event(
        lambda pos: [CrossMarks(pos, ax=stradi.ax)])
    event_handler(SimpleNamespace(
        key="shift", button=1, inaxes=stradi.ax, xdata=2, ydata=3))

    assert len(stradi.marks) == 1
    assert np.allclose(stradi.marks[0].pos, [2, 3])


def test_plot_results_avoids_pyplot_figure_in_headless_mode(monkeypatch):
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    monkeypatch.setattr(psyplot_gui, "UNIT_TESTING", True, raising=False)

    reader = DataReader(
        Image.fromarray(np.zeros((12, 12, 4), dtype=np.uint8), mode="RGBA"),
        plot=False,
    )
    reader._column_starts = np.array([0])
    reader.columns = [0]
    reader._column_ends = np.array([12])

    def fail_if_called(*args, **kwargs):
        raise AssertionError("plot_results should not call pyplot.figure()")

    import matplotlib.pyplot as plt

    monkeypatch.setattr(plt, "figure", fail_if_called)

    class FakePlotterArray(object):
        def __init__(self, name):
            self.psy = SimpleNamespace(arr_name=name)

    class FakeGrouper(object):
        def __init__(self, fig, name):
            self.axes = [fig.add_axes([0.1, 0.1, 0.8, 0.8])]
            self.plotter_arrays = [FakePlotterArray(name)]

    class FakeProjectItem(object):
        def __init__(self):
            self.psy = SimpleNamespace(update=lambda **kwargs: None)

    class FakeAxesProject(object):
        def update(self, **kwargs):
            return None

    class FakeProject(list):
        def __init__(self, items, axes):
            super(FakeProject, self).__init__(items)
            self.axes = axes
            self.main = self

    def fake_create_grouper(
        self, ds, cols, fig, x0, y0, total_width, height, ax0=None,
        transformed=True, colnames=None
    ):
        return FakeGrouper(fig, "col_%s" % cols[0])

    import psyplot.project as psy

    monkeypatch.setattr(DataReader, "create_grouper", fake_create_grouper)
    monkeypatch.setattr(
        psy,
        "gcp",
        lambda current: lambda **kwargs: FakeProject(
            [FakeProjectItem()], {}),
    )
    monkeypatch.setattr(psy, "scp", lambda project: None)

    df = pd.DataFrame({0: [1.0, 2.0]}, index=[0, 1])
    sp, groupers = reader.plot_results(df)

    assert len(sp) == 1
    assert len(groupers) == 1


def test_plot_results_skips_project_registration_in_headless_mode(monkeypatch):
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    monkeypatch.setattr(psyplot_gui, "UNIT_TESTING", True, raising=False)

    reader = DataReader(
        Image.fromarray(np.zeros((12, 12, 4), dtype=np.uint8), mode="RGBA"),
        plot=False,
    )
    reader._column_starts = np.array([0])
    reader.columns = [0]
    reader._column_ends = np.array([12])

    class FakePlotterArray(object):
        def __init__(self, name):
            self.psy = SimpleNamespace(arr_name=name)

    class FakeGrouper(object):
        def __init__(self, fig, name):
            self.axes = [fig.add_axes([0.1, 0.1, 0.8, 0.8])]
            self.plotter_arrays = [FakePlotterArray(name)]

    class FakeProjectItem(object):
        def __init__(self):
            self.psy = SimpleNamespace(update=lambda **kwargs: None)

    class FakeAxesProject(object):
        def update(self, **kwargs):
            return None

    class FakeProject(list):
        def __init__(self, items, axes):
            super(FakeProject, self).__init__(items)
            self.axes = axes
            self.main = self

    def fake_create_grouper(
        self, ds, cols, fig, x0, y0, total_width, height, ax0=None,
        transformed=True, colnames=None
    ):
        return FakeGrouper(fig, "col_%s" % cols[0])

    import psyplot.project as psy

    scp_calls = []

    monkeypatch.setattr(DataReader, "create_grouper", fake_create_grouper)
    monkeypatch.setattr(
        psy,
        "gcp",
        lambda current: lambda **kwargs: FakeProject(
            [FakeProjectItem()], {}),
    )
    monkeypatch.setattr(psy, "scp", lambda project: scp_calls.append(project))

    df = pd.DataFrame({0: [1.0, 2.0]}, index=[0, 1])
    sp, groupers = reader.plot_results(df)

    assert len(sp) == 1
    assert len(groupers) == 1
    assert scp_calls == []
    assert hasattr(groupers[0].axes[0].figure, "number")
