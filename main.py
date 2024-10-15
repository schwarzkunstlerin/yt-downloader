import sys
import os
import logging
import yt_dlp

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTabWidget, QPushButton,
    QLineEdit, QLabel, QProgressBar
)
from PyQt5.QtGui import QIcon  # Import QIcon do ustawienia ikony


# Konfiguracja loggera
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)


class YouTubeDownloader(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("YouTube Downloader")
        self.setGeometry(300, 300, 400, 200)

        # Ustawienie ikony
        self.setWindowIcon(QIcon("youtube-downloader.ico"))  # Zmień "icon.ico" na ścieżkę do Twojej ikony

        # Tworzenie zakładek
        self.tabs = QTabWidget()
        self.single_link_tab = QWidget()
        self.playlist_tab = QWidget()

        self.tabs.addTab(self.single_link_tab, "Pojedynczy link")
        # self.tabs.addTab(self.playlist_tab, "Playlista")

        # Konfiguracja zakładki pojedynczych linków
        self.setup_single_link_tab()

        # Konfiguracja zakładki playlist (do rozbudowania)
        self.setup_playlist_tab()

        # Layout główny
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)

    def get_tmp_dir(self):
        """Zwraca ścieżkę do folderu tmp i tworzy go, jeśli nie istnieje."""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        tmp_dir = os.path.join(current_dir, 'tmp')
        if not os.path.exists(tmp_dir):
            os.makedirs(tmp_dir)  # Tworzy folder tmp, jeśli nie istnieje
        return tmp_dir

    def setup_single_link_tab(self):
        """Konfiguracja zakładki do pobierania pojedynczych linków."""
        single_link_layout = QVBoxLayout()

        single_link_label = QLabel("Wprowadź link do filmu na YouTube:")
        self.single_link_input = QLineEdit()
        self.download_video_btn = QPushButton("Pobierz Film")
        self.download_audio_btn = QPushButton("Pobierz Muzykę")

        # Pasek postępu
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)  # Ukryty do momentu rozpoczęcia pobierania

        # Label do wyświetlania wiadomości lub błędów
        self.message_label = QLabel("")

        single_link_layout.addWidget(single_link_label)
        single_link_layout.addWidget(self.single_link_input)
        single_link_layout.addWidget(self.download_video_btn)
        single_link_layout.addWidget(self.download_audio_btn)
        single_link_layout.addWidget(self.progress_bar)
        single_link_layout.addWidget(self.message_label)

        self.single_link_tab.setLayout(single_link_layout)

        # Przypisanie funkcji do przycisków
        self.download_video_btn.clicked.connect(self.download_video)
        self.download_audio_btn.clicked.connect(self.download_audio)

    def setup_playlist_tab(self):
        """Konfiguracja zakładki do pobierania playlist."""
        playlist_layout = QVBoxLayout()

        playlist_label = QLabel("Wprowadź link do playlisty na YouTube:")
        self.playlist_input = QLineEdit()
        self.download_playlist_btn = QPushButton("Pobierz Playlistę")

        playlist_layout.addWidget(playlist_label)
        playlist_layout.addWidget(self.playlist_input)
        playlist_layout.addWidget(self.download_playlist_btn)

        self.playlist_tab.setLayout(playlist_layout)

        self.download_playlist_btn.clicked.connect(self.download_playlist)

    def update_progress_bar(self, percent):
        """Aktualizuje pasek postępu."""
        self.progress_bar.setValue(percent)

    def download_video(self):
        """Pobiera film z YouTube w najwyższej dostępnej jakości."""
        url = self.single_link_input.text()
        if not url:
            logging.warning("Brak linku do pobrania filmu.")
            self.message_label.setText("Błąd: Proszę podać prawidłowy link do YouTube.")
            return

        logging.info(f"Rozpoczynam pobieranie filmu: {url}")
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)  # Reset paska na 0 przed rozpoczęciem
        self.message_label.setText("")  # Resetowanie wiadomości

        try:
            ydl_opts = {
                'format': 'best',
                'progress_hooks': [self.ydl_hook],
                'outtmpl': '%(title)s.%(ext)s',
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            logging.info("Pobieranie filmu zakończone")
            self.message_label.setText("Sukces: Filmik został pobrany.")
        except Exception as e:
            logging.error(f"Błąd podczas pobierania filmu: {str(e)}")
            self.message_label.setText(f"Błąd: {str(e)}")
        finally:
            self.progress_bar.setVisible(False)  # Ukrycie paska po zakończeniu pobierania

    def get_ffmpeg_path(self):
        """Funkcja zwraca ścieżkę do FFmpeg w katalogu projektu."""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ffmpeg_path = os.path.join(current_dir, 'ffmpeg', 'bin', 'ffmpeg.exe')
        return ffmpeg_path

    def download_audio(self):
        """Pobiera ścieżkę dźwiękową z filmu z YouTube i zapisuje ją jako mp3."""
        url = self.single_link_input.text()
        if not url:
            self.message_label.setText("Proszę podać prawidłowy link do YouTube.")
            return

        logging.info(f"Rozpoczynam pobieranie muzyki: {url}")
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)  # Reset paska postępu

        # Pobieranie tymczasowych plików wideo do folderu tmp
        tmp_dir = self.get_tmp_dir()

        try:
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'progress_hooks': [self.ydl_hook],  # Dodanie paska postępu dla audio
                'ffmpeg_location': self.get_ffmpeg_path(),  # Użycie ścieżki do FFmpeg
                'outtmpl': '%(title)s.%(ext)s',  # Skierowanie tymczasowych plików do tmp
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            self.message_label.setText("Muzyka została pobrana jako mp3.")
        except Exception as e:
            logging.error(f"Błąd podczas pobierania muzyki: {str(e)}")
            self.message_label.setText(f"Błąd: {str(e)}")
        finally:
            self.progress_bar.setVisible(False)  # Ukrycie paska po zakończeniu pobierania


    def download_playlist(self):
        """Przykładowa funkcja do pobierania playlist (do rozbudowania)."""
        url = self.playlist_input.text()
        logging.info(f"Rozpoczynam pobieranie playlisty: {url}")
        self.message_label.setText("Pobieranie playlist nie jest jeszcze zaimplementowane.")

    def ydl_hook(self, d):
        """Funkcja odpowiedzialna za aktualizację paska postępu."""
        if d['status'] == 'downloading':
            percent = d['_percent_str'].strip().replace('%', '')  # Oczyszczenie procentu z niepotrzebnych znaków
            self.update_progress_bar(int(float(percent)))  # Konwersja procentów na liczbę całkowitą
        elif d['status'] == 'finished':
            logging.info("Pobieranie zakończone")
            self.progress_bar.setValue(100)  # Ustawienie paska na 100% po zakończeniu

# Inicjalizacja aplikacji
if __name__ == '__main__':
    app = QApplication(sys.argv)
    downloader = YouTubeDownloader()
    downloader.show()
    sys.exit(app.exec_())
