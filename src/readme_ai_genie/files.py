import os
import webbrowser
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt
import pathspec

console = Console()
MAX_BYTES = 1 * 1024 * 1024
ENV_FILE = '.env'
API_KEY_NAME = 'GROQ_API_KEY'
GROQ_KEY_URL = 'https://console.groq.com/keys'


# --- (ensure_api_key function remains the same) ---
def ensure_api_key():
    from dotenv import load_dotenv, set_key
    load_dotenv()
    api_key = os.getenv(API_KEY_NAME)
    if not api_key:
        console.print("\n[yellow]👀 Looks like this is your first time running the Genie![/yellow]")
        console.print("[cyan]🪄 You need a FREE Groq API key to summon AI magic.[/cyan]")
        console.print(f"[magenta]🌐 Opening {GROQ_KEY_URL}...[/magenta]")
        webbrowser.open(GROQ_KEY_URL)
        user_key = Prompt.ask("\n[green]🔑 Paste your new Groq API key here and press Enter[/green]")
        if not user_key or not user_key.strip():
            console.print("[red]❌ No API key entered. Exiting.[/red]")
            exit(1)
        env_path = Path.cwd() / ENV_FILE
        try:
            set_key(str(env_path), API_KEY_NAME, user_key.strip())
            os.environ[API_KEY_NAME] = user_key.strip()
        except Exception as e:
            console.print(f"[red]💔 Couldn't save key to {ENV_FILE}: {e}[/red]")
            exit(1)
        console.print(f"\n[green]✅ Your Groq API key has been saved to {ENV_FILE}. You're all set![/green]")


def get_project_files():
    """Scans the project directory, prioritizing important files for large projects."""
    root = Path.cwd()

    ignore_lines = [
        'node_modules', '.git', 'dist', 'coverage', 'README.md', '.env*', '__pycache__',
        '*.pyc', '*.pyo', '*.egg-info', 'venv/', '*.lock', '*.log',
    ]

    gitignore_path = root / '.gitignore'
    if gitignore_path.exists():
        with open(gitignore_path, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f.readlines() if line.strip() and not line.strip().startswith("#")]
            ignore_lines.extend(lines)

    spec = pathspec.PathSpec.from_lines('gitwildmatch', ignore_lines)

    all_files_paths = [p for p in root.rglob('*') if not spec.match_file(str(p.relative_to(root))) and p.is_file()]

    total_files = len(all_files_paths)
    files_to_process = all_files_paths

    # NEW: Hard limit on the number of files to analyze to protect the token budget
    MAX_FILES_TO_ANALYZE = 200
    if total_files > MAX_FILES_TO_ANALYZE:
        # Prioritize config, main entry points, and source files
        priority_patterns = ['pyproject.toml', 'package.json', 'requirements.txt', 'main.py', 'app.py', 'index.js']

        priority_files = [p for p in all_files_paths if p.name in priority_patterns]
        other_files = [p for p in all_files_paths if p.name not in priority_patterns]

        # Take all priority files, and fill the rest of the budget with other files
        files_to_process = priority_files + other_files
        files_to_process = files_to_process[:MAX_FILES_TO_ANALYZE]

    files_data = []
    for file_path in files_to_process:
        try:
            if file_path.stat().st_size > MAX_BYTES: continue

            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            relative_path = file_path.relative_to(root)
            files_data.append({'path': str(relative_path), 'content': content})

        except (IOError, OSError):
            continue

    return sorted(files_data, key=lambda x: x['path']), total_files
