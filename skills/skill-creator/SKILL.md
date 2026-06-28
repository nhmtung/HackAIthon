---
name: skill-creator
description: Create new skills, modify and improve existing skills, and measure skill performance. Use when users want to create a skill from scratch, edit, or optimize an existing skill, run evals to test a skill, benchmark skill performance with variance analysis, or optimize a skill's description for better triggering accuracy.
---

# Skill Creator

A skill for creating new skills and iteratively improving them.

At a high level, the process of creating a skill goes like this:

- Decide what you want the skill to do and roughly how it should do it.
- Write a draft of the skill in a directory like `skills/<name>/SKILL.md`.
- Create a few test prompts and run validation runs on them.
- Grade, aggregate, and iterate based on results.

## Skill Structure
Skills use a directory structure:
```
skills/skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter (name, description required)
│   └── Markdown instructions
```

YAML Frontmatter:
- `name`: unique identifier (lowercase, hyphens for spaces).
- `description`: complete description of what the skill does and when it should trigger. Make the description pushy to prevent undertriggering.
