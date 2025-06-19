import os
import httpx
import asyncio
import  json
from rich.console import Console
from .styles import personalities

console = Console()


def get_architect_prompt(files, pkg_info):
    badge_block = f"[![PyPI version](https://img.shields.io/pypi/v/{pkg_info.get('name')})](https://pypi.org/project/{pkg_info.get('name')}/)\n[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)"

    MAX_CONTEXT_CHARS = 12000
    file_manifest = "# Project File Structure\n"

    # Prioritize key files
    priority_files = []
    other_files = []
    priority_patterns = [
        'pyproject.toml', 'package.json', 'requirements.txt',
        'main.py', 'app.py', '__main__.py', 'cli.py', 'setup.py',
        'README.md', 'Dockerfile', '.env', 'config'
    ]

    for file_info in files:
        path = file_info['path']
        if any(p in path.lower() for p in priority_patterns):
            priority_files.append(file_info)
        else:
            other_files.append(file_info)

    # Process priority files first
    full_content_block = "\n\n# Full Content of Key Files\n"
    current_chars = 0
    processed_files = []

    for file_info in priority_files + other_files:
        content = file_info['content']
        if current_chars + len(content) < MAX_CONTEXT_CHARS:
            full_content_block += f"\n---\n\n// File: {file_info['path']}\n{content}\n"
            current_chars += len(content)
            processed_files.append(file_info['path'])

    # Add unprocessed files to manifest
    for file_info in files:
        if file_info['path'] not in processed_files:
            file_manifest += f"- `{file_info['path']}`\n"

    # Optimized prompt structure
    prompt_header = f"""
You are an expert technical writer. Generate a comprehensive README.md using ONLY the provided context. Structure MUST include:

1. **# Project Title** - Use: {pkg_info.get('name', 'Unknown')}
2. **Badges** - EXACTLY: {badge_block}
3. **## Tech Stack** - List ALL technologies from files
4. **## Features** - Bullet-pointed key features
5. **## Installation** - Step-by-step commands
6. **## Usage** - Code examples from files
7. **## How It Works** - Mermaid.js diagram of architecture
8. **## Contributing** - Guidelines
9. **## License** - MIT

Analyze file relationships. Infer functionality from:
- File paths and naming conventions
- Import/require statements
- Configuration patterns
- Entry point files

Return ONLY the README.md content without additional commentary.
"""
    final_prompt = prompt_header + file_manifest + full_content_block
    return final_prompt[:28000]  # Strict Groq limit


def get_stylist_prompt(style='default'):
    base_instructions = """
You are a senior developer applying final polish to a README. Perform EXACTLY these actions:

1. Add 🔥 one-line tagline under title
2. Insert relevant emojis in headers (max 3 per section)
3. Apply clean Markdown formatting
4. Add inspirational quote at end
5. Preserve ALL technical content
6. Maintain original section structure

Apply this personality:
"""
    if style not in personalities:
        style = 'default'
    return base_instructions + personalities[style]['prompt']

#
# def get_architect_prompt(files, pkg_info):
#     """
#     Builds a smart prompt with a file manifest and content of only the most critical files.
#     """
#     badge_block = f"[![PyPI version](https://img.shields.io/pypi/v/{pkg_info.get('name')})](https://pypi.org/project/{pkg_info.get('name')}/)\n[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)"
#
#     MAX_CONTEXT_CHARS = 12000
#
#     file_manifest = "# Project File Structure\n"
#     for file_info in files:
#         file_manifest += f"- `{file_info['path']}`\n"
#
#     full_content_block = "\n\n# Full Content of Key Files\n"
#     current_chars = 0
#     priority_patterns = [
#         'pyproject.toml', 'package.json', 'requirements.txt', 'main.py', 'app.py', '__main__.py', 'cli.py', 'setup.py'
#     ]
#
#     for file_info in files:
#         path = file_info['path']
#         content = file_info['content']
#
#         is_priority = any(p in path.lower() for p in priority_patterns)
#         if is_priority and (current_chars + len(content)) < MAX_CONTEXT_CHARS:
#             full_content_block += f"\n---\n\n// File: {path}\n{content}\n"
#             current_chars += len(content)
#
#     file_context = file_manifest + full_content_block
#
#     prompt_header = f"""
# You are an expert technical writer...
# Analyze the following project context...
# # EXPECTED SECTIONS...
# ---
# # PROJECT CONTEXT
# **Project Name:** {pkg_info.get('name', 'Unknown')}
# **Description:** {pkg_info.get('description', 'No description found.')}
# **Badges:**
# {badge_block}
# **Project Files Summary & Key Content:**
# """
#     final_prompt = prompt_header + file_context
#     if len(final_prompt) > 25000:
#         final_prompt = final_prompt[:25000] + "\n...[CONTEXT TRUNCATED]..."
#
#     return final_prompt
#
#
# def get_stylist_prompt(style='default'):
#     base_instructions = """
# You are a witty, stylish, and highly skilled open-source senior developer...
# # YOUR TASK...
# """
#     if style not in personalities:
#         console.print(f"[yellow]⚠️ Unknown style '{style}'. Using 'default' instead.[/yellow]")
#         style = 'default'
#     selected = personalities[style]
#     return base_instructions + '\n---\n' + selected['prompt']


# async def call_groq(prompt):
#     """Calls the Groq API with a given prompt, now with smart retries."""
#     api_key = os.getenv("GROQ_API_KEY")
#     if not api_key:
#         raise ValueError("GROQ_API_KEY not found in environment variables.")
#
#     model_name = os.getenv("GROQ_MODEL", "llama3-8b-8192")
#     console.print(f"[grey50]\n  └─ Calling the God of Speed ({model_name})...[/grey50]")
#
#     # --- The NEW "Patient General" Strategy ---
#     retries = 3
#     delay = 2  # Start with a 2-second delay
#
#     for attempt in range(retries):
#         try:
#             async with httpx.AsyncClient(timeout=60.0) as client:
#                 response = await client.post(
#                     'https://api.groq.com/openai/v1/chat/completions',
#                     headers={'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'},
#                     json={
#                         "messages": [{"role": "user", "content": prompt}],
#                         "model": model_name,
#                     }
#                 )
#
#                 # A 5xx error means the server stumbled. We should retry.
#                 if response.status_code >= 500:
#                     raise httpx.HTTPStatusError(f"Server error: {response.status_code}", request=response.request,
#                                                 response=response)
#
#                 response.raise_for_status()  # Will raise an error for 4xx client errors
#                 data = response.json()
#                 if not data.get("choices"): raise ValueError("API returned no choices.")
#
#                 # Success!
#                 return data["choices"][0]["message"]["content"].strip()
#
#         except httpx.HTTPStatusError as e:
#             # If it's a server error and we have retries left, we wait and try again.
#             if e.response.status_code >= 500 and attempt < retries - 1:
#                 console.print(f"[yellow]  └─ The oracle stumbled. Waiting {delay}s and trying again...[/yellow]")
#                 await asyncio.sleep(delay)
#                 delay *= 2  # Exponential backoff
#             else:
#                 # If it's a client error (like 413) or the last retry, we fail.
#                 console.print(f"[red]  └─ Groq API request failed: {e.response.status_code} {e.response.text}[/red]")
#                 raise
#         except Exception as e:
#             console.print(f"[red]  └─ Groq call failed: {e}[/red]")
#             raise
#
#     # If all retries fail, we raise the final error.
#     raise Exception("All retry attempts failed. The AI provider seems to be unavailable.")

async def call_groq(prompt):
    """Calls the Groq API with a given prompt, now with smart retries, including for 429."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in environment variables.")
    messages = [
        {
            "role": "system",
            "content": "You are an expert technical writer. Return ONLY the requested content without additional commentary."
        },
        {
            "role": "user",
            "content": prompt
        }
    ]
    model_name = os.getenv("GROQ_MODEL", "llama3-8b-8192")
    console.print(f"[grey50]\n  └─ Calling the God of Speed ({model_name})...[/grey50]")

    retries = 5  # Let's give it a few more tries for stubborn rate limits
    # We'll calculate the delay dynamically based on Groq's suggestion

    for attempt in range(retries):
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    'https://api.groq.com/openai/v1/chat/completions',
                    headers={'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'},
                    json={
                        "messages": messages,
                        "model": model_name,
                        "temperature": 0.2,  # Lower for more deterministic output
                        "max_tokens": 4096,  # Prevent runaway responses
                    }
                )

                # A 5xx error means the server stumbled. We should retry.
                if response.status_code >= 500:
                    raise httpx.HTTPStatusError(f"Server error: {response.status_code}", request=response.request,
                                                response=response)

                # --- NEW LOGIC FOR 429 ERRORS ---
                if response.status_code == 429:
                    error_data = response.json()
                    suggested_wait_time = 0
                    if 'error' in error_data and 'message' in error_data['error']:
                        # Try to parse the suggested time from the message
                        message = error_data['error']['message']
                        try:
                            # Look for 'Please try again in X.XXXs'
                            parts = message.split("try again in ")
                            if len(parts) > 1:
                                time_str = parts[1].split("s")[0]
                                suggested_wait_time = float(time_str)
                        except (ValueError, IndexError):
                            pass  # Fallback to default if parsing fails

                    # Ensure a minimum wait time, even if Groq doesn't suggest one
                    # Add your requested +10 seconds buffer
                    wait_delay = suggested_wait_time + 10
                    # Let's make sure it waits at least 15 seconds if nothing is suggested
                    wait_delay = max(wait_delay, 15)

                    if attempt < retries - 1:
                        console.print(
                            f"[yellow]  └─ Woah, too fast! Groq wants us to chill for {wait_delay:.2f}s. Taking a power nap...[/yellow]")
                        await asyncio.sleep(wait_delay)
                        continue  # Skip to the next attempt immediately
                    else:
                        console.print(
                            f"[red]  └─ Still hitting the rate limit after all attempts. You're too powerful, Badboy![/red]")
                        raise httpx.HTTPStatusError(f"Rate limit exceeded after {retries} retries.",
                                                    request=response.request, response=response)

                response.raise_for_status()  # Will raise an error for other 4xx client errors
                data = response.json()
                if not data.get("choices"): raise ValueError("API returned no choices.")

                # Success!
                return data["choices"][0]["message"]["content"].strip()

        except httpx.HTTPStatusError as e:
            # If it's a 5xx server error and we have retries left, we wait and try again with exponential backoff.
            # 429 is handled specifically above.
            if e.response.status_code >= 500 and attempt < retries - 1:
                # Default backoff for 5xx errors if no 429 specific retry happened
                current_delay = 2 * (2 ** attempt)  # Exponential backoff for 5xx
                console.print(
                    f"[yellow]  └─ The oracle stumbled (server error). Waiting {current_delay}s and trying again...[/yellow]")
                await asyncio.sleep(current_delay)
            else:
                # If it's another client error (like 401, 403) or the last retry for 5xx, we fail.
                console.print(f"[red]  └─ Groq API request failed: {e.response.status_code} {e.response.text}[/red]")
                raise
        except Exception as e:
            console.print(f"[red]  └─ Groq call failed unexpectedly: {e}[/red]")
            raise

    # If all retries fail for some reason (should be caught by exceptions above, but as a safeguard)
    raise Exception("All retry attempts failed. The AI provider seems to be unavailable or persistently rate-limiting.")


async def generate_readme_content(files, style='default', plain=False):
    """Orchestrates the two-step AI generation process using Groq."""
    pkg_info = {}
    try:
        import tomli as toml
        with open("pyproject.toml", "rb") as f:
            data = toml.load(f)
            pkg_info['name'] = data.get('project', {}).get('name')
            pkg_info['description'] = data.get('project', {}).get('description')
    except (ImportError, FileNotFoundError):
        pass

    console.print("[grey50]🔍 Generating factual draft from project manifest...[/grey50]")
    architect_prompt = get_architect_prompt(files, pkg_info)
    factual_draft = await call_groq(architect_prompt)

    if plain:
        console.print("[yellow]--plain flag detected. Skipping styling.[/yellow]")
        return factual_draft

    console.print("[grey50]💅 Styling the draft...[/grey50]")
    stylist_prompt = get_stylist_prompt(style) + f"\n---\n# RAW DRAFT:\n\n{factual_draft}"
    final_draft = await call_groq(stylist_prompt)

    return final_draft or factual_draft
