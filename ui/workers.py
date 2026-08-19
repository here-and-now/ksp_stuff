"""QThread wrapper so kRPC work does not freeze the UI."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from PyQt6.QtCore import QThread, pyqtSignal


class Task(QThread):
    log_line = pyqtSignal(str)
    telemetry = pyqtSignal(object)
    failed = pyqtSignal(str)
    succeeded = pyqtSignal(object)

    def __init__(self, fn: Callable[["Task"], Any], parent: Any = None) -> None:
        super().__init__(parent)
        self._fn = fn
        self._abort = False

    def request_abort(self) -> None:
        self._abort = True

    def aborted(self) -> bool:
        return self._abort

    def run(self) -> None:
        try:
            result = self._fn(self)
            self.succeeded.emit(result)
        except Exception as exc:
            self.failed.emit(f"{type(exc).__name__}: {exc}")
