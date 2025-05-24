# Naughty AI Assistant

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
