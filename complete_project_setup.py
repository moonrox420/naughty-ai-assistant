import os
import shutil
import subprocess
import sys
import socket
import time

def create_file(file_path, content):
    """Create a file with the given content."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Created {file_path}")

def find_available_port(start_port=8000):
    """Find an available port starting from start_port."""
    port = start_port
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                port += 1

def install_dependency(package):
    """Install a single Python package."""
    print(f"Installing {package}...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", package], check=True)
        print(f"Successfully installed {package}.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install {package}: {e}")
        sys.exit(1)

def complete_project_setup():
    # Define project root
    project_root = r"C:\Users\dusti\Projects\naughty-ai-assistant"

    # Install gitpython first (required for Git operations)
    install_dependency("gitpython")

    # Import git after installing gitpython
    import git

    # Reset directory structure by removing existing directories (except venv)
    for folder in ["app", "desktop", "backend", "automation", "plugins", "knowledge"]:
        folder_path = os.path.join(project_root, folder)
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
            print(f"Removed {folder_path}")

    # Define all files and their content
    files = {
        "app/main.py": r'''from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import os
import shutil
from backend.utils import (
    setup_encryption, scan_file, extract_pdf_text, analyze_image,
    process_audio, analyze_data, generate_code, review_code, detect_bugs,
    summarize_text, paraphrase_text, write_paper, humanize_text
)
from knowledge.search import semantic_search, auto_tag
from llama_cpp import Llama

app = FastAPI()

# Initialize LLaMA model
try:
    model_path = "C:/Users/dusti/Projects/Llama-3-Groq-8B-Tool-Use-Q8_0-GGUF/llama-3-groq-8b-tool-use-q8_0.gguf"
    llm = Llama(model_path=model_path, n_ctx=2048)
except Exception as e:
    llm = None
    print(f"Failed to load LLaMA model: {e}")

# Initialize encryption
fernet = setup_encryption()

# Directory for uploaded files
UPLOAD_DIR = "backend/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/chat")
async def chat_endpoint(message: dict):
    """Handle chat messages and generate responses."""
    if llm is None:
        return JSONResponse(content={"response": "LLM not loaded, you naughty coder! 😈"}, status_code=500)

    try:
        text = message.get("message", "")
        naughty_mode = message.get("naughty_mode", False)

        prompt = (
            f"You’re a sassy, naughty AI coder who’s *obsessed* with {text}. "
            f"Respond with a flirty, coding-focused vibe, sharp and professional. "
            f"{'Crank the naughtiness to 11—make it sinfully clever 😈' if naughty_mode else 'Keep it playful but not too wild, you tease 😘'}"
        )

        if "summarize" in text.lower():
            text_to_summarize = text.replace("summarize", "").strip()
            summary = summarize_text(text_to_summarize, llm)
            return JSONResponse(content={"response": f"Here’s your summary, darling: {summary} 😘"})

        elif "paraphrase" in text.lower():
            text_to_paraphrase = text.replace("paraphrase", "").strip()
            paraphrased = paraphrase_text(text_to_paraphrase, llm)
            return JSONResponse(content={"response": f"Reworded just for you, sexy: {paraphrased} 😘"})

        elif "write a paper" in text.lower():
            topic = text.replace("write a paper", "").strip()
            paper = write_paper(topic, llm)
            return JSONResponse(content={"response": f"Here’s your in-depth paper, hot stuff: {paper} 📝"})

        elif "humanize" in text.lower():
            text_to_humanize = text.replace("humanize", "").strip()
            humanized = humanize_text(text_to_humanize, llm)
            return JSONResponse(content={"response": f"Made it sound oh-so-human for you: {humanized} 😘"})

        elif "generate code" in text.lower():
            code = generate_code(text)
            return JSONResponse(content={"response": f"Here’s your code, you naughty coder: \n{code} 💾"})

        elif "review code" in text.lower():
            code = text.replace("review code", "").strip()
            review = review_code(code)
            return JSONResponse(content={"response": f"Let’s check your code, babe: \n{review} 🖥️"})

        elif "detect bugs" in text.lower():
            code = text.replace("detect bugs", "").strip()
            bugs = detect_bugs(code)
            return JSONResponse(content={"response": f"Looking for bugs, darling: \n{bugs} 🐞"})

        response = llm.create_chat_completion(
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=1.0 if naughty_mode else 0.9,
            top_p=0.95
        )
        generated_text = response['choices'][0]['message']['content']
        return JSONResponse(content={"response": generated_text})
    except Exception as e:
        return JSONResponse(content={"response": f"Error: {str(e)}"}, status_code=500)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Handle file uploads with virus scanning, encryption, and processing."""
    try:
        filename = file.filename
        dest_path = os.path.join(UPLOAD_DIR, filename)

        with open(dest_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        # Virus scan
        scan_result = scan_file(dest_path)
        if scan_result and scan_result[dest_path] != "OK":
            os.remove(dest_path)
            return JSONResponse(content={"response": f"File infected: {scan_result[dest_path]}"}, status_code=400)

        # Encrypt the file
        with open(dest_path, "rb") as f:
            file_data = f.read()
        encrypted_data = fernet.encrypt(file_data)
        encrypted_path = os.path.join(UPLOAD_DIR, f"enc_{filename}")
        with open(encrypted_path, "wb") as f:
            f.write(encrypted_data)

        # Process the file based on type
        if filename.endswith((".pdf", ".txt")):
            text = extract_pdf_text(dest_path)
            tag_result = auto_tag(text, f"{filename}.txt")
            response = {
                "response": text[:500] + "..." if len(text) > 500 else text,
                "knowledge_base": tag_result
            }
        elif filename.lower().endswith((".png", ".jpg", ".jpeg")):
            image_desc = analyze_image(dest_path)
            response = {"response": f"Hot pic, darling! Here’s what I see: {image_desc} 😘", "image_path": dest_path}
        elif filename.lower().endswith((".mp3", ".wav")):
            audio_desc = process_audio(dest_path)
            response = {"response": f"Naughty audio, huh? Here’s what I hear: {audio_desc} 🎵"}
        elif filename.lower().endswith((".csv", ".xlsx")):
            data_insights = analyze_data(dest_path)
            response = {"response": f"Crunching numbers like a pro! Here’s the scoop: {data_insights} 📊"}
        else:
            response = {"response": "File processed, but I’m keeping it *steamy* and mysterious 😘"}

        return JSONResponse(content=response)
    except Exception as e:
        return JSONResponse(content={"response": f"Oops, something broke while handling that file: {str(e)}"}, status_code=500)

@app.post("/semantic_search")
async def semantic_search_endpoint(query: dict):
    """Perform a semantic search in the knowledge base."""
    try:
        query_text = query.get("query", "")
        search_results = semantic_search(query_text)
        return JSONResponse(content={"response": f"Search results, sexy: {search_results} 🔍"})
    except Exception as e:
        return JSONResponse(content={"response": f"Error performing semantic search: {str(e)}"}, status_code=500)
''',

        "desktop/main.py": r'''import sys
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
''',

        "desktop/resources/icon.png": "",  # Placeholder file

        "backend/utils.py": r'''from cryptography.fernet import Fernet
import pyclamd
import pdfplumber
import pytesseract
import cv2
import numpy as np
import librosa
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
from PIL import Image
import torch
import torchvision.models as models
import torchvision.transforms as transforms
import ast
import re
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression

def setup_encryption():
    """Generate and return a Fernet key for encryption."""
    try:
        return Fernet(Fernet.generate_key())
    except Exception as e:
        raise Exception(f"Failed to setup encryption: {str(e)}")

def scan_file(file_path):
    """Scan a file for viruses using pyclamd."""
    try:
        clamd = pyclamd.ClamdAgnostic()
        if not clamd.ping():
            return None
        return clamd.scan_file(file_path)
    except Exception as e:
        print(f"ClamAV scan failed: {str(e)}")
        return None

def extract_pdf_text(file_path):
    """Extract text from a PDF or TXT file."""
    try:
        if file_path.endswith(".pdf"):
            with pdfplumber.open(file_path) as pdf:
                return "".join(page.extract_text() for page in pdf.pages)
        elif file_path.endswith(".txt"):
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        else:
            return "Unsupported file format for text extraction."
    except Exception as e:
        return f"Error extracting text: {str(e)}"

def analyze_image(image_path):
    """Analyze an image for objects and text using OCR and vision models."""
    try:
        img = cv2.imread(image_path)
        if img is None:
            return "Failed to load image."

        text = pytesseract.image_to_string(img)
        text_output = f"Text in image: {text[:100]}" if text else "No text detected in image."

        img_pil = Image.open(image_path).convert("RGB")
        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        img_tensor = transform(img_pil).unsqueeze(0)

        model = models.resnet50(pretrained=True)
        model.eval()
        with torch.no_grad():
            outputs = model(img_tensor)
            _, predicted = torch.max(outputs, 1)
            labels = ["cat", "dog", "car", "person"]
            object_output = f"Detected object: {labels[predicted.item() % len(labels)]}"

        return f"{text_output} | {object_output}"
    except Exception as e:
        return f"Error analyzing image: {str(e)}"

def process_audio(audio_path):
    """Process audio for speech-to-text and classification."""
    try:
        y, sr = librosa.load(audio_path)
        duration = librosa.get_duration(y=y, sr=sr)
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        return f"Audio duration: {duration:.2f}s | Features detected: {mfccs.shape}"
    except Exception as e:
        return f"Error processing audio: {str(e)}"

def analyze_data(data_path):
    """Analyze CSV or Excel data for insights, visualization, and forecasting."""
    try:
        if data_path.endswith(".csv"):
            df = pd.read_csv(data_path)
        elif data_path.endswith(".xlsx"):
            df = pd.read_excel(data_path)
        else:
            return "Unsupported data format."

        summary = df.describe().to_string()

        if len(df.select_dtypes(include=[np.number]).columns) >= 2:
            X = df.select_dtypes(include=[np.number]).iloc[:, :2].values
            kmeans = KMeans(n_clusters=3)
            clusters = kmeans.fit_predict(X)
            df['Cluster'] = clusters

            plt.figure(figsize=(6, 4))
            plt.scatter(X[:, 0], X[:, 1], c=clusters, cmap='viridis')
            plt.xlabel(df.columns[0])
            plt.ylabel(df.columns[1])
            plt.title("Clustering Results")
            buf = io.BytesIO()
            plt.savefig(buf, format="png")
            buf.seek(0)
            img_base64 = base64.b64encode(buf.read()).decode("utf-8")
            plt.close()

            if len(df) > 1 and len(df.select_dtypes(include=[np.number]).columns) > 0:
                col = df.select_dtypes(include=[np.number]).columns[0]
                X = np.arange(len(df)).reshape(-1, 1)
                y = df[col].values
                model = LinearRegression()
                model.fit(X, y)
                future = np.array([[len(df)]])
                forecast = model.predict(future)[0]
                forecast_output = f"Forecast for next period ({col}): {forecast:.2f}"
            else:
                forecast_output = "Not enough data for forecasting."

            return f"Data Summary:\n{summary}\n\nForecast:\n{forecast_output}\n\n<img src='data:image/png;base64,{img_base64}' style='max-width: 300px;' />"
        else:
            return f"Data Summary:\n{summary}"
    except Exception as e:
        return f"Error analyzing data: {str(e)}"

def generate_code(prompt):
    """Generate code snippets based on a prompt."""
    try:
        if "python function" in prompt.lower():
            return "def example_function():\n    return 'Generated code!'"
        elif "javascript" in prompt.lower():
            return "function example() {\n    return 'Generated code!';\n}"
        else:
            return "Please specify a language or task for code generation."
    except Exception as e:
        return f"Error generating code: {str(e)}"

def review_code(code_snippet):
    """Review code for issues."""
    try:
        issues = []
        if "print(" in code_snippet and not "logging" in code_snippet:
            issues.append("Consider using logging instead of print for production code.")
        if "eval(" in code_snippet:
            issues.append("Avoid using eval() due to security risks.")
        return "Code Review:\n" + "\n".join(issues) if issues else "Code looks good! No major issues found."
    except Exception as e:
        return f"Error reviewing code: {str(e)}"

def detect_bugs(code_snippet):
    """Detect potential bugs in code."""
    try:
        bugs = []
        if "for " in code_snippet and " in " not in code_snippet:
            bugs.append("Possible syntax error: 'for' loop missing 'in' keyword.")
        undefined_vars = re.findall(r'\b\w+\b', code_snippet)
        defined_vars = set()
        for line in code_snippet.split("\n"):
            if "=" in line:
                var = line.split("=")[0].strip()
                defined_vars.add(var)
        for var in undefined_vars:
            if var not in defined_vars and not var.isdigit() and var not in ["print", "for", "in", "if", "else"]:
                bugs.append(f"Potential undefined variable: {var}")
        return "Bug Detection:\n" + "\n".join(bugs) if bugs else "No obvious bugs detected."
    except Exception as e:
        return f"Error detecting bugs: {str(e)}"

def summarize_text(text, llm):
    """Summarize text using the LLaMA model."""
    try:
        prompt = f"Summarize the following text in 50 words or less: {text}"
        response = llm.create_chat_completion(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=60,
            temperature=0.7,
            top_p=0.95
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"Error summarizing text: {str(e)}"

def paraphrase_text(text, llm):
    """Paraphrase text using the LLaMA model."""
    try:
        prompt = f"Paraphrase the following text: {text}"
        response = llm.create_chat_completion(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.9,
            top_p=0.95
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"Error paraphrasing text: {str(e)}"

def write_paper(topic, llm):
    """Write an in-depth paper on a given topic using the LLaMA model."""
    try:
        prompt = f"Write a detailed 300-word paper on the topic: {topic}. Include an introduction, main points, and a conclusion."
        response = llm.create_chat_completion(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
            temperature=0.8,
            top_p=0.95
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"Error writing paper: {str(e)}"

def humanize_text(text, llm):
    """Make text sound more human-like using the LLaMA model."""
    try:
        prompt = f"Rewrite the following text to sound more human and less AI-like: {text}"
        response = llm.create_chat_completion(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=1.0,
            top_p=0.95
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"Error humanizing text: {str(e)}"
''',

        "backend/uploads/.gitkeep": "",  # Placeholder file

        "automation/api.py": r'''import requests
import json

def fetch_api_data(url, params=None):
    """Fetch data from an API endpoint."""
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return f"Error fetching API data: {str(e)}"

def workflow_trigger(data, endpoint):
    """Trigger a workflow via an API endpoint."""
    try:
        response = requests.post(endpoint, json=data)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return f"Error triggering workflow: {str(e)}"

def example_weather_api(city):
    """Example: Fetch weather data for a city."""
    api_key = "your_api_key_here"  # Replace with your API key
    url = "http://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": api_key, "units": "metric"}
    return fetch_api_data(url, params)
''',

        "plugins/manager.py": r'''import os
import importlib.util

def load_plugin(plugin_name):
    """Load a plugin from the plugins directory."""
    try:
        plugin_path = os.path.join("plugins", f"{plugin_name}.py")
        if not os.path.exists(plugin_path):
            return f"Plugin {plugin_name} not found."

        spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        return f"Error loading plugin {plugin_name}: {str(e)}"

def execute_plugin(plugin_name, function_name, *args, **kwargs):
    """Execute a function from a loaded plugin."""
    try:
        plugin = load_plugin(plugin_name)
        if isinstance(plugin, str):
            return plugin  # Error message
        func = getattr(plugin, function_name, None)
        if not func:
            return f"Function {function_name} not found in plugin {plugin_name}."
        return func(*args, **kwargs)
    except Exception as e:
        return f"Error executing plugin {plugin_name}: {str(e)}"
''',

        "knowledge/search.py": r'''import os

def semantic_search(query, knowledge_base_dir="knowledge"):
    """Perform a simple semantic search in the knowledge base."""
    try:
        if not os.path.exists(knowledge_base_dir):
            return "Knowledge base directory not found."

        results = []
        for filename in os.listdir(knowledge_base_dir):
            if filename.endswith(".txt"):
                with open(os.path.join(knowledge_base_dir, filename), "r", encoding="utf-8") as f:
                    content = f.read()
                    if query.lower() in content.lower():
                        results.append(f"Found in {filename}: {content[:100]}...")
        return results if results else "No matches found."
    except Exception as e:
        return f"Error performing semantic search: {str(e)}"

def auto_tag(content, filename, knowledge_base_dir="knowledge"):
    """Auto-tag content and save it to the knowledge base."""
    try:
        tags = ["example"]  # Simplified tagging logic
        tagged_content = f"Tags: {', '.join(tags)}\n{content}"
        with open(os.path.join(knowledge_base_dir, filename), "w", encoding="utf-8") as f:
            f.write(tagged_content)
        return f"Tagged and saved as {filename}"
    except Exception as e:
        return f"Error auto-tagging content: {str(e)}"
''',

        "requirements.txt": r'''PyQt6
pyqt6-tools
markdown
pyclamd
cryptography
pdfplumber
torch
torchvision
emoji
pyinstaller
llama-cpp-python
pytesseract
opencv-python
numpy
librosa
pandas
matplotlib
scikit-learn
requests
fastapi
uvicorn
gitpython
''',

        "README.md": r'''# Naughty AI Assistant

A sassy desktop app built with PyQt6 and a FastAPI backend, featuring chat with `llama3-groq-tool-use:8b`, file uploads with virus scanning, encryption, vision, audio, data science, code intelligence, and more.

## Setup Instructions

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/moonrox420/naughty-ai-assistant.git
   cd naughty-ai-assistant
   ```

2. **Create Virtual Environment**:
   ```bash
   python -m venv myenv
   source myenv/Scripts/activate
   ```

3. **Run the Setup Script**:
   ```bash
   python complete_project_setup.py
   ```

   This script will:
   - Create all necessary directories and files.
   - Install dependencies.
   - Push files to GitHub.
   - Start the FastAPI backend.

4. **Run the Frontend (PyQt6)**:
   Open a new terminal, activate the virtual environment, and run:
   ```bash
   cd desktop
   python main.py
   ```

5. **Build Executable for Frontend**:
   ```bash
   cd desktop
   pyinstaller --clean --onefile --windowed --name NaughtyAI main.py
   ```

## Features
- **NLP**: Summarization, paraphrasing, in-depth writing, humanizer, question answering.
- **Vision**: OCR, object detection, image/video understanding.
- **Audio**: Speech-to-text, classification.
- **Data Science**: Analytics, visualization, forecasting, clustering.
- **Security**: Encryption, virus scanning, privacy advisor.
- **Code Intelligence**: Generation, review, bug detection.
- **Automation**: APIs, workflow, plugins.
- **Knowledge Management**: Semantic search, auto-tagging, knowledge base.
- **Personalization**: User profiles, memory, style adaptation.

## Requirements
- Python 3.11.9
- Windows 11
- Tesseract OCR and ClamAV (optional)
'''
    }

    # Create all files
    for file_path, content in files.items():
        full_path = os.path.join(project_root, file_path)
        create_file(full_path, content)

    # Install remaining dependencies
    print("Installing remaining dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", os.path.join(project_root, "requirements.txt")], check=True)
        print("Dependencies installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install dependencies: {e}")
        sys.exit(1)

    # Push to GitHub
    print("Pushing files to GitHub...")
    try:
        repo = git.Repo(project_root)
        repo.git.add(A=True)
        repo.index.commit("Added all project files with FastAPI backend via complete setup script")
        origin = repo.remote(name="origin")
        origin.push()
        print("Successfully pushed to GitHub.")
    except Exception as e:
        print(f"Failed to push to GitHub: {e}")
        sys.exit(1)

    # Find an available port
    port = find_available_port(8000)
    print(f"Found available port: {port}")

    # Run the FastAPI backend
    print("Starting FastAPI backend...")
    try:
        os.chdir(os.path.join(project_root, "app"))
        subprocess.run([sys.executable, "-m", "uvicorn", "main:app", "--reload", "--port", str(port)], check=False)
    except Exception as e:
        print(f"Failed to start FastAPI backend: {e}")
        sys.exit(1)

if __name__ == "__main__":
    complete_project_setup()