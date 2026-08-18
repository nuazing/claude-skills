# claude-skills

Eine kleine Sammlung von [Claude Code](https://claude.com/claude-code) Skills, die ich im Alltag nutze — und die vielleicht auch für andere nützlich sind.

Ein Skill ist ein Ordner mit einer `SKILL.md` (Anleitung für Claude) plus optionalen Skripten. Claude lädt ihn automatisch, sobald die Beschreibung zur Aufgabe passt — man muss ihn nicht per Namen aufrufen.

## Skills

| Skill | Was es macht |
| --- | --- |
| [`md-to-pdf`](skills/md-to-pdf) | Wandelt eine Markdown-Datei in ein sauberes, druckfertiges PDF um — Tabellenzeilen brechen nie über Seitenumbrüche, jede Seite bekommt eine „N / total"-Fusszeile, optionale Akzentfarbe. Läuft über ein gebündeltes Python-Skript statt über eine jedes Mal neu erfundene HTML/CSS-Pipeline. |

## Installation

Skills liegen in `~/.claude/skills/` (persönlich, projektübergreifend) oder in `.claude/skills/` innerhalb eines Projekts.

### Einzelnen Skill installieren

```bash
git clone https://github.com/nuazing/claude-skills.git /tmp/claude-skills && cp -R /tmp/claude-skills/skills/md-to-pdf ~/.claude/skills/
```

### Alle Skills installieren

```bash
git clone https://github.com/nuazing/claude-skills.git /tmp/claude-skills && cp -R /tmp/claude-skills/skills/. ~/.claude/skills/
```

### Als Symlink (bleibt mit `git pull` aktuell)

```bash
git clone https://github.com/nuazing/claude-skills.git ~/Code/claude-skills && ln -s ~/Code/claude-skills/skills/md-to-pdf ~/.claude/skills/md-to-pdf
```

Danach in einer neuen Claude-Code-Session: der Skill wird automatisch erkannt. Mit `/skills` lässt sich prüfen, ob er geladen ist.

## Updates

```bash
cd ~/Code/claude-skills && git pull
```

Bei Symlink-Installation war's das. Bei Kopier-Installation danach nochmal den `cp`-Befehl von oben ausführen.

## Voraussetzungen

`md-to-pdf` braucht macOS mit Homebrew — das mitgelieferte `setup_env.sh` legt beim ersten Lauf automatisch ein venv mit `weasyprint` + `markdown` an und installiert bei Bedarf `pango`/`cairo`/`glib`. Danach ist es ein No-op.

## Lizenz

[MIT](LICENSE)
