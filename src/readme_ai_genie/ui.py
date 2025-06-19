import questionary
from rich.console import Console
from rich.text import Text

console = Console()


def _review_single_section(section, section_number, total_sections, is_skipped_review=False):
    """Handles the review logic for a single section of the README."""
    # Suggestion 2: Display section titles for cleaner UX.
    title = section.split('\n')[0].replace('#', '').strip()
    console.print(f"\n[green]🔍 Reviewing: {title} ({section_number}/{total_sections})[/green]")

    # Preview with basic syntax highlighting
    console.print("[blue]--- AI Draft Section ---[/blue]")
    console.print(Text(section, style="grey50"))
    console.print("[blue]------------------------[/blue]")

    choices = ["✅ Approve", "✏️ Edit", "❌ Discard"]
    # Suggestion 1: Add a skip option for the main review loop.
    if not is_skipped_review:
        choices.append("⏭️ Skip (Decide later)")

    action = questionary.select(
        "How do you want to handle this section?",
        choices=choices,
    ).ask()

    if action == "✅ Approve":
        return {"status": "approved", "content": section}
    elif action == "✏️ Edit":
        edited_section = questionary.text(
            "Edit the section (your editor might not open, edit here):",
            multiline=True,
            default=section,
        ).ask()
        return {"status": "approved", "content": edited_section}
    elif action == "⏭️ Skip (Decide later)":
        return {"status": "skipped", "content": section}

    # Discard returns a discarded status
    return {"status": "discarded"}


def review_and_finalize(ai_draft, auto_approve=False):
    """Guides the user through reviewing the AI draft with legendary UX."""
    if auto_approve:
        console.print("[yellow]--yes flag detected. Auto-approving the AI draft.[/yellow]")
        return ai_draft.strip()

    sections = ai_draft.split("\n#")
    processed_sections = ["#" + s.strip() for s in sections if s.strip()]

    global_action = questionary.select(
        "An AI draft is ready. How would you like to proceed?",
        choices=[
            "Go section-by-section for a detailed review",
            "✅ Approve All (Accept the entire draft as is)",
            "❌ Discard All (Cancel the operation)",
        ],
    ).ask()

    if "Approve All" in global_action:
        return ai_draft.strip()

    if not global_action or "Discard All" in global_action:
        # Suggestion 3: Confirm before full discard to prevent rage-quits.
        confirm = questionary.confirm("Are you sure you want to discard all AI content?").ask()
        if confirm:
            console.print("[yellow]Operation cancelled. No file will be written.[/yellow]")
            return ""
        else:
            # If they don't confirm, restart the process.
            return review_and_finalize(ai_draft, auto_approve)

    final_content_list = []
    skipped_sections = []

    # Main review loop
    for i, section in enumerate(processed_sections):
        result = _review_single_section(section, i + 1, len(processed_sections))
        if result["status"] == "approved":
            final_content_list.append(result["content"])
        elif result["status"] == "skipped":
            skipped_sections.append(result["content"])

    # Review skipped sections if any exist
    if skipped_sections:
        console.print("\n[magenta bold]--- 📝 Reviewing Skipped Sections ---[/magenta bold]")
        for i, section in enumerate(skipped_sections):
            result = _review_single_section(section, i + 1, len(skipped_sections), is_skipped_review=True)
            if result["status"] == "approved":
                final_content_list.append(result["content"])

    if not final_content_list:
        console.print("[yellow]All sections were discarded. No file will be written.[/yellow]")
        return ""

    return "\n\n".join(final_content_list).strip()
