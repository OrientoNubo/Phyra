# Phyra -- Installation Guide

---

## Method 1: Script Install (Recommended)

```bash
git clone https://github.com/[username]/phyra.git
cd phyra
chmod +x scripts/install.sh
./scripts/install.sh
```

The install script performs the following:

1. Copies `.claude/skills/phyra-*` to `~/.claude/skills/`
2. Copies `.claude/agents/phyra-*` to `~/.claude/agents/`
3. Copies `.claude/commands/phyra-*` to `~/.claude/commands/`
4. Copies `.phyra/examples/` to `~/.phyra/examples/`
5. Prompts whether to automatically add the Agent Teams configuration to `~/.claude/settings.json`

---

## Method 2: Project-Level Install (No Global Pollution)

Use this method to install Phyra only within a specific project, without modifying your global Claude Code configuration.

```bash
cd your-project/
git clone https://github.com/[username]/phyra.git .phyra-plugin
cp -r .phyra-plugin/.claude/skills/phyra-* .claude/skills/
cp -r .phyra-plugin/.claude/agents/phyra-* .claude/agents/
cp -r .phyra-plugin/.claude/commands/phyra-* .claude/commands/
mkdir -p .phyra/examples
cp .phyra-plugin/.phyra/examples/* .phyra/examples/
```

This keeps all Phyra files within your project directory. Nothing is written to `~/.claude/`.

---

## Method 3: Plugin Marketplace (Future)

Once the Claude Code Plugin distribution mechanism is stable, Phyra plans to be available via the Plugin Marketplace:

```
/plugin install phyra
```

This is not yet available.

---

## Agent Teams Configuration

To use AT (Agent Teams) mode, add the following to `~/.claude/settings.json`:

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

The script install (Method 1) can configure this automatically when prompted.

---

## Update

```bash
cd phyra/
git pull
./scripts/install.sh --update
```

The `--update` flag overwrites existing Phyra files while leaving any user-defined non-Phyra files untouched.

---

## Uninstall

```bash
./scripts/uninstall.sh
```

The uninstall script removes all files with the `phyra-` prefix from skills, agents, and commands directories. User-defined files are not affected.

---

## Verification

After installation, verify that Phyra is available by running any command in Claude Code:

```
/phyra-paper-read --help
```

If the command is recognized, installation was successful.
