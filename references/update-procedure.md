# Vesper Update Procedure

## Standard update (no conflicts)

```bash
cd ~/.hermes/skills/ocas-vesper
git fetch origin
# Check if new commits exist
git log HEAD..origin/main --oneline
# If yes:
git pull origin main
```

## When local modifications block pull

```bash
cd ~/.hermes/skills/ocas-vesper
git stash
# Move untracked files that conflict with remote
mv references/new-file-from-remote.md /tmp/
git pull origin main
git stash pop
# Resolve any merge conflicts in SKILL.md
# If conflict: choose the version that's a superset (usually local), 
# then git add SKILL.md && git commit
```

## After pulling — sync profile copy

Sessions load from the profile directory, NOT the git repo. Always sync:

```bash
cp ~/.hermes/skills/ocas-vesper/SKILL.md \
   ~/.hermes/profiles/indigo/skills/ocas-vesper/SKILL.md
# Sync any new/changed reference files
cp ~/.hermes/skills/ocas-vesper/references/*.md \
   ~/.hermes/profiles/indigo/skills/ocas-vesper/references/
# Sync any new/changed scripts
cp ~/.hermes/skills/ocas-vesper/scripts/* \
   ~/.hermes/profiles/indigo/skills/ocas-vesper/scripts/
```

## Verify

```bash
cd ~/.hermes/skills/ocas-vesper
grep "version:" SKILL.md
git log --oneline -3
```

## Dual-location gotcha

Skill files live in two places:
- **Git repo**: `~/.hermes/skills/ocas-vesper/` — updated by `git pull`
- **Profile**: `~/.hermes/profiles/indigo/skills/ocas-vesper/` — loaded by sessions

If you update the git repo but forget to sync the profile, the next session runs stale code. Always sync both.
