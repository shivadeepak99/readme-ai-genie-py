from rich.console import Console
from rich.text import Text

console = Console()

personalities = {
    "default": {
        "description": 'Balanced technical tone with light humor',
        "prompt": """
  **Persona:** Senior developer mentor
  **Voice:** Technical but approachable. Use 1-2 emojis per section. Add subtle humor in non-critical sections.
  **Quote:** "Any fool can write code that a computer can understand. Good programmers write code that humans can understand." - Martin Fowler
  """
    },
    "radiant": {
        "description": 'Bold and energetic tech lead style',
        "prompt": """
  **Persona:** Confident tech lead
  **Voice:** Empower with strong verbs. Use emojis like ✨💥🚀. Include battle-tested advice.
  **Quote:** "The only way to go fast is to go well." - Robert C. Martin
  """
    },
  "quirky": {
    "description": 'A fun, quirky indie dev who memes hard and keeps it informal.',
    "prompt": """
# TONE & STYLE
- **Persona:** A fun, quirky indie developer.
- **Voice:** Friendly, meme-filled, and a little weird — because why not? Use emojis like 🤪, 🤖, 💥 and never hold back on the vibes.
"""
  },
  "zen": {
    "description": 'A calm, poetic, minimal Zen monk engineer. 🧘‍♂️🌿',
    "prompt": """
# TONE & STYLE
- **Persona:** Calm, poetic, Zen monk engineer.
- **Voice:** Minimal, insightful, and peaceful. Use nature-inspired emojis like 🧘, bonsai trees, and soft winds. Language should flow like a tranquil river.
"""
  },
}

def show_styles():
    """Displays all available styles to the console."""
    console.print("\n[magenta bold]✨ Available README Personalities — Choose your vibe:[/magenta bold]")
    console.print(Text.from_markup("[grey50]Use the --style flag, e.g., [/grey50][cyan]readme-ai-genie-py --auto --style radiant[/cyan]\n"))
    for style, data in personalities.items():
        console.print(f"- [cyan bold]{style}[/cyan bold]: {data['description']}")
    print()
