"""PyQt control window. Replaces the old Bokeh ``KSPBokehApp``."""

from __future__ import annotations

import logging
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
from PyQt6.QtGui import QColor, QPalette, QTextCursor
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPlainTextEdit,
    QPushButton,
    QSpinBox,
    QStatusBar,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from profile import RSS_RP1, STOCK
from session import Session, SessionError
from tabs import CareerTab, CommsTab, ConstellationTab, HangarTab, LaunchTab, VesselsTab
from workers import Task

log = logging.getLogger("kspstuff")


def apply_dark_palette(app: QApplication) -> None:
    app.setStyle("Fusion")
    palette = QPalette()
    bg = QColor("#1e1e1e")
    panel = QColor("#252526")
    text = QColor("#e0e0e0")
    accent = QColor("#3d6f8c")
    palette.setColor(QPalette.ColorRole.Window, bg)
    palette.setColor(QPalette.ColorRole.WindowText, text)
    palette.setColor(QPalette.ColorRole.Base, QColor("#141414"))
    palette.setColor(QPalette.ColorRole.AlternateBase, panel)
    palette.setColor(QPalette.ColorRole.ToolTipBase, panel)
    palette.setColor(QPalette.ColorRole.ToolTipText, text)
    palette.setColor(QPalette.ColorRole.Text, text)
    palette.setColor(QPalette.ColorRole.Button, panel)
    palette.setColor(QPalette.ColorRole.ButtonText, text)
    palette.setColor(QPalette.ColorRole.BrightText, QColor("#ff6b6b"))
    palette.setColor(QPalette.ColorRole.Highlight, accent)
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.PlaceholderText, QColor("#888888"))
    app.setPalette(palette)


class MainWindow(QMainWindow):
    def __init__(
        self,
        *,
        host: str = "127.0.0.1",
        rpc_port: int = 50000,
        stream_port: int = 50001,
        profile_name: str = "auto",
    ) -> None:
        super().__init__()
        self.setWindowTitle("kspstuff")
        self.resize(1180, 780)
        self.session: Session | None = None
        self._task: Task | None = None
        self._constellation = None
        self._initial_profile = profile_name

        self.host_edit = QLineEdit(host)
        self.host_edit.setMaximumWidth(160)
        self.rpc_port = QSpinBox()
        self.rpc_port.setRange(1, 65535)
        self.rpc_port.setValue(rpc_port)
        self.stream_port = QSpinBox()
        self.stream_port.setRange(1, 65535)
        self.stream_port.setValue(stream_port)
        self.profile_box = QComboBox()
        self.profile_box.addItem("Auto-detect", "auto")
        self.profile_box.addItem(STOCK.display_name, "stock")
        self.profile_box.addItem(RSS_RP1.display_name, "rss")
        if profile_name == "stock":
            self.profile_box.setCurrentIndex(1)
        elif profile_name in ("rss", "rss_rp1"):
            self.profile_box.setCurrentIndex(2)

        self.connect_btn = QPushButton("Connect")
        self.disconnect_btn = QPushButton("Disconnect")
        self.disconnect_btn.setEnabled(False)
        self.connect_btn.clicked.connect(self.connect_session)
        self.disconnect_btn.clicked.connect(self.disconnect_session)

        self.badges = QLabel("offline")
        self.badges.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        conn_row = QHBoxLayout()
        for label, widget in (
            ("Host", self.host_edit),
            ("RPC", self.rpc_port),
            ("Stream", self.stream_port),
            ("Profile", self.profile_box),
        ):
            conn_row.addWidget(QLabel(label))
            conn_row.addWidget(widget)
        conn_row.addWidget(self.connect_btn)
        conn_row.addWidget(self.disconnect_btn)
        conn_row.addWidget(self.badges, 1)

        self.tabs = QTabWidget()
        self.vessels_tab = VesselsTab(self)
        self.launch_tab = LaunchTab(self)
        self.constellation_tab = ConstellationTab(self)
        self.comms_tab = CommsTab(self)
        self.career_tab = CareerTab(self)
        self.hangar_tab = HangarTab(self)
        self.tabs.addTab(self.vessels_tab, "Vessels")
        self.tabs.addTab(self.launch_tab, "Launch")
        self.tabs.addTab(self.hangar_tab, "Hangar")
        self.tabs.addTab(self.constellation_tab, "Constellation")
        self.tabs.addTab(self.comms_tab, "Comms")
        self.tabs.addTab(self.career_tab, "Career / RP-1")

        self.log_view = QPlainTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setMaximumHeight(160)
        self.log_view.setPlaceholderText("Log")

        root = QWidget()
        layout = QVBoxLayout(root)
        layout.addLayout(conn_row)
        layout.addWidget(self.tabs, 1)
        layout.addWidget(self.log_view)
        self.setCentralWidget(root)
        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("Not connected — KSP + kRPC are not required to browse the UI.")

    def log(self, message: str) -> None:
        log.info(message)
        self.log_view.appendPlainText(message)
        self.log_view.moveCursor(QTextCursor.MoveOperation.End)

    def require_session(self) -> Session | None:
        if self.session is None or not self.session.connected:
            self.log("Connect to kRPC first. The game is not required until then.")
            return None
        return self.session

    def connect_session(self) -> None:
        from session import ConnectionSettings

        settings = ConnectionSettings(
            address=self.host_edit.text().strip() or "127.0.0.1",
            rpc_port=self.rpc_port.value(),
            stream_port=self.stream_port.value(),
        )
        session = Session(settings)
        try:
            session.connect(profile=self.profile_box.currentData())
        except SessionError as exc:
            self.log(str(exc))
            self.statusBar().showMessage("Connection failed")
            return
        self.session = session
        self.connect_btn.setEnabled(False)
        self.disconnect_btn.setEnabled(True)
        self._show_status()
        self.launch_tab.apply_profile(session.profile)
        try:
            self.vessels_tab.refresh()
        except Exception as exc:
            self.log(f"Vessel refresh skipped: {exc}")
        try:
            self.career_tab.refresh()
        except Exception as exc:
            self.log(f"Career refresh skipped: {exc}")

    def disconnect_session(self) -> None:
        if self._task is not None and self._task.isRunning():
            self._task.request_abort()
        if self.session is not None:
            self.session.close()
        self.session = None
        self._constellation = None
        self.connect_btn.setEnabled(True)
        self.disconnect_btn.setEnabled(False)
        self.badges.setText("offline")
        self.statusBar().showMessage("Disconnected")
        self.log("Disconnected")

    def _show_status(self) -> None:
        assert self.session is not None
        st = self.session.status
        flags = [
            f"kRPC {st.krpc_version or '?'}",
            self.session.profile.display_name,
            "MechJeb" if st.mechjeb else "no MechJeb",
            "RealAntennas" if st.realantennas else "no RA",
            "RemoteTech" if st.remotetech else "no RT",
            "CommNet" if st.commnet else "no CommNet",
            "FAR" if st.far else "no FAR",
        ]
        self.badges.setText("  ·  ".join(flags))
        self.statusBar().showMessage("Connected")
        self.log(" · ".join(flags))

    def run_task(
        self,
        fn: Callable[[Task], Any],
        *,
        telemetry: Callable[[Any], None] | None = None,
        done: Callable[[Any], None] | None = None,
    ) -> None:
        if self._task is not None and self._task.isRunning():
            self.log("A task is already running")
            return
        if self.require_session() is None:
            return
        task = Task(fn, self)
        task.log_line.connect(self.log)
        if telemetry is not None:
            task.telemetry.connect(telemetry)
        task.failed.connect(self._task_failed)
        task.succeeded.connect(lambda result: self._task_done(result, done))
        task.finished.connect(self._task_idle)
        self._task = task
        self.launch_tab.launch_btn.setEnabled(False)
        self.launch_tab.abort_btn.setEnabled(True)
        task.start()

    def abort_task(self) -> None:
        if self._task is not None and self._task.isRunning():
            self._task.request_abort()
            self.log("Abort requested")

    def _task_failed(self, message: str) -> None:
        self.log(message)
        self.statusBar().showMessage("Task failed")

    def _task_done(self, result: Any, done: Callable[[Any], None] | None) -> None:
        self.statusBar().showMessage("Task finished")
        if done is not None:
            try:
                done(result)
            except Exception as exc:
                self.log(f"Follow-up failed: {exc}")

    def _task_idle(self) -> None:
        self.launch_tab.launch_btn.setEnabled(True)
        self.launch_tab.abort_btn.setEnabled(False)

    def closeEvent(self, event: Any) -> None:  # noqa: N802
        self.disconnect_session()
        super().closeEvent(event)


def main(argv: list[str] | None = None) -> int:
    raise SystemExit("UI is parked; run python main.py status|mun")
