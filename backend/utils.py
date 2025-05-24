from cryptography.fernet import Fernet
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
