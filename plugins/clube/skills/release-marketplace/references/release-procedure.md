# Marketplace Release Procedure — step by step

The ceremony from pre-flight to GitHub Release, as one deterministic sequence. See
[SKILL.md](../SKILL.md) for the entrypoint checklist and the rules; this document is the
executable walkthrough.

## 0. Pre-flight

```bash
git -C /home/renan/src/clube-marketplace status                          # clean main
git -C /home/renan/src/clube-marketplace fetch origin
gh auth status                                                           # GitHub CLI ready
make -C /home/renan/src/clube-marketplace sync                           # if new dirs were added
```

Decide the target SemVer with the maintainer (bilingual docs, `make check` parity gates):
- New harness/feature support merged since last tag → **minor** (`X.Y.Z+1.0`).
- Pure fixes, no surface change → **patch**.
- Breaking manifest/catalog change → **major**.

## 1. Spin up the release worktree

Create a disposable branch + worktree from current `main`. Never commit on main directly:

```bash
WD=/tmp/opencode/clube-rel-XXXX                          # pick a fresh path
git -C /home/renan/src/clube-marketplace worktree add "$WD" -b chore/release-X.Y.Z main
```

## 2. Bump every versioned manifest

See [semver-manifests.md](semver-manifests.md) for the full map. In the worktree:

```bash
cd "$WD"
# generic sync (root package.json, marketplaces, plugin manifests, adapter pkgs, README/changelog badges)
sed -i 's/0\.4\.0/0.5.0/g' \
  package.json \
  .claude-plugin/marketplace.json .omp-plugin/marketplace.json \
  .cursor-plugin/marketplace.json .agents/plugins/marketplace.json \
  .opencode-plugin/marketplace.json \
  plugins/clube/.claude-plugin/plugin.json plugins/clube/.cursor-plugin/plugin.json \
  plugins/clube/.codex-plugin/plugin.json plugins/clube/.omp-plugin/plugin.json \
  plugins/clube/.opencode-plugin/plugin.json \
  .opencode/plugins/clube/package.json \
  README.md README.pt-BR.md
# adapter package-lock: bump ONLY the two top-level version fields (root + packages[""])
sed -i '3s/0\.4\.0/0.5.0/;9s/0\.4\.0/0.5.0/' .opencode/plugins/clube/package-lock.json
# vertical skills: sync the metadata.version frontmatter
sed -i 's/version: v0\.4\.0/version: v0.5.0/' \
  plugins/clube/skills/*/SKILL.md
# changelogs: close the Unreleased section into X.Y.Z (EN + pt-BR) — keep date bilingual-fixed
```

> **Dependency lock discipline:** `sed 's/0.4.0/0.5.0/g'` on a `package-lock.json` would
> also rewrite the `json-schema ^0.4.0` dependency — restore it or do the line-targeted
> `3s/...;9s/...` form above. `make check` does not gate the adapter locks, but parity
> hygiene does.

Then update the bilingual CHANGELOGs and add the synchronization bullet to the release
section (see [github-release.md](github-release.md) for the note format).

## 3. Gates

```bash
cd "$WD" && make check   # 0 problems — SemVer parity across all 11 manifests + OpenCode integration
cd "$WD" && make test    # all green
```

`make check` is the authoritative SemVer validator (see
[semver-manifests.md](semver-manifests.md#make-check-semantics)).

## 4. Commit, push, PR

```bash
cd "$WD"
git add -A && git commit -m "chore(release): X.Y.Z"
git push -u origin chore/release-X.Y.Z
gh pr create --base main --head chore/release-X.Y.Z \
  --title "chore(release): X.Y.Z" --body "Release **vX.Y.Z** — <one-line summary>. Bilingual changelog."
```

## 5. Merge (repo convention: merge commit)

```bash
gh pr merge <n> --merge            # merge commit, not squash — keeps the release commit intact
git -C /home/renan/src/clube-marketplace fetch origin
```

## 6. Tag

```bash
cd /home/renan/src/clube-marketplace
git pull --ff-only                 # main now has the merge commit
git tag -a vX.Y.Z -m "Clube Marketplace vX.Y.Z"
git push origin vX.Y.Z
```

## 7. GitHub Release (with changelog)

```bash
cd /home/renan/src/clube-marketplace
gh release create vX.Y.Z --generate-notes      # first time per version
```

See [github-release.md](github-release.md) for the full ceremony, the bilingual notes
template, and the optional `gh release edit` follow-ups.

## 8. Cleanup

- Delete the release branch remotely + locally (`git push origin --delete chore/release-X.Y.Z`).
- Remove the worktree: `git -C /home/renan/src/clube-marketplace worktree remove "$WD"`.
- Refresh the development checkout (`src`): it now points at the new merge commit.
- Keep the ORCA worktrees in sync: re-attach/detach the `mako`/`mako-pt-br` mirrors to the
  new `main` tip.
