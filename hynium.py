# coding=utf-8
# ========================
"""
Hythonium Browser - A lightweight web browser built with PyQt5 and QtWebEngine.
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
    QListWidget,
    QComboBox,
    QMenu,
    QAction,
)
from PyQt5.QtWebEngineWidgets import (
    QWebEngineView,
    QWebEngineProfile,
    QWebEngineDownloadItem,
    QWebEngineSettings,
)
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtGui import QFont
import tkinter as tk
from tkinter import messagebox
from types import ModuleType
import sys
import os


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

        (
            self.config,
            self.homepage,
            self.search_engine,
            self.new_tab,
            self.download_folder,
            self.User_Agent,
        ) = load_loaded_config()

        # Initialize download directory
        os.makedirs(self.download_folder, exist_ok=True)

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
        new_tab_btn.clicked.connect(lambda: self.create_new_tab(QUrl(self.new_tab)))
        new_tab_btn.setFixedSize(30, 30)

        # Settings button
        self.config_btn = QPushButton("⚙")
        self.config_btn.clicked.connect(self.set_config)

        # History button
        self.history_btn = QPushButton("History")
        self.history_btn.clicked.connect(self.show_history)

        # Layout settings
        top_layout = QVBoxLayout()
        header_layout = QHBoxLayout()
        header_layout.addWidget(new_tab_btn)
        header_layout.addWidget(self.url_bar, stretch=4)
        header_layout.addWidget(self.history_btn)
        header_layout.addWidget(self.config_btn)
        top_layout.addLayout(header_layout)
        top_layout.addWidget(self.tabs)

        container = QWidget()
        container.setLayout(top_layout)
        self.setCentralWidget(container)

        # Initial tab
        self.create_new_tab(QUrl(self.homepage))

        # Initialize history
        self.history = []
        self.load_history()

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
            if url.toString() not in self.history:
                self.history.append(url.toString())
                self.save_history()

    def navigate_to_url(self):
        url = self.url_bar.text().strip().lower()
        if not url:
            return

        if not url.startswith(("http:", "https:", "file:", "ftp:", "about:")):
            if url.endswith(top_level_domains):
                url = "http://" + url
            else:
                url = self.search_engine + url

        if current_tab := self.tabs.currentWidget():
            current_tab.setUrl(QUrl(url))

    def close_current_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)

    def set_config(self):
        if not os.path.exists("config.py"):
            messagebox.showerror("Error", "config.py file not found.")
            return

        self.config_window = tk.Tk()
        self.config_window.title("Hythonium Config")
        self.config_window.geometry("1200x900")

        # Get screen width and height
        screen_width = self.config_window.winfo_screenwidth()
        screen_height = self.config_window.winfo_screenheight()

        # Calculate window position
        x = (screen_width / 2) - (1200 / 2)
        y = (screen_height / 2) - (900 / 2)

        # Set window position
        self.config_window.geometry("%dx%d+%d+%d" % (1200, 900, x, y))

        with open("config.py", "r", encoding="utf-8") as f:
            self.before_content = f.read()

        # Bind window close event to quit_config method
        self.config_window.protocol("WM_DELETE_WINDOW", self.quit_config)

        # Create a frame to hold buttons
        button_frame = tk.Frame(self.config_window)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # Create buttons and place them in the frame
        save_btn = tk.Button(
            button_frame,
            text="Save",
            command=lambda: self.save_config(self.config_text.get("1.0", tk.END)),
        )
        save_quit_btn = tk.Button(
            button_frame,
            text="Save & Quit",
            command=lambda: (
                self.save_config(self.config_text.get("1.0", tk.END)),
                self.config_window.destroy(),
            ),
        )
        save_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5, pady=5)
        save_quit_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5, pady=5)

        self.config_text = tk.Text(self.config_window, font=("Consolas", 14))
        self.config_text.insert(tk.END, self.before_content)
        self.config_text.pack(fill=tk.BOTH, expand=True)

        self.config_window.mainloop()

    def save_config(self, content):
        with open("config.py", "w", encoding="utf-8") as f:
            f.write(content)
        self.before_content = content
        (
            self.config,
            self.homepage,
            self.search_engine,
            self.new_tab,
            self.download_folder,
            self.User_Agent,
        ) = load_loaded_config()

    def quit_config(self):
        if self.config_text.get("1.0", tk.END).strip() != self.before_content.strip():
            if messagebox.askyesno(
                "Save Changes", "Do you want to save changes before quitting?"
            ):
                self.save_config(self.config_text.get("1.0", tk.END))
        self.config_window.destroy()

    def handle_download(self, download):
        filename = download.url().fileName()
        file_path = os.path.join(self.download_folder, filename)
        counter = 1
        base, ext = os.path.splitext(filename)
        while os.path.exists(file_path):
            file_path = os.path.join(self.download_folder, f"{base}({counter}){ext}")
            counter += 1
        download.setPath(file_path)
        download.accept()
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

    def show_history(self):
        self.history_window = QMainWindow()
        self.history_window.setWindowTitle("Hythonium History")
        self.history_window.setGeometry(100, 100, 600, 400)
        self.history_window.setStyleSheet("font-family: 'Microsoft Yahei';")

        history_list = QListWidget()
        history_list.addItems(self.history)

        # Delete button
        delete_btn = QPushButton("Delete Selected")
        delete_btn.clicked.connect(lambda: self.delete_selected_history(history_list))

        goto_btn = QPushButton("Go to Selected")
        goto_btn.clicked.connect(lambda: self.goto_selected_history(history_list))

        clear_btn = QPushButton("Clear All")
        clear_btn.clicked.connect(lambda: self.clear_all_history(history_list))

        # Layout settings
        top_layout = QVBoxLayout()
        top_layout.addWidget(history_list)
        top_layout.addWidget(delete_btn)
        top_layout.addWidget(goto_btn)
        top_layout.addWidget(clear_btn)

        container = QWidget()
        container.setLayout(top_layout)
        self.history_window.setCentralWidget(container)
        self.history_window.show()

    def delete_selected_history(self, history_list):
        selected_items = history_list.selectedItems()
        for item in selected_items:
            self.history.remove(item.text())
            history_list.takeItem(history_list.row(item))
        self.save_history()

    def goto_selected_history(self, history_list):
        selected_items = history_list.selectedItems()
        for item in selected_items:
            self.url_bar.setText(item.text())
            self.navigate_to_url()

    def clear_all_history(self, history_list):
        history_list.clear()
        self.history = []
        self.save_history()

    def load_history(self):
        """Load history from a file"""
        history_path = "history.txt"
        if os.path.exists(history_path) and os.path.isfile(history_path):
            try:
                with open(history_path, "r", encoding="utf-8") as f:
                    self.history = [line.strip() for line in f.readlines()]
            except Exception as e:
                print(f"Error loading history: {e}")

    def save_history(self):
        """Save history to a file"""
        history_path = "history.txt"
        try:
            with open(history_path, "w", encoding="utf-8") as f:
                for url in self.history:
                    f.write(url + "\n")
        except Exception as e:
            print(f"Error saving history: {e}")


# Load Config
def load_external_config():
    if getattr(sys, "frozen", False):
        exe_dir = os.path.dirname(sys.executable)
    else:
        exe_dir = os.path.dirname(__file__)

    config_path = os.path.join(exe_dir, "config.py")
    if os.path.exists(config_path) and os.path.isfile(config_path):
        try:
            config_module = ModuleType("config")
            with open(config_path, "r", encoding="utf-8") as f:
                exec(f.read(), config_module.__dict__)
            return config_module.config
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}

    else:
        return {}


def load_loaded_config():
    config = load_external_config()
    print("Loaded config:", config)
    homepage = config.get("homepage", "https://www.bing.com")
    search_engine = config.get("search_engine", "https://www.bing.com/search?q=")
    new_tab = config.get("new_tab", "https://www.bing.com")
    download_folder = config.get("download_folder", "Downloads")
    User_Agent = config.get(
        "User_Agent",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    )
    return config, homepage, search_engine, new_tab, download_folder, User_Agent


top_level_domains = (
    ".com",
    ".org",
    ".net",
    ".edu",
    ".gov",
    ".mil",
    ".biz",
    ".info",
    ".name",
    ".pro",
    ".aero",
    ".coop",
    ".museum",
    ".jobs",
    ".travel",
    ".cat",
    ".int",
    ".tel",
    ".mobi",
    ".asia",
    ".post",
    ".xxx",
    ".ac",
    ".ad",
    ".ae",
    ".af",
    ".ag",
    ".ai",
    ".al",
    ".am",
    ".ao",
    ".aq",
    ".ar",
    ".as",
    ".at",
    ".au",
    ".aw",
    ".ax",
    ".az",
    ".ba",
    ".bb",
    ".bd",
    ".be",
    ".bf",
    ".bg",
    ".bh",
    ".bi",
    ".bj",
    ".bm",
    ".bn",
    ".bo",
    ".br",
    ".bs",
    ".bt",
    ".bv",
    ".bw",
    ".by",
    ".bz",
    ".ca",
    ".cc",
    ".cd",
    ".cf",
    ".cg",
    ".ch",
    ".ci",
    ".ck",
    ".cl",
    ".cm",
    ".cn",
    ".co",
    ".cr",
    ".cu",
    ".cv",
    ".cx",
    ".cy",
    ".cz",
    ".de",
    ".dj",
    ".dk",
    ".dm",
    ".do",
    ".dz",
    ".ec",
    ".ee",
    ".eg",
    ".eh",
    ".er",
    ".es",
    ".et",
    ".eu",
    ".fi",
    ".fj",
    ".fk",
    ".fm",
    ".fo",
    ".fr",
    ".ga",
    ".gb",
    ".gd",
    ".ge",
    ".gf",
    ".gg",
    ".gh",
    ".gi",
    ".gl",
    ".gm",
    ".gn",
    ".gp",
    ".gq",
    ".gr",
    ".gs",
    ".gt",
    ".gu",
    ".gw",
    ".gy",
    ".hk",
    ".hm",
    ".hn",
    ".hr",
    ".ht",
    ".hu",
    ".id",
    ".ie",
    ".il",
    ".im",
    ".in",
    ".io",
)

app = QApplication(sys.argv)
User_Agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"

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
