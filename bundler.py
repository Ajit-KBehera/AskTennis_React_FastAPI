import os

# ---------------- CONFIGURATION ----------------
OUTPUT_FILE = "codebase_context.txt"
# Folders to ignore
IGNORE_DIRS = {
    ".git",
    "__pycache__",
    "venv",
    "env",
    ".idea",
    ".vscode",
    "node_modules",
    "dist",
    "build",
    "coverage",
    "logs",
    ".md",
    ".gitignore",
    ".env",
    ".DS_Store",
    ".db",
}
# Specific files to ignore
IGNORE_FILES = {"package-lock.json", "yarn.lock"}
# File extensions to include
INCLUDE_EXTS = {
    ".py",
    ".json",
    ".html",
    ".css",
    ".sql",
    ".txt",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
}
# -----------------------------------------------


def is_binary(file_path):
    """Check if file is likely binary (prevents reading images/pyc files)."""
    try:
        with open(file_path, "tr") as check_file:
            check_file.read()
            return False
    except:
        return True


def bundle_files():
    with open(OUTPUT_FILE, "w", encoding="utf-8") as outfile:
        # Walk through all directories
        for root, dirs, files in os.walk("."):
            # Modify dirs in-place to skip ignored directories
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

            for file in files:
                # Skip the output file itself, the script itself, and specific ignored files
                if file == OUTPUT_FILE or file == "bundler.py" or file in IGNORE_FILES:
                    continue

                # Check extension
                _, ext = os.path.splitext(file)
                if ext.lower() in INCLUDE_EXTS:
                    file_path = os.path.join(root, file)

                    # Optional: Skip binary files just in case
                    if is_binary(file_path):
                        continue

                    # Write the file header (VITAL for the AI to understand context)
                    outfile.write(f"\n{'=' * 20}\n")
                    outfile.write(f"FILE PATH: {file_path}\n")
                    outfile.write(f"{'=' * 20}\n\n")

                    # Write file content
                    try:
                        with open(file_path, "r", encoding="utf-8") as infile:
                            outfile.write(infile.read())
                        outfile.write("\n")  # Extra newline for separation
                    except Exception as e:
                        outfile.write(f"# Error reading file: {e}\n")

    print(f"Success! All code bundled into: {OUTPUT_FILE}")


if __name__ == "__main__":
    bundle_files()
