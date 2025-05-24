from fastapi import FastAPI, UploadFile, File, HTTPException
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
