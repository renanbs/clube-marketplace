# GitHub Release with Bilingual Changelog

Publishing the tag to GitHub with release notes, following the repository's bilingual
convention (all notable docs ship EN + pt-BR).

## Tag

Annotated tag at the release merge commit:

```bash
cd /home/renan/src/clube-marketplace
git tag -a vX.Y.Z -m "Clube Marketplace vX.Y.Z"
git push origin vX.Y.Z
```

Verify the remote tag:

```bash
git ls-remote --tags origin | grep vX.Y.Z
```

## Create the GitHub Release

```bash
gh release create vX.Y.Z --generate-notes
```

- First release on the repo: notes are generated from the tag's commits. If `--generate-notes`
  produces too-synthetic output, supply the notes manually with `--notes-file` (see template).

## Bilingual notes template

```markdown
## Changelog
<!-- EN section -->
### Added / Changed / Fixed
- ...

## Registro de alterações
<!-- pt-BR section -->
### Adicionado / Alterado / Corrigido
- ...
```

The notes should mirror the `[X.Y.Z] - <date>` section of `CHANGELOG.md` (EN) and
`CHANGELOG.pt-BR.md` (pt-BR), with the release marked as **Latest** (default).

## Optional follow-ups

- `gh release view vX.Y.Z` to confirm the body and tag.
- `gh release edit vX.Y.Z --prerelease` if a pre-release is desired (rare here).
- Cleanup helpers after the release: delete the merged release branch and sync dev
  checkouts (see [release-procedure.md](release-procedure.md#8-cleanup)).
