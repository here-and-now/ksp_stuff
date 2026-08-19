"""Live MET / altitude / Q plot for the launch tab."""

from __future__ import annotations

from typing import Any

from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

try:
    import pyqtgraph as pg
except ImportError:  # pragma: no cover
    pg = None  # type: ignore[misc, assignment]
else:
    pg.setConfigOptions(antialias=True)


class TelemetryPlot(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._met: list[float] = []
        self._alt: list[float] = []
        self._q: list[float] = []
        self._plot: Any = None
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        if pg is None:
            layout.addWidget(QLabel("pyqtgraph is not installed — no live plot."))
            return

        plot = pg.PlotWidget(background="#1e1e1e")
        plot.showGrid(x=True, y=True, alpha=0.2)
        plot.setLabel("bottom", "MET", units="s", color="#cccccc")
        plot.setLabel("left", "Altitude", units="m", color="#81b29a")
        for axis_name, pen in (
            ("bottom", "#cccccc"),
            ("left", "#81b29a"),
            ("right", "#e07a5f"),
        ):
            axis = plot.getAxis(axis_name) if axis_name != "right" else None
            if axis is not None:
                axis.setPen(pen)
                axis.setTextPen(pen)

        p1 = plot.plotItem
        p1.showAxis("right")
        right = p1.getAxis("right")
        right.setLabel("Dynamic pressure", units="Pa", color="#e07a5f")
        right.setPen("#e07a5f")
        right.setTextPen("#e07a5f")

        vb_q = pg.ViewBox()
        p1.scene().addItem(vb_q)
        right.linkToView(vb_q)
        vb_q.setXLink(p1)

        self._curve_alt = p1.plot(pen=pg.mkPen("#81b29a", width=2), name="altitude")
        self._curve_q = pg.PlotCurveItem(pen=pg.mkPen("#e07a5f", width=2), name="Q")
        vb_q.addItem(self._curve_q)

        self._plot = plot
        self._vb_q = vb_q
        p1.vb.sigResized.connect(self._sync_q_view)
        layout.addWidget(plot)
        self._sync_q_view()

    def _sync_q_view(self) -> None:
        if self._plot is None:
            return
        self._vb_q.setGeometry(self._plot.plotItem.vb.sceneBoundingRect())
        self._vb_q.linkedViewChanged(self._plot.plotItem.vb, self._vb_q.XAxis)

    def clear(self) -> None:
        self._met.clear()
        self._alt.clear()
        self._q.clear()
        self._redraw()

    def append(self, sample: Any) -> None:
        self._met.append(float(sample.met))
        self._alt.append(float(sample.altitude))
        self._q.append(float(sample.dynamic_pressure))
        if len(self._met) % 2 == 0 or sample.met < 2:
            self._redraw()

    def _redraw(self) -> None:
        if self._plot is None:
            return
        self._curve_alt.setData(self._met, self._alt)
        self._curve_q.setData(self._met, self._q)
