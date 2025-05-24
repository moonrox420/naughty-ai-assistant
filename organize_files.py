import os
import shutil

def organize_files():
    # Define the project root
    project_root = r"C:\Users\dusti\Projects\naughty-ai-assistant"

    # Define the directory structure and file locations
    structure = {
        "app": ["main.py"],
        "desktop": ["main.py"],
        "desktop/resources": ["icon.png"],
        "backend": ["utils.py"],
        "backend/uploads": [".gitkeep"],
        "automation": ["api.py"],
        "plugins": ["manager.py"],
        "knowledge": ["search.py"],
        "": ["requirements.txt", "README.md", "organize_files.py"]  # Root directory files
    }

    # Ensure all directories exist
    for directory in structure.keys():
        dir_path = os.path.join(project_root, directory)
        os.makedirs(dir_path, exist_ok=True)

    # Move files to their correct locations
    for directory, files in structure.items():
        for file in files:
            src_path = os.path.join(project_root, file)
            if os.path.exists(src_path):
                dest_path = os.path.join(project_root, directory, file)
                shutil.move(src_path, dest_path)
                print(f"Moved {file} to {dest_path}")
            else:
                print(f"File {file} not found in project root.")

if __name__ == "__main__":
    organize_files()