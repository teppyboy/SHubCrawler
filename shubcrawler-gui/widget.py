# This Python file uses the following encoding: utf-8
import logging
import os
import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtCore import QFile, Slot, QThread, Signal
from PySide6.QtUiTools import QUiLoader
from shubcrawler.proxy import ProxyManager
from shubcrawler.grabber import add_callback
from shubcrawler.file import File

logger = logging.getLogger("shubcrawler-gui")
if os.getenv("SHUBCRAWLER_GUI_DEBUG") == "1":
    logger.setLevel("DEBUG")
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    logger.addHandler(ch)
    logger.debug("User Interface logger is set to debug mode.")

if os.getenv("SHUBCRAWLER_DEBUG") == "1":
    crawler_logger = logging.getLogger("shubcrawler")
    crawler_logger.setLevel("DEBUG")
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    crawler_logger.addHandler(ch)
    crawler_logger.debug("Module logger is set to debug mode.")


class App:
    def __init__(self):
        self._proxymanager = ProxyManager()

    def run(self):
        logger.debug("Loading mitmproxy")
        self._proxymanager.start_proxy(8080)

    @staticmethod
    def ui_run(window):
        _cbs = []

        def _cb():
            @Slot(File)
            def set_url(file):
                window.urlTb.setPlainText(file.url)

            class Thread(QThread):
                signal = Signal(File)
                file = None

                def run(self):
                    self.signal.emit(self.file)
            thread = Thread()
            thread.signal.connect(set_url)

            def callback(file):
                thread.file = file
                thread.start()

            add_callback(callback)
        _cbs.append(_cb)
        for cb in _cbs:
            cb()

    def stop(self):
        self._proxymanager.stop_proxy()


class Widget(QWidget):
    def __init__(self):
        super(Widget, self).__init__()
        self._app = App()
        self.setWindowTitle("SHub File Grabber")
        self.load_ui()
        self._app.run()

    def load_ui(self):
        loader = QUiLoader()
        path = os.fspath(Path(__file__).resolve().parent / "form.ui")
        ui_file = QFile(path)
        ui_file.open(QFile.ReadOnly)
        self._app.ui_run(loader.load(ui_file, self))
        ui_file.close()

    def closeEvent(self, event):
        logger.debug(event)
        self._app.stop()


def main():
    app = QApplication([])
    widget = Widget()
    widget.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
