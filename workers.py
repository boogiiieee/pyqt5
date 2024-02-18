from typing import Any, Callable

from loguru import logger
from PyQt5.QtCore import QObject, QRunnable, pyqtSignal, pyqtSlot


class WorkerSignals(QObject):
    finished: pyqtSignal = pyqtSignal()
    result: pyqtSignal = pyqtSignal(object)
    # error: pyqtSignal = pyqtSignal()


class Worker(QRunnable):
    def __init__(self, name: str, function: Callable[..., Any] | Any) -> None:
        super().__init__()
        self.fn = function
        self.signals: WorkerSignals = WorkerSignals()

    @pyqtSlot()
    def run(self) -> None:
        try:
            result = self.fn
            logger.debug(f"{result}")
        except Exception as e:
            logger.error(f"Worker error {e}")
        else:
            self.signals.result.emit(result)
            logger.debug("Returned thread result")
        finally:
            self.signals.finished.emit()
            logger.debug("Finished thread")
