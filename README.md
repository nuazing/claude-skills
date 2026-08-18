# claude-skills

Eine kleine Sammlung von [Claude Code](https://claude.com/claude-code) Skills, die ich im Alltag nutze — und die vielleicht auch für andere nützlich sind.

Ein Skill ist ein Ordner mit einer `SKILL.md` (Anleitung für Claude) plus optionalen Skripten. Claude lädt ihn automatisch, sobald die Beschreibung zur Aufgabe passt — man muss ihn nicht per Namen aufrufen.

## Skills

| Skill | Was es macht |
| --- | --- |
| [`md-to-pdf`](skills/md-to-pdf) | Wandelt eine Markdown-Datei in ein sauberes, druckfertiges PDF um — Tabellenzeilen brechen nie über Seitenumbrüche, jede Seite bekommt eine „N / total"-Fusszeile, optionale Akzentfarbe. Läuft über ein gebündeltes Python-Skript statt über eine jedes Mal neu erfundene HTML/CSS-Pipeline. |

## Installation

### Als Plugin (empfohlen)

Das Repo ist gleichzeitig ein Plugin-Marketplace. In Claude Code:

```
/plugin marketplace add nuazing/claude-skills
```

```
/plugin install nuazing-skills@nuazing
```

Damit sind alle Skills der Sammlung auf einmal installiert — und neue kommen bei einem Update automatisch dazu.

### Manuell kopieren

Wer lieber nur einen einzelnen Skill will: Skills liegen in `~/.claude/skills/` (persönlich, projektübergreifend) oder in `.claude/skills/` innerhalb eines Projekts.

```bash
git clone https://github.com/nuazing/claude-skills.git /tmp/claude-skills && cp -R /tmp/claude-skills/skills/md-to-pdf ~/.claude/skills/
```

Alle Skills auf einmal:

```bash
git clone https://github.com/nuazing/claude-skills.git /tmp/claude-skills && cp -R /tmp/claude-skills/skills/. ~/.claude/skills/
```

Danach in einer neuen Claude-Code-Session: der Skill wird automatisch erkannt.

## Updates

Als Plugin:

```
/plugin update nuazing-skills
```

Bei manueller Installation: `git pull` im Klon, danach den `cp`-Befehl von oben nochmal ausführen.

## Voraussetzungen

`md-to-pdf` braucht macOS mit Homebrew — das mitgelieferte `setup_env.sh` legt beim ersten Lauf automatisch ein venv mit `weasyprint` + `markdown` an und installiert bei Bedarf `pango`/`cairo`/`glib`. Danach ist es ein No-op.

## Aufbau des Repos

```
.claude-plugin/
  marketplace.json   Marketplace-Manifest (macht das Repo per /plugin marketplace add nutzbar)
  plugin.json        Plugin-Manifest — bündelt alle Skills unter skills/
skills/
  md-to-pdf/         ein Ordner pro Skill, jeweils mit SKILL.md
```

Ein neuer Skill = ein neuer Ordner unter `skills/` plus eine Zeile in der Tabelle oben. Die Manifeste müssen dafür nicht angefasst werden; nur die `version` in `plugin.json` sollte man hochzählen.

## Lizenz

[MIT](LICENSE)
