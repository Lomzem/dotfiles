"""Check the installed principles router, references, and harness entry points."""

from pathlib import Path
import re


def main():
    root = Path(__file__).resolve().parent
    index = (root / "README.md").read_text()
    references = set(root.glob("*.md")) - {root / "README.md", root / "SOURCES.md"}
    assert len(references) == 22, f"Expected 22 principles, found {len(references)}"
    linked = set()
    for document in root.glob("*.md"):
        for target in re.findall(r"\]\(([^)]+)\)", document.read_text()):
            if "://" in target:
                continue
            destination = (document.parent / target.split("#")[0]).resolve()
            assert destination.is_file(), f"{document.name}: missing {target}"
            if document.name == "README.md":
                linked.add(destination)
    assert references <= linked, "Router omits a principle"
    assert "every trigger" in index, "Router must assess all trigger branches"
    assert "in full" in index, "Router must load matching references in full"
    skill = root.parent / "skills/principles"
    entry = (skill / "SKILL.md").read_text()
    assert "disable-model-invocation: true" in entry, "Claude manual policy missing"
    assert "~/.agents/principles/README.md" in entry, "Manual entry uses another router"
    assert "allow_implicit_invocation: false" in (skill / "agents/openai.yaml").read_text(), "Codex manual policy missing"
    instructions = (root.parent / "global-instructions.md").read_text()
    assert "~/.agents/principles/README.md" in instructions, "Automatic pointer missing"
    for reference in references:
        assert "disable-model-invocation" not in reference.read_text(), f"{reference.name}: expected plain reference"
    print("OK: 22 indexed principles, local links, automatic pointer, and both manual policies")


if __name__ == "__main__":
    main()
