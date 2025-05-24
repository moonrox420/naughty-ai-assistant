import sys
import os
import uuid
import asyncio
import requests
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton, QCheckBox, QLabel, QFileDialog
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QIcon
import markdown
import emoji

class NaughtyAIApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Naughty AI Assistant 😈")
        self.setGeometry(100, 100, 800, 600)

        self.naughty_mode = False
        self.messages = []
        self.backend_url = "http://127.0.0.1:8000"  # FastAPI backend URL

        self.init_ui()

        self.setStyle("Fusion")
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a1a1a;
            }
            QTextEdit, QTextEdit#chat_display {
                background-color: #2a2a2a;
                color: white;
                border: 1px solid #e53e3e;
            }
            QPushButton, QPushButton#send_button {
                background-color: #e53e3e;
                color: white;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #ff5555;
            }
            QCheckBox, QCheckBox#naughty_toggle {
                color: white;
            }
            QLabel, QLabel#upload_label {
                color: white;
            }
        """)
        self.setWindowIcon(QIcon("desktop/resources/icon.png"))

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        layout.addWidget(self.chat_display)

        self.upload_label = QLabel("Drop files here or click to upload, you rebel!")
        self.upload_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.upload_label.setAcceptDrops(True)
        layout.addWidget(self.upload_label)

        input_layout = QHBoxLayout()
        self.input_field = QTextEdit()
        self.input_field.setFixedHeight(50)
        input_layout.addWidget(self.input_field)

        send_button = QPushButton("Send")
        send_button.clicked.connect(self.send_message_async)
        input_layout.addWidget(send_button)

        upload_button = QPushButton("Upload")
        upload_button.clicked.connect(self.browse_file)
        input_layout.addWidget(upload_button)

        layout.addLayout(input_layout)

        controls_layout = QHBoxLayout()
        self.naughty_toggle = QCheckBox("Spicy Mode 😈")
        self.naughty_toggle.stateChanged.connect(self.toggle_naughty_mode)
        controls_layout.addWidget(self.naughty_toggle)

        emoji_button = QPushButton("😈")
        emoji_button.clicked.connect(self.show_emoji_picker)
        controls_layout.addWidget(emoji_button)

        layout.addLayout(controls_layout)

    def drag_enter_event(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def drop_event(self, event):
        files = [url.toLocalFile() for url in event.mimeData().urls()]
        if files:
            self.process_file(files[0])

    def browse_file(self, event=None):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File")
        if file_path:
            self.process_file(file_path)

    def process_file(self, file_path):
        try:
            with open(file_path, "rb") as f:
                files = {"file": (os.path.basename(file_path), f)}
                response = requests.post(f"{self.backend_url}/upload", files=files)
                response.raise_for_status()
                result = response.json()

            response_text = result.get("response", "No response from backend")
            image_path = result.get("image_path", None)
            knowledge_base_info = result.get("knowledge_base", None)

            self.add_message(response_text, "ai", image_path=image_path)
            if knowledge_base_info:
                self.add_message(knowledge_base_info, "ai")
        except Exception as e:
            self.add_message(f"Oops, something broke while handling that file: {str(e)}", "ai")

    def send_message_async(self):
        message = self.input_field.toPlainText().strip()
        if not message:
            return
        self.add_message(message, "user")
        self.input_field.clear()

        QTimer.singleShot(0, lambda: asyncio.run(self.generate_response(message)))

    async def generate_response(self, message):
        try:
            if "fetch weather" in message.lower():
                city = message.replace("fetch weather", "").strip()
                response = requests.post(f"{self.backend_url}/chat", json={"message": message, "naughty_mode": self.naughty_mode})
                response.raise_for_status()
                result = response.json()
                self.add_message(result.get("response", "No response from backend"), "ai")
                return
            elif "execute plugin" in message.lower():
                parts = message.replace("execute plugin", "").strip().split()
                if len(parts) >= 2:
                    plugin_name, function_name = parts[:2]
                    response = requests.post(f"{self.backend_url}/chat", json={"message": message, "naughty_mode": self.naughty_mode})
                    response.raise_for_status()
                    result = response.json()
                    self.add_message(result.get("response", "No response from backend"), "ai")
                else:
                    self.add_message("Please specify plugin and function, e.g., 'execute plugin myplugin myfunction'", "ai")
                return
            elif "semantic search" in message.lower():
                query = message.replace("semantic search", "").strip()
                response = requests.post(f"{self.backend_url}/semantic_search", json={"query": query})
                response.raise_for_status()
                result = response.json()
                self.add_message(result.get("response", "No response from backend"), "ai")
                return

            response = requests.post(f"{self.backend_url}/chat", json={"message": message, "naughty_mode": self.naughty_mode})
            response.raise_for_status()
            result = response.json()
            self.add_message(result.get("response", "No response from backend"), "ai", reaction_id=str(uuid.uuid4()))
        except Exception as e:
            self.add_message(f"Error: {str(e)}", "ai")

    def add_message(self, text, sender, image_path=None, reaction_id=None):
        self.messages.append({"text": text, "sender": sender, "image_path": image_path, "reaction_id": reaction_id})
        self.update_chat_display()

    def update_chat_display(self):
        html = ""
        for msg in self.messages:
            color = "#3b82f6" if msg["sender"] == "user" else "#e53e3e"
            text = markdown.markdown(emoji.emojize(msg["text"]))
            html += f'<p style="color: white; background-color: {color}; padding: 8px; border-radius: 8px; margin: 4px; display: inline-block;">{text}</p>'
            if msg["image_path"]:
                html += f'<img src="{msg["image_path"]}" style="max-width: 200px; border-radius: 8px; margin: 4px;" />'
            if msg["reaction_id"]:
                html += '<div style="margin: 4px;">'
                for em in ["😈", "🔥", "😘"]:
                    html += f'<span style="cursor: pointer;" onclick="this.parentNode.parentNode.innerHTML+=\'<p style=\\\'color: white; background-color: #e53e3e; padding: 8px; border-radius: 8px; margin: 4px; display: inline-block;\\\'>You hit me with a {em}? Oh, you’re trouble—let’s code something *filthy* next! 😈</p>\'">{em}</span> '
                html += '</div>'
            html += "<br>"
        self.chat_display.setHtml(html)
        self.chat_display.verticalScrollBar().setValue(self.chat_display.verticalScrollBar().maximum())

    def toggle_naughty_mode(self, state):
        self.naughty_mode = state == Qt.CheckState.Checked.value
        self.add_message("Spicy mode " + ("ON! Let’s get *wild* 😈" if self.naughty_mode else "OFF. Keeping it tame, you tease 😘"), "ai")

    def show_emoji_picker(self):
        emojis = ["😈", "🔥", "😘", "😉", "💾"]
        for em in emojis:
            self.input_field.insertPlainText(em)
        self.add_message("Pick an emoji, you naughty coder! 😈", "ai")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NaughtyAIApp()
    window.show()
    sys.exit(app.exec())