# coding=utf-8
# ========================
"""
Hythonium Browser - A lightweight web browser built with PyQt5 and QtWebEngine

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""
# ========================
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QLineEdit,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QMessageBox,
    QTabWidget,
    QPushButton,
)
from PyQt5.QtWebEngineWidgets import (
    QWebEngineView,
    QWebEngineProfile,
    QWebEngineDownloadItem,
    QWebEngineSettings,
)
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QFont
from types import ModuleType
import sys
import os


# Load Config
def load_external_config():
    """Load external config.py from the same directory as the exe"""
    if getattr(sys, "frozen", False):
        exe_dir = os.path.dirname(sys.executable)
    else:
        exe_dir = os.path.dirname(__file__)

    config_path = os.path.join(exe_dir, "config.py")
    if os.path.exists(config_path) and os.path.isfile(config_path):
        # Create a temporary module to save the configuration
        try:
            config_module = ModuleType("config")
            with open(config_path, "r", encoding="utf-8") as f:
                exec(f.read(), config_module.__dict__)
            return config_module.config
        except:
            return {}

    else:
        return {}


config = load_external_config()
print("Loaded config:", config)
homepage = config.get("homepage", "https://www.baidu.com")
search_engine = config.get("search_engine", "https://www.baidu.com/s?wd=")
new_tab = config.get("new_tab", "https://www.baidu.com")
download_folder = config.get("download_folder", "Downloads")
User_Agent = config.get(
    "User_Agent",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
)


class WebEngineView(QWebEngineView):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

    def createWindow(self, type):
        return self.main_window.create_new_tab(QUrl("about:blank"))


class Browser(QMainWindow):
    def __init__(self):
        super(Browser, self).__init__()
        self.setWindowTitle("Hythonium")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("font-family: 'Microsoft Yahei';")

        # Initialize download directory
        os.makedirs(download_folder, exist_ok=True)

        # Create tab widget
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)

        # URL bar and button
        self.url_bar = QLineEdit()
        self.url_bar.setFont(QFont("Microsoft Yahei", 10))
        self.url_bar.returnPressed.connect(self.navigate_to_url)

        # New tab button
        new_tab_btn = QPushButton("+")
        new_tab_btn.clicked.connect(lambda: self.create_new_tab(QUrl(new_tab)))
        new_tab_btn.setFixedSize(30, 30)

        # Layout settings
        top_layout = QVBoxLayout()
        header_layout = QHBoxLayout()
        header_layout.addWidget(new_tab_btn)
        header_layout.addWidget(self.url_bar, stretch=4)
        top_layout.addLayout(header_layout)
        top_layout.addWidget(self.tabs)

        container = QWidget()
        container.setLayout(top_layout)
        self.setCentralWidget(container)

        # Initial tab
        self.create_new_tab(QUrl(homepage))

        # Connect download signals
        QWebEngineProfile.defaultProfile().downloadRequested.connect(
            self.handle_download
        )

    def create_new_tab(self, url):
        new_tab = WebEngineView(self)
        new_tab.setUrl(url)
        new_tab.urlChanged.connect(self.update_url)

        index = self.tabs.addTab(new_tab, "Loading...")
        self.tabs.setCurrentIndex(index)

        new_tab.loadFinished.connect(
            lambda _, tab=new_tab: self.tabs.setTabText(
                self.tabs.indexOf(tab), tab.page().title()[:15]
            )
        )
        return new_tab

    def update_url(self, url):
        current_tab = self.tabs.currentWidget()
        if current_tab:
            self.url_bar.setText(url.toString())
            self.tabs.setTabText(
                self.tabs.currentIndex(), current_tab.page().title()[:15]
            )

    def navigate_to_url(self):
        url = self.url_bar.text().strip()
        if not url:
            return

        if not url.startswith(("http:", "https:", "file:", "ftp:")):
            url = search_engine + url

        if current_tab := self.tabs.currentWidget():
            current_tab.setUrl(QUrl(url))

    def close_current_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)

    def handle_download(self, download):
        """Handle download request"""
        # Generate safe file name
        filename = download.url().fileName()
        file_path = os.path.join(download_folder, filename)

        # Handle duplicate file names
        counter = 1
        base, ext = os.path.splitext(filename)
        while os.path.exists(file_path):
            file_path = os.path.join(download_folder, f"{base}({counter}){ext}")
            counter += 1

        # Configure download parameters
        download.setPath(file_path)
        download.accept()

        # Connect signals
        download.downloadProgress.connect(
            lambda recv, total: self.statusBar().showMessage(
                f"Downloading: {recv/1024:.1f}KB/{total/1024:.1f}KB"
                if total > 0
                else f"Receiving: {recv/1024:.1f}KB"
            )
        )
        download.finished.connect(lambda: self.show_download_complete(download))

    def show_download_complete(self, download):
        if download.state() == QWebEngineDownloadItem.DownloadCompleted:
            QMessageBox.information(
                self,
                "Download Complete",
                f"File saved to folder:\n{download.path()}\n\nSize: {os.path.getsize(download.path())/1024:.1f}KB",
            )
        else:
            QMessageBox.warning(self, "Warning", "File download failed.")


app = QApplication(sys.argv)

# Configure browser engine
profile = QWebEngineProfile.defaultProfile()
profile.setHttpUserAgent(User_Agent)
# Add font configuration
web_settings = profile.settings()
web_settings.setFontFamily(QWebEngineSettings.StandardFont, "Microsoft Yahei")
web_settings.setFontFamily(QWebEngineSettings.SerifFont, "Microsoft Yahei")
web_settings.setFontFamily(QWebEngineSettings.SansSerifFont, "Microsoft Yahei")
web_settings.setFontFamily(QWebEngineSettings.FixedFont, "Microsoft Yahei")
# Start window
print("Browser service started.")
window = Browser()
window.show()
sys.exit(app.exec_())
