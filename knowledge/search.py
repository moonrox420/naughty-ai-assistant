import os

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
