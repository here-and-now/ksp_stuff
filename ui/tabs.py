"""Tab widgets. They talk to a Session owned by MainWindow."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Callable

_ROOT = Path(__file__).resolve().parent.parent
_UIDIR = Path(__file__).resolve().parent
for _p in (_ROOT, _UIDIR):
    _s = str(_p)
    if _s not in sys.path:
        sys.path.insert(0, _s)

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from career import snapshot_career
from launch import AscentConfig
from profile import GameProfile
from vessels import COLUMNS, list_vessels
from plot import TelemetryPlot


def _item(value: object) -> QTableWidgetItem:
    item = QTableWidgetItem(str(value))
    item.setFlags(item.flags() ^ Qt.ItemFlag.ItemIsEditable)
    return item


def _fill(table: QTableWidget, headers: tuple[str, ...], rows: list[tuple[object, ...]]) -> None:
    table.setColumnCount(len(headers))
    table.setHorizontalHeaderLabels(list(headers))
    table.setRowCount(len(rows))
    for r, row in enumerate(rows):
        for c, value in enumerate(row):
            table.setItem(r, c, _item(value))
    table.resizeColumnsToContents()


def _spin(minimum: float, maximum: float, value: float, step: float, decimals: int = 0) -> QDoubleSpinBox:
    box = QDoubleSpinBox()
    box.setRange(minimum, maximum)
    box.setDecimals(decimals)
    box.setSingleStep(step)
    box.setValue(value)
    box.setMaximumWidth(160)
    return box


class VesselsTab(QWidget):
    def __init__(self, host: Any) -> None:
        super().__init__()
        self.host = host
        self._vessels: list[Any] = []
        self.search = QLineEdit()
        self.search.setPlaceholderText("Name contains…")
        self.exact = QCheckBox("Exact")
        refresh = QPushButton("Refresh")
        switch = QPushButton("Switch to selected")
        refresh.clicked.connect(self.refresh)
        switch.clicked.connect(self.switch_selected)
        self.search.returnPressed.connect(self.refresh)

        self.table = QTableWidget(0, len(COLUMNS))
        self.table.setHorizontalHeaderLabels(list(COLUMNS))
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table.verticalHeader().setVisible(False)

        bar = QHBoxLayout()
        bar.addWidget(QLabel("Search"))
        bar.addWidget(self.search, 1)
        bar.addWidget(self.exact)
        bar.addWidget(refresh)
        bar.addWidget(switch)

        layout = QVBoxLayout(self)
        layout.addLayout(bar)
        layout.addWidget(self.table)

    def refresh(self) -> None:
        session = self.host.require_session()
        if session is None:
            return
        name = self.search.text().strip() or None
        rows = list_vessels(session, name=name, exact=self.exact.isChecked())
        self._vessels = [v for v, _s in rows]
        _fill(self.table, COLUMNS, [snap.as_row() for _v, snap in rows])
        self.host.log(f"{len(rows)} vessels")

    def switch_selected(self) -> None:
        session = self.host.require_session()
        if session is None:
            return
        row = self.table.currentRow()
        if row < 0 or row >= len(self._vessels):
            self.host.log("Select a vessel first")
            return
        vessel = self._vessels[row]
        session.switch_to(vessel)
        self.host.log(f"Active vessel → {vessel.name}")


class LaunchTab(QWidget):
    def __init__(self, host: Any) -> None:
        super().__init__()
        self.host = host
        self.target_alt = _spin(10_000, 5_000_000, 150_000, 1_000)
        self.turn_start = _spin(0, 200_000, 2_500, 100)
        self.turn_end = _spin(1_000, 400_000, 70_000, 1_000)
        self.inclination = _spin(-180, 180, 0, 1, 2)
        self.roll = _spin(0, 360, 90, 1)
        self.max_q = _spin(1_000, 80_000, 20_000, 500)
        self.max_twr = _spin(0, 10, 0, 0.1, 2)
        self.end_stage = QSpinBox()
        self.end_stage.setRange(0, 30)
        self.end_stage.setValue(0)
        self.northerly = QCheckBox("Northerly azimuth")
        self.northerly.setChecked(True)
        self.circularize = QCheckBox("Circularize when apoapsis is reached")
        self.circularize.setChecked(True)
        self.heading_label = QLabel("Heading: —")

        for box in (
            self.target_alt,
            self.turn_start,
            self.turn_end,
            self.inclination,
            self.roll,
            self.max_q,
            self.max_twr,
        ):
            box.valueChanged.connect(self._update_heading)

        form = QFormLayout()
        form.addRow("Target apoapsis m", self.target_alt)
        form.addRow("Turn start m", self.turn_start)
        form.addRow("Turn end m", self.turn_end)
        form.addRow("Inclination °", self.inclination)
        form.addRow("Roll °", self.roll)
        form.addRow("Max Q Pa", self.max_q)
        form.addRow("Max TWR (0 = off)", self.max_twr)
        form.addRow("Stop staging at", self.end_stage)
        form.addRow(self.northerly)
        form.addRow(self.circularize)
        form.addRow(self.heading_label)

        self.launch_btn = QPushButton("Launch")
        self.abort_btn = QPushButton("Abort")
        self.abort_btn.setEnabled(False)
        self.launch_btn.clicked.connect(self.launch)
        self.abort_btn.clicked.connect(self.host.abort_task)

        buttons = QHBoxLayout()
        buttons.addWidget(self.launch_btn)
        buttons.addWidget(self.abort_btn)
        buttons.addStretch()

        self.plot = TelemetryPlot()
        left = QVBoxLayout()
        left.addLayout(form)
        left.addLayout(buttons)
        left.addStretch()

        layout = QHBoxLayout(self)
        layout.addLayout(left, 0)
        layout.addWidget(self.plot, 1)

    def apply_profile(self, profile: GameProfile) -> None:
        lo, hi = profile.altitude_range
        self.target_alt.setRange(lo / 4, hi * 2)
        self.target_alt.setValue(profile.default_target_altitude)
        self.turn_start.setValue(profile.default_turn_start)
        self.turn_end.setValue(profile.default_turn_end)
        self.max_q.setValue(profile.default_max_q)
        self.max_twr.setValue(profile.default_max_twr or 0)
        self._update_heading()

    def config(self) -> AscentConfig:
        twr = self.max_twr.value()
        return AscentConfig(
            target_altitude=self.target_alt.value(),
            turn_start_altitude=self.turn_start.value(),
            turn_end_altitude=self.turn_end.value(),
            end_stage=self.end_stage.value(),
            inclination=self.inclination.value(),
            roll=self.roll.value(),
            max_q=self.max_q.value(),
            max_twr=twr if twr > 0 else None,
            northerly=self.northerly.isChecked(),
            circularize=self.circularize.isChecked(),
        )

    def _update_heading(self) -> None:
        from geometry import heading_from_inclination, inertial_launch_azimuth

        session = self.host.session
        inc = self.inclination.value()
        lat = 0.0
        if session is not None and session.connected:
            try:
                lat = float(session.active_vessel.flight().latitude)
            except Exception:
                lat = 0.0
        if abs(lat) < 0.5:
            heading = heading_from_inclination(inc)
        else:
            heading = inertial_launch_azimuth(
                lat, inc, northerly=self.northerly.isChecked()
            )
        self.heading_label.setText(f"Heading: {heading:.1f}°  (lat {lat:.2f}°)")

    def launch(self) -> None:
        session = self.host.require_session()
        if session is None:
            return
        self.plot.clear()
        cfg = self.config()

        def work(task: Any) -> None:
            from launch import Ascent

            ascent = Ascent(
                session,
                cfg,
                on_log=task.log_line.emit,
                on_telemetry=task.telemetry.emit,
                abort=task.aborted,
            )
            ascent.run()

        self.host.run_task(work, telemetry=self.plot.append)


class ConstellationTab(QWidget):
    def __init__(self, host: Any) -> None:
        super().__init__()
        self.host = host
        self.name = QLineEdit()
        self.name.setPlaceholderText("Constellation name substring")
        self.layer = QComboBox()
        from constellation import LAYERS

        for key, layer in LAYERS.items():
            self.layer.addItem(layer.title, key)
        self.layer.currentIndexChanged.connect(self._apply_layer)
        self.count = QSpinBox()
        self.count.setRange(1, 12)
        self.count.setValue(3)
        self.num = QSpinBox()
        self.num.setRange(1, 20)
        self.num.setValue(2)
        self.den = QSpinBox()
        self.den.setRange(1, 20)
        self.den.setValue(3)
        self.plan = QPlainTextEdit()
        self.plan.setPlaceholderText(
            "RemoteTech only (optional JSON). RP-1/RA ignores this — "
            "CommNet routes itself. Example:\n"
            '{"HighGainAntenna": "setup_network"}'
        )
        self.plan.setFixedHeight(90)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(
            ["Name", "Body", "Apo", "Peri", "Period s", "Δperiod"]
        )
        self.table.verticalHeader().setVisible(False)

        def btn(label: str, slot: Callable[[], None]) -> QPushButton:
            b = QPushButton(label)
            b.clicked.connect(slot)
            return b

        buttons = QHBoxLayout()
        for label, slot in (
            ("Load existing", self.load_existing),
            ("Resonant orbit", self.resonant),
            ("Release sats", self.release),
            ("Staggered recirc", self.recirc),
            ("Fine-tune period", self.fine_tune),
            ("Commission comms", self.setup_comms),
            ("Slot report", self.slot_report),
        ):
            buttons.addWidget(btn(label, slot))

        form = QFormLayout()
        form.addRow("Name", self.name)
        form.addRow("Layer", self.layer)
        form.addRow("Satellites to release", self.count)
        form.addRow("Resonance numerator", self.num)
        form.addRow("Resonance denominator", self.den)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(QLabel("Antenna plan"))
        layout.addWidget(self.plan)
        layout.addLayout(buttons)
        layout.addWidget(self.table)

    def _apply_layer(self) -> None:
        from constellation import LAYERS, resonance_for_count

        key = self.layer.currentData()
        layer = LAYERS.get(key)
        if layer is None:
            return
        self.count.setValue(layer.count)
        num, den = resonance_for_count(layer.count)
        self.num.setValue(num)
        self.den.setValue(den)
        self.host.log(layer.notes)

    def _plan(self) -> dict:
        text = self.plan.toPlainText().strip()
        if not text:
            return {}
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Antenna plan JSON: {exc}") from exc
        if not isinstance(data, dict):
            raise ValueError("Antenna plan must be a JSON object")
        return data

    def _constellation(self):
        from constellation import Constellation, ConstellationConfig

        session = self.host.require_session()
        if session is None:
            return None
        try:
            plan = self._plan()
        except ValueError as exc:
            self.host.log(str(exc))
            return None
        cfg = ConstellationConfig(
            name=self.name.text().strip(),
            satellite_count=self.count.value(),
            resonance_numerator=self.num.value(),
            resonance_denominator=self.den.value(),
            antenna_plan=plan,
            layer=self.layer.currentData() or "meo4",
        )
        return Constellation(session, cfg, on_log=self.host.log)

    def _refresh_table(self, constel) -> None:
        snaps = constel.snapshots()
        if not snaps:
            _fill(self.table, ("Name", "Body", "Apo", "Peri", "Period s", "Δperiod"), [])
            return
        mean = sum(s.period for _v, s in snaps) / len(snaps)
        rows = [
            (
                s.name,
                s.body,
                round(s.apoapsis),
                round(s.periapsis),
                round(s.period, 3),
                round(s.period - mean, 4),
            )
            for _v, s in snaps
        ]
        _fill(self.table, ("Name", "Body", "Apo", "Peri", "Period s", "Δperiod"), rows)

    def load_existing(self) -> None:
        constel = self._constellation()
        if constel is None:
            return
        constel.load_existing()
        self._refresh_table(constel)
        self.host._constellation = constel

    def _run(self, fn: Callable[[Any], None]) -> None:
        constel = getattr(self.host, "_constellation", None) or self._constellation()
        if constel is None:
            return
        self.host._constellation = constel

        def work(task: Any) -> None:
            constel.on_log = task.log_line.emit
            constel.abort = task.aborted
            fn(constel)

        self.host.run_task(work, done=lambda _r: self._refresh_table(constel))

    def resonant(self) -> None:
        self._run(lambda c: c.resonant_orbit())

    def release(self) -> None:
        self._run(lambda c: c.release_all())

    def recirc(self) -> None:
        self._run(lambda c: c.recircularize_staggered())

    def fine_tune(self) -> None:
        self._run(lambda c: c.fine_tune_period())

    def setup_comms(self) -> None:
        self._run(lambda c: c.setup_comms())

    def slot_report(self) -> None:
        constel = getattr(self.host, "_constellation", None) or self._constellation()
        if constel is None:
            return
        self.host._constellation = constel
        from constellation import LAYERS

        layer = LAYERS.get(self.layer.currentData() or constel.config.layer)
        for line in constel.spacing_report(layer):
            self.host.log(line)
        self._refresh_table(constel)


class CommsTab(QWidget):
    HEADERS = (
        "Vessel",
        "Link",
        "Path",
        "Part",
        "Band",
        "Gain",
        "Tx dBm",
        "TL",
        "Aim",
        "Condition",
    )

    def __init__(self, host: Any) -> None:
        super().__init__()
        self.host = host
        self.name = QLineEdit()
        self.name.setPlaceholderText("Vessel name substring (empty = constellation or all)")
        inspect = QPushButton("Inspect")
        inspect.clicked.connect(self.inspect)
        commission = QPushButton("Deploy & inventory")
        commission.clicked.connect(self.commission)
        self.table = QTableWidget(0, len(self.HEADERS))
        self.table.setHorizontalHeaderLabels(list(self.HEADERS))
        self.table.verticalHeader().setVisible(False)
        self.notes = QTextEdit()
        self.notes.setReadOnly(True)
        self.notes.setMaximumHeight(110)
        bar = QHBoxLayout()
        bar.addWidget(self.name, 1)
        bar.addWidget(inspect)
        bar.addWidget(commission)
        layout = QVBoxLayout(self)
        layout.addLayout(bar)
        layout.addWidget(self.table, 1)
        layout.addWidget(self.notes)

    def _vessels(self, session: Any) -> list[Any]:
        name = self.name.text().strip()
        if not name:
            constel = getattr(self.host, "_constellation", None)
            if constel and constel.vessels:
                return list(constel.vessels)
            return [v for v, _s in list_vessels(session)]
        return [v for v, _s in list_vessels(session, name=name, exact=False)]

    def inspect(self) -> None:
        session = self.host.require_session()
        if session is None:
            return
        from comms import coverage_report

        report = coverage_report(session, self._vessels(session), switch=False)
        self._show(report)

    def commission(self) -> None:
        session = self.host.require_session()
        if session is None:
            return
        vessels = self._vessels(session)

        def work(task: Any) -> Any:
            from comms import commission_network

            return commission_network(session, vessels, on_log=task.log_line.emit)

        self.host.run_task(work, done=self._show)

    def _show(self, report: Any) -> None:
        rows: list[tuple[object, ...]] = []
        for row in report.rows:
            link = "up" if row.can_communicate else ("down" if row.can_communicate is False else "—")
            if row.antennas:
                for ant in row.antennas:
                    rows.append(
                        (
                            row.vessel_name,
                            link,
                            row.path,
                            ant.part_name,
                            ant.band or "—",
                            ant.gain or "—",
                            ant.tx_dbm or "—",
                            ant.tech_level or "—",
                            ant.target,
                            ant.state,
                        )
                    )
            else:
                rows.append(
                    (
                        row.vessel_name,
                        link,
                        row.path,
                        "—",
                        "—",
                        "—",
                        "—",
                        "—",
                        "—",
                        "—",
                    )
                )
        _fill(self.table, self.HEADERS, rows)
        notes = [f"{report.linked} linked, {report.dark} dark"] + list(report.notes)
        self.notes.setPlainText("\n".join(f"• {n}" for n in notes))
        for n in notes:
            self.host.log(n)


class CareerTab(QWidget):
    def __init__(self, host: Any) -> None:
        super().__init__()
        self.host = host
        self.summary = QLabel("Connect to read career fields.")
        self.summary.setWordWrap(True)
        self.notes = QTextEdit()
        self.notes.setReadOnly(True)
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Contract", "State", "Active"])
        self.table.verticalHeader().setVisible(False)
        refresh = QPushButton("Refresh")
        refresh.clicked.connect(self.refresh)
        layout = QVBoxLayout(self)
        layout.addWidget(self.summary)
        layout.addWidget(refresh, alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.table, 1)
        layout.addWidget(QLabel("RP-1 notes"))
        layout.addWidget(self.notes)

    def refresh(self) -> None:
        session = self.host.require_session()
        if session is None:
            return
        snap = snapshot_career(session)
        funds = "—" if snap.funds is None else f"{snap.funds:,.0f}"
        science = "—" if snap.science is None else f"{snap.science:.1f}"
        rep = "—" if snap.reputation is None else f"{snap.reputation:.1f}"
        self.summary.setText(
            f"Mode {snap.game_mode}    Funds {funds}    Science {science}    Rep {rep}"
        )
        rows = [
            (c.title, c.state, "yes" if c.active else "no") for c in snap.contracts
        ]
        _fill(self.table, ("Contract", "State", "Active"), rows)
        self.notes.setPlainText("\n".join(f"• {n}" for n in snap.notes))


class HangarTab(QWidget):
    """Craft files on disk. kRPC can launch these; it cannot build them in the VAB."""

    def __init__(self, host: Any) -> None:
        super().__init__()
        self.host = host
        self.ksp = QLineEdit()
        self.save = QComboBox()
        self.save.setEditable(True)
        self.facility = QComboBox()
        self.facility.addItems(["VAB", "SPH"])
        self.template = QComboBox()
        from craft import TEMPLATES

        for key in TEMPLATES:
            self.template.addItem(key)
        browse = QPushButton("Browse…")
        browse.clicked.connect(self._browse)
        discover = QPushButton("Find KSP")
        discover.clicked.connect(self._discover)
        refresh = QPushButton("List crafts")
        refresh.clicked.connect(self.refresh)
        write_btn = QPushButton("Write template into save")
        write_btn.clicked.connect(self.write_template)
        launch_btn = QPushButton("Launch selected")
        launch_btn.clicked.connect(self.launch_selected)
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Name", "Facility", "Parts", "Path"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.detail = QPlainTextEdit()
        self.detail.setReadOnly(True)
        self.detail.setMaximumHeight(120)
        self.table.itemSelectionChanged.connect(self._show_selected)

        form = QFormLayout()
        ksp_row = QHBoxLayout()
        ksp_row.addWidget(self.ksp, 1)
        ksp_row.addWidget(browse)
        ksp_row.addWidget(discover)
        form.addRow("KSP root", ksp_row)
        form.addRow("Save", self.save)
        form.addRow("Facility", self.facility)
        form.addRow("Template", self.template)

        buttons = QHBoxLayout()
        buttons.addWidget(refresh)
        buttons.addWidget(write_btn)
        buttons.addWidget(launch_btn)
        buttons.addStretch()

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addLayout(buttons)
        layout.addWidget(self.table, 1)
        layout.addWidget(self.detail)
        self._discover()

    def _hangar(self):
        from pathlib import Path

        from hangar import Hangar

        root = Path(self.ksp.text().strip())
        save = self.save.currentText().strip()
        if not root.is_dir() or not save:
            self.host.log("Set KSP root and a save name first")
            return None
        return Hangar(ksp_root=root, save=save)

    def _browse(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "KSP root")
        if path:
            self.ksp.setText(path)
            self._fill_saves()

    def _discover(self) -> None:
        from hangar import discover_hangar

        hangar = discover_hangar()
        if hangar is None:
            self.host.log("No KSP install found. Set KSPSTUFF_KSP or browse.")
            return
        self.ksp.setText(str(hangar.ksp_root))
        self._fill_saves()
        if hangar.save:
            idx = self.save.findText(hangar.save)
            if idx >= 0:
                self.save.setCurrentIndex(idx)
            else:
                self.save.setEditText(hangar.save)
        self.host.log(f"KSP {hangar.ksp_root}")

    def _fill_saves(self) -> None:
        from pathlib import Path

        from hangar import Hangar

        root = Path(self.ksp.text().strip())
        if not root.is_dir():
            return
        current = self.save.currentText()
        self.save.clear()
        dummy = Hangar(ksp_root=root, save="")
        for name in dummy.list_saves():
            self.save.addItem(name)
        if current:
            idx = self.save.findText(current)
            if idx >= 0:
                self.save.setCurrentIndex(idx)

    def refresh(self) -> None:
        hangar = self._hangar()
        if hangar is None:
            return
        facility = self.facility.currentText()
        crafts = hangar.list_crafts(facility)
        rows = [
            (c.name, c.facility, c.parts if c.parts is not None else "?", str(c.path))
            for c in crafts
        ]
        _fill(self.table, ("Name", "Facility", "Parts", "Path"), rows)
        self.host.log(f"{len(crafts)} craft(s) in {facility}")

    def write_template(self) -> None:
        hangar = self._hangar()
        if hangar is None:
            return
        from craft import TEMPLATES

        key = self.template.currentText()
        craft = TEMPLATES[key]()
        path = hangar.install(craft, facility=self.facility.currentText(), overwrite=True)
        self.host.log(f"Wrote {craft.summary()} → {path}")
        self.refresh()

    def launch_selected(self) -> None:
        session = self.host.require_session()
        hangar = self._hangar()
        if session is None or hangar is None:
            return
        row = self.table.currentRow()
        if row < 0:
            self.host.log("Select a craft")
            return
        name = self.table.item(row, 0).text()
        facility = self.table.item(row, 1).text()

        def work(task: Any) -> None:
            hangar.launch(session, name, facility=facility)
            task.log_line.emit(f"Launched {name}")

        self.host.run_task(work)

    def _show_selected(self) -> None:
        hangar = self._hangar()
        row = self.table.currentRow()
        if hangar is None or row < 0:
            return
        name = self.table.item(row, 0).text()
        facility = self.table.item(row, 1).text()
        try:
            craft = hangar.load_craft(name, facility)
        except Exception as exc:
            self.detail.setPlainText(str(exc))
            return
        lines = [craft.summary(), craft.description, ""]
        for part in craft.parts:
            lines.append(f"{part.name}  istg={part.istg} dstg={part.dstg}  {part.token}")
        self.detail.setPlainText("\n".join(lines))
