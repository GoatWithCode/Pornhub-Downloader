import sys
import threading
import webbrowser
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout,
    QPushButton, QLineEdit, QLabel, QProgressBar, QListWidget, QListWidgetItem
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap
import yt_dlp

class PornhubDownloader(QWidget):
    update_progress_signal = pyqtSignal(int, str)
    update_status_signal = pyqtSignal(str)
    add_list_item_signal = pyqtSignal(str, str, dict)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pornhub Downloader by >>>G0at with Code<<<")
        self.setGeometry(100, 100, 500, 700)
        self.setStyleSheet("background-color: black; color: white;")
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        layout = QVBoxLayout()

        self.logo = QLabel()
        pixmap = QPixmap("logo.png")
        self.logo.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.logo.setAlignment(Qt.AlignCenter)

        self.url_label = QLabel("Video URL:")
        self.url_label.setStyleSheet("color: white; margin-bottom: 0px;")

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Video-URL hier einfügen")
        self.url_input.setStyleSheet("""
            QLineEdit {
                background-color: #2c2c2c; color: white; padding: 8px; border-radius: 6px; border: 1px solid #555; margin-top: 0px; margin-bottom: 5px;
            }
        """)

        self.open_browser_btn = QPushButton("🌐 Pornhub öffnen")
        self.open_browser_btn.clicked.connect(lambda: webbrowser.open("https://www.pornhub.com"))
        self.open_browser_btn.setStyleSheet("""
            QPushButton {
                background-color: #444444; color: white; border: none; border-radius: 6px; padding: 6px; margin-bottom: 10px;
            }
            QPushButton:hover {
                background-color: #666666;
            }
        """)

        self.add_url_btn = QPushButton("➕ Link hinzufügen")
        self.add_url_btn.clicked.connect(self.add_url_clicked)
        self.add_url_btn.setStyleSheet("""
            QPushButton {
                background-color: #007BFF; color: white; border: none; border-radius: 6px; padding: 6px; margin-bottom: 15px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)

        self.url_list = QListWidget()
        self.url_list.setStyleSheet("""
            QListWidget {
                background-color: #2c2c2c; color: white; border-radius: 6px; border: 1px solid #555; margin-bottom: 15px;
            }
        """)
        self.url_list.currentItemChanged.connect(self.on_list_selection_changed)

        self.download_btn = QPushButton("⬇️ Alle Videos herunterladen")
        self.download_btn.clicked.connect(self.start_download_all_thread)
        self.download_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF6600; color: black; border: none; border-radius: 10px; padding: 10px; font-weight: bold; margin-bottom: 5px;
            }
            QPushButton:hover {
                background-color: #FF8533;
            }
        """)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: white; margin-bottom: 0px;")

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("Noch kein Download gestartet")
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #3a3a3a; color: white; border: 1px solid #555; border-radius: 5px; text-align: center; margin-top: 0px;
            }
            QProgressBar::chunk {
                background-color: #FF6600; width: 20px;
            }
        """)

        layout.addWidget(self.logo)
        layout.addWidget(self.url_label)
        layout.addWidget(self.url_input)
        layout.addWidget(self.open_browser_btn)
        layout.addWidget(self.add_url_btn)
        layout.addWidget(self.url_list)
        layout.addWidget(self.download_btn)
        layout.addStretch(1)
        layout.addWidget(self.status_label)
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)

        self.update_progress_signal.connect(self.update_progress)
        self.update_status_signal.connect(self.update_status_label)
        self.add_list_item_signal.connect(self.add_item_to_list)

    def add_url_clicked(self):
        url = self.url_input.text().strip()
        if not url:
            self.update_status_signal.emit("⚠️ Bitte eine gültige URL eingeben.")
            return
        threading.Thread(target=self.fetch_video_info, args=(url,), daemon=True).start()
        self.update_status_signal.emit("🔍 Hole Videoinfos...")

    def fetch_video_info(self, url):
        try:
            ydl_opts = {'quiet': True, 'skip_download': True, 'no_warnings': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                title = info.get('title', 'Unbekannt')
                duration = info.get('duration', 0)
                channel = info.get('uploader') or info.get('channel') or 'Unbekannt'
                length_str = self.seconds_to_hms(duration)
                text = f"{title} [{length_str}] — {channel}"
                metadata = {'title': title, 'duration': length_str, 'channel': channel, 'url': url}
                self.add_list_item_signal.emit(url, text, metadata)
                self.update_status_signal.emit("✅ Videoinfo geladen")
        except Exception as e:
            self.update_status_signal.emit(f"❌ Fehler beim Laden der Videoinfos: {e}")

    def add_item_to_list(self, url, text, metadata):
        item = QListWidgetItem(text)
        item.setData(Qt.UserRole, url)
        item.setData(Qt.UserRole + 1, metadata)
        self.url_list.addItem(item)
        self.url_input.clear()

    def on_list_selection_changed(self, current, previous):
        pass

    def seconds_to_hms(self, seconds):
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        if h > 0:
            return f"{h}h {m}m {s}s"
        elif m > 0:
            return f"{m}m {s}s"
        else:
            return f"{s}s"

    def start_download_all_thread(self):
        urls = [self.url_list.item(i).data(Qt.UserRole) for i in range(self.url_list.count())]
        if not urls:
            self.update_status_signal.emit("⚠️ Keine Links in der Liste.")
            return
        threading.Thread(target=self.download_all_videos, args=(urls,), daemon=True).start()

    def update_progress(self, value, text=None):
        self.progress_bar.setValue(value)
        if text:
            self.progress_bar.setFormat(text)

    def update_status_label(self, message):
        self.status_label.setText(message)

    def download_all_videos(self, urls):
        download_folder = os.path.join(os.getcwd(), "downloads")
        if not os.path.exists(download_folder):
            os.makedirs(download_folder)

        self.update_status_signal.emit(f"⬇️ Starte Download von {len(urls)} Videos...")
        for idx, url in enumerate(urls, start=1):
            self.update_status_signal.emit(f"⬇️ Lade Video {idx}/{len(urls)} herunter...")
            self.update_progress_signal.emit(0, f"Video {idx} läuft...")
            try:
                ydl_opts = {
                    'outtmpl': os.path.join(download_folder, '%(title)s.%(ext)s'),
                    'format': 'best',
                    'progress_hooks': [self.progress_hook],
                    'quiet': True,
                    'no_warnings': True,
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
            except Exception as e:
                self.update_status_signal.emit(f"❌ Fehler bei Video {idx}: {str(e)}")
        self.update_progress_signal.emit(100, "✅ Alle Downloads abgeschlossen")
        self.update_status_signal.emit("✅ Fertig")

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            downloaded = d.get('downloaded_bytes', 0)
            total = d.get('total_bytes') or d.get('total_bytes_estimate')
            if total and downloaded:
                percent = int(downloaded / total * 100)
                self.update_progress_signal.emit(percent, f"{percent}% heruntergeladen")
            else:
                self.update_progress_signal.emit(0, "Download läuft...")
        elif d['status'] == 'finished':
            self.update_progress_signal.emit(100, "✅ Download abgeschlossen")
            self.update_status_signal.emit("✅ Fertig")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PornhubDownloader()
    window.show()
    sys.exit(app.exec_())
