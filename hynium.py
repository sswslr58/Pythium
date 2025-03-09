# coding=utf-8
# ========================
# Hythonium Browser
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
from PyQt5.QtGui import QFont, QIcon
from types import ModuleType
import sys
import os


# Load Config
def load_external_config():
    """从exe同级目录加载外部config.py"""
    if getattr(sys, "frozen", False):
        exe_dir = os.path.dirname(sys.executable)
    else:
        exe_dir = os.path.dirname(__file__)

    config_path = os.path.join(exe_dir, "config.py")
    if os.path.exists(config_path):
        # 创建临时模块来保存配置
        config_module = ModuleType("config")
        with open(config_path, "r", encoding="utf-8") as f:
            exec(f.read(), config_module.__dict__)

        return config_module.config
    else:
        return {}


config = load_external_config()
print("Loaded config:", config)
homepage = config.get("homepage", "https://www.baidu.com")
search_engine = config.get("search_engine", "https://www.baidu.com/s?wd=")
new_tab = config.get("new_tab", "https://www.baidu.com")
save_folder = config.get("save_folder", "Downloads")
User_Agent = config.get(
    "User_Agent",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
)
default_dnload_filename = config.get("default_dnload_filename", "download_file")


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

        # 初始化下载目录
        os.makedirs(save_folder, exist_ok=True)

        # 创建标签页
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)

        # 地址栏和按钮
        self.url_bar = QLineEdit()
        self.url_bar.setFont(QFont("Microsoft Yahei", 10))
        self.url_bar.returnPressed.connect(self.navigate_to_url)

        # 下载相关控件
        self.download_input = QLineEdit()
        self.download_input.setPlaceholderText("输入下载URL后点击右侧按钮")
        download_btn = QPushButton("下载")
        download_btn.clicked.connect(self.load_download_url)

        # 新建标签页按钮
        new_tab_btn = QPushButton("+")
        new_tab_btn.clicked.connect(lambda: self.create_new_tab(QUrl(new_tab)))
        new_tab_btn.setFixedSize(30, 30)

        # 布局设置
        top_layout = QVBoxLayout()
        header_layout = QHBoxLayout()
        header_layout.addWidget(new_tab_btn)
        header_layout.addWidget(self.url_bar, stretch=4)
        header_layout.addWidget(self.download_input, stretch=3)
        header_layout.addWidget(download_btn, stretch=1)
        top_layout.addLayout(header_layout)
        top_layout.addWidget(self.tabs)

        container = QWidget()
        container.setLayout(top_layout)
        self.setCentralWidget(container)

        # 初始标签页
        self.create_new_tab(QUrl(homepage))

        # 连接下载信号
        QWebEngineProfile.defaultProfile().downloadRequested.connect(
            self.handle_download
        )

    def create_new_tab(self, url):
        new_tab = WebEngineView(self)
        new_tab.setUrl(url)
        new_tab.urlChanged.connect(self.update_url)

        index = self.tabs.addTab(new_tab, "加载中...")
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

    def load_download_url(self):
        """加载下载URL到当前标签页"""
        url = self.download_input.text().strip()
        if not url:
            QMessageBox.warning(self, "提示", "请输入下载地址")
            return

        if current_tab := self.tabs.currentWidget():
            current_tab.load(QUrl(url))

    def handle_download(self, download):
        """处理下载请求"""
        # 生成安全文件名
        filename = download.url().fileName() or default_dnload_filename
        file_path = os.path.join(save_folder, filename)

        # 处理重复文件名
        counter = 1
        base, ext = os.path.splitext(filename)
        while os.path.exists(file_path):
            file_path = os.path.join(save_folder, f"{base}({counter}){ext}")
            counter += 1

        # 配置下载参数
        download.setPath(file_path)
        download.accept()

        # 连接信号
        download.downloadProgress.connect(
            lambda recv, total: self.statusBar().showMessage(
                f"下载进度: {recv/1024:.1f}KB/{total/1024:.1f}KB"
                if total > 0
                else f"已接收: {recv/1024:.1f}KB"
            )
        )
        download.finished.connect(lambda: self.show_download_complete(download))

    def show_download_complete(self, download):
        if download.state() == QWebEngineDownloadItem.DownloadCompleted:
            QMessageBox.information(
                self,
                "下载完成",
                f"文件保存位置:\n{download.path()}\n\n大小: {os.path.getsize(download.path())/1024:.1f}KB",
            )  
        else:
            QMessageBox.warning(self, "下载失败", "文件下载未完成")


app = QApplication(sys.argv)

# 配置浏览器引擎
profile = QWebEngineProfile.defaultProfile()
profile.setHttpUserAgent(User_Agent)
# 新增字体配置
web_settings = profile.settings()
web_settings.setFontFamily(QWebEngineSettings.StandardFont, "Microsoft Yahei")
web_settings.setFontFamily(QWebEngineSettings.SerifFont, "Microsoft Yahei")
web_settings.setFontFamily(QWebEngineSettings.SansSerifFont, "Microsoft Yahei")
web_settings.setFontFamily(QWebEngineSettings.FixedFont, "Microsoft Yahei")
# 启动窗口
print("Browser service started.")
window = Browser()
window.show()
sys.exit(app.exec_())
