import sys
import os
import uuid
import asyncio
import torch
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton, QCheckBox, QLabel, QFileDialog
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QIcon
import markdown
import emoji
from llama_cpp import Llama
from backend.utils import (
    setup_encryption, scan_file, extract_pdf_text, analyze_image,
    process_audio, analyze_data, generate_code, review_code, detect_bugs
)

class NaughtyAIApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Naughty AI Assistant 😈")
        self.setGeometry(100, 100, 800, 600)

        self.upload_folder = "uploads"
        os.makedirs(self.upload_folder, exist_ok=True)
        self.fernet = setup_encryption()
        self.naughty_mode = False
        self.messages = []
        self.conversation_history = []

        try:
            model_path = "C:/Users/dusti/Projects/Llama-3-Groq-8B-Tool-Use-Q8_0-GGUF/llama-3-groq-8b-tool-use-q8_0.gguf"
            self.llm = Llama(model_path=model_path, n_ctx=2048)
        except Exception as e:
            print(f"Failed to load LLaMA model: {e}")
            self.llm = None

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
            filename = os.path.basename(file_path)
            dest_path = os.path.join(self.upload_folder, filename)

            with open(file_path, "rb") as src, open(dest_path, "wb") as dst:
                dst.write(src.read())

            scan_result = scan_file(dest_path)
            if scan_result and scan_result[dest_path] != "OK":
                os.remove(dest_path)
                self.add_message(f"File infected: {scan_result[dest_path]}", "ai")
                return
            else:
                self.add_message("File clean, you sexy rebel! Ready to get wild?", "ai")

            with open(dest_path, "rb") as f:
                file_data = f.read()
            encrypted_data = self.fernet.encrypt(file_data)
            encrypted_path = os.path.join(self.upload_folder, f"enc_{filename}")
            with open(encrypted_path, "wb") as f:
                f.write(encrypted_data)

            if filename.endswith((".pdf", ".txt")):
                text = extract_pdf_text(dest_path)
                self.add_message(text[:500] + "..." if len(text) > 500 else text, "ai")
            elif filename.lower().endswith((".png", ".jpg", ".jpeg")):
                image_desc = analyze_image(dest_path)
                self.add_message(f"Hot pic, darling! Here’s what I see: {image_desc} 😘", "ai", image_path=dest_path)
            elif filename.lower().endswith((".mp3", ".wav")):
                audio_desc = process_audio(dest_path)
                self.add_message(f"Naughty audio, huh? Here’s what I hear: {audio_desc} 🎵", "ai")
            elif filename.lower().endswith((".csv", ".xlsx")):
                data_insights = analyze_data(dest_path)
                self.add_message(f"Crunching numbers like a pro! Here’s the scoop: {data_insights} 📊", "ai")
            else:
                self.add_message("File processed, but I’m keeping it *steamy* and mysterious 😘", "ai")
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
            if self.llm is None:
                self.add_message("LLM not loaded, you naughty coder! 😈", "ai")
                return

            prompt = (
                f"You’re a sassy, naughty AI coder who’s *obsessed* with {message}. "
                f"Respond with a flirty, coding-focused vibe, sharp and professional. "
                f"{'Crank the naughtiness to 11—make it sinfully clever 😈' if self.naughty_mode else 'Keep it playful but not too wild, you tease 😘'}"
            )

            if self.conversation_history:
                full_prompt = "<|endoftext|>".join(self.conversation_history) + "<|endoftext|>" + prompt
            else:
                full_prompt = prompt

            response = self.llm.create_chat_completion(
                messages=[
                    {"role": "user", "content": full_prompt}
                ],
                max_tokens=150,
                temperature=1.0 if self.naughty_mode else 0.9,
                top_p=0.95
            )
            generated_text = response['choices'][0]['message']['content']

            self.conversation_history.append(prompt)
            self.conversation_history.append(generated_text)
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]

        except Exception as e:
            generated_text = f"Error: {str(e)}"

        self.add_message(generated_text, "ai", reaction_id=str(uuid.uuid4()))

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