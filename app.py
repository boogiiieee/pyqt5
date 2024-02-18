import sys
from datetime import timedelta
from typing import Any, Callable, Dict, List, Tuple

import psutil
from loguru import logger
from PyQt5.QtCore import QThreadPool, QTimer
from PyQt5.QtWidgets import QApplication, QDesktopWidget, QGridLayout, QLabel, QMainWindow, QPushButton, QWidget

from configs import TIMER_INTERVAL, WINDOW_HEIGHT, WINDOW_LEFT, WINDOW_TITLE, WINDOW_TOP, WINDOW_WIDTH
from workers import Worker


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(WINDOW_TITLE.title())
        self.setGeometry(WINDOW_LEFT, WINDOW_TOP, WINDOW_WIDTH, WINDOW_HEIGHT)
        self.__center()

        self.timer: QTimer = QTimer()
        self.timer.setInterval(TIMER_INTERVAL)
        self.timer.timeout.connect(self.monitoring)

        self.label1 = QLabel("Текущую загрузку ЦП:")
        self.label2 = QLabel("Затраченное время ЦП юзером:")
        self.label3 = QLabel("ОЗУ:")
        self.label4 = QLabel("Кол-во процессов:")
        self.label5 = QLabel("Батарея:")
        self.label6 = QLabel("SWAP:")
        self.label7 = QLabel("HDD:")
        self.label8 = QLabel("Диск I/O:")
        self.label9 = QLabel("Сеть I/O:")
        self.label10 = QLabel("Время загрузки системы:")

        layout: QGridLayout = QGridLayout()

        self.button_start: QPushButton = QPushButton("START")
        self.button_stop: QPushButton = QPushButton("STOP")
        self.button_stop.setEnabled(False)

        self.button_start.pressed.connect(self.start)
        self.button_stop.released.connect(self.stop)

        layout.addWidget(self.label1, 0, 0, 1, 2)
        layout.addWidget(self.label2, 0, 0, 2, 2)
        layout.addWidget(self.label3, 0, 0, 3, 2)
        layout.addWidget(self.label4, 0, 0, 4, 2)
        layout.addWidget(self.label5, 0, 0, 5, 2)
        layout.addWidget(self.label6, 0, 0, 6, 2)
        layout.addWidget(self.label7, 0, 0, 7, 2)
        layout.addWidget(self.label8, 0, 0, 8, 2)
        layout.addWidget(self.label9, 0, 0, 9, 2)
        layout.addWidget(self.label10, 0, 0, 10, 2)

        layout.addWidget(self.button_start, 9, 0)
        layout.addWidget(self.button_stop, 9, 1)

        widget: QWidget = QWidget()
        widget.setLayout(layout)

        self.setCentralWidget(widget)

        logger.info("Start gui interface...")
        self.show()

        self.threadpool: QThreadPool = QThreadPool()
        self.threadpool.setMaxThreadCount(10)
        logger.debug(f"Multithreading with maximum {self.threadpool.maxThreadCount()} threads")
        logger.debug(f"Active threads: {self.threadpool.activeThreadCount()}")

    def __center(self) -> None:
        geometry_main_window = self.frameGeometry()
        center_point_of_screen = QDesktopWidget().availableGeometry().center()
        geometry_main_window.moveCenter(center_point_of_screen)
        # top left of rectangle becomes top left of window centering it
        self.move(geometry_main_window.topLeft())
        logger.debug("Drawing the window in the center")

    def stop(self) -> None:
        self.timer.stop()
        logger.debug("Stop monitoring")
        self.threadpool.clear()
        logger.debug("Removes the runnables that are not yet started from the queue.")
        self.button_start.setEnabled(True)
        self.button_stop.setEnabled(False)

    def start(self) -> None:
        self.timer.start()
        logger.debug("Start monitoring")
        self.button_start.setEnabled(False)
        self.button_stop.setEnabled(True)

    def get_result_by_thread(self, data: Tuple | float | List) -> None:
        if isinstance(data, float):
            self.label1.setText(f"Текущую загрузку ЦП: {str(data)}%")
        elif isinstance(data, tuple) and type(data).__name__ == "scputimes":
            self.label2.setText(f"Затраченное время ЦП юзером: {str(timedelta(seconds=int(data[2])))}")
        elif isinstance(data, tuple) and type(data).__name__ == "svmem":
            self.label3.setText(f"ОЗУ: Общая: {data[0] / (1024 ** 3)} Гб, " f"Используется {data[2]}%")
        elif isinstance(data, tuple) and type(data).__name__ == "sswap":
            self.label6.setText(
                f"SWAP: Всего {data[0] / (1024 ** 3)} Гб, "
                f"Используется {round(data[1] / (1024 ** 3), 3)} Гб, "
                f"Свободно {round(data[2] / (1024 ** 3), 3)} Гб"
            )
        elif isinstance(data, tuple) and type(data).__name__ == "sbattery":
            self.label5.setText(f"Батарея: {data[0]}%")
        elif isinstance(data, list):
            self.label4.setText(f"Кол-во процессов: {len(data)}")
        elif isinstance(data, tuple) and type(data).__name__ == "sdiskusage":
            self.label7.setText(f"HDD: Свободно {data[2] / (1024 ** 3)} Гб")
        elif isinstance(data, tuple) and type(data).__name__ == "sdiskio":
            self.label8.setText(f"Диск I/O: Кол-во операций чтения {data[0]}, " f"Кол-во операций записи {data[1]}")
        elif isinstance(data, tuple) and type(data).__name__ == "snetio":
            self.label9.setText(f"Сеть I/O: Кол-во отправленных байт {data[0]}, " f"Кол-во полученных байт {data[1]}")
        elif isinstance(data, tuple) and type(data).__name__ == "scpustats":
            self.label10.setText(f"CPU: системные вызовы {data[3]}")

    def monitoring(self) -> None:
        instance_names: Dict[str, Callable[..., Any]] = {
            "virtual_memory": psutil.virtual_memory(),
            "cpu_percent": psutil.cpu_percent(),
            "cpu_times": psutil.cpu_times(),
            "sensors_battery": psutil.sensors_battery(),
            "pids": psutil.pids(),
            "swap_memory": psutil.swap_memory(),
            "disk_usage": psutil.disk_usage("/"),
            "disk_io_counters": psutil.disk_io_counters(),
            "net_io_counters": psutil.net_io_counters(),
            "cpu_stats": psutil.cpu_stats(),
        }

        workers_obj = {name: Worker(name=name, function=fn) for name, fn in instance_names.items()}

        for _, obj in workers_obj.items():
            obj.signals.result.connect(self.get_result_by_thread)
            self.threadpool.start(obj)
        logger.debug(f"Active threads {self.threadpool.activeThreadCount()}")


if __name__ == "__main__":
    app: QApplication = QApplication(sys.argv)
    main: QMainWindow = MainWindow()
    sys.exit(app.exec_())
