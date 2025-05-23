# Naughty AI Assistant

A sassy desktop app built with PyQt6, featuring chat with `llama3-groq-tool-use:8b`, file uploads with virus scanning, encryption, vision, audio, data science, code intelligence, and more.

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

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Download LLaMA Model**:
   - Clone the model repository:
     ```bash
     git clone https://huggingface.co/rumbleFTW/Llama-3-Groq-8B-Tool-Use-Q8_0-GGUF
     cd Llama-3-Groq-8B-Tool-Use-Q8_0-GGUF
     git lfs pull
     ```
   - Ensure `llama-3-groq-8b-tool-use-q8_0.gguf` is in `C:\Users\dusti\Projects\Llama-3-Groq-8B-Tool-Use-Q8_0-GGUF`.

5. **Install Additional Tools**:
   - **Tesseract OCR**: Download and install from [here](https://github.com/tesseract-ocr/tesseract).
   - **ClamAV**: Install for virus scanning (optional).

6. **Run the App**:
   ```bash
   cd desktop
   python main.py
   ```

7. **Build Executable**:
   ```bash
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
- **Personalization**: User profiles, memory, style adaptation.

## Requirements
- Python 3.11.9
- Windows 11
- Tesseract OCR and ClamAV (optional)