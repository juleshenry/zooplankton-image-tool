# AGENTS.md

Notes for AI agents and contributors working on this repo.

## Development

```bash
poetry install
poetry run pytest
```

Source lives in `src/zit/`, tests in `tests/`.

## CI and releases

- `.github/workflows/ci-cd.yml` runs tests only (Python 3.11–3.13) on pushes and PRs to `main`.
- `.github/workflows/publish.yml` is the **only** workflow that publishes to PyPI. It runs on `v*` tag pushes: tests first, then build and publish.
- PyPI trusted publishing (OIDC) is registered for **`publish.yml`** with environment **`pypi`** on `juleshenry/zooplankton-image-tool`. Do not rename that workflow, move the publish job elsewhere, or change the environment name without updating the publisher on PyPI too, or publishing will be rejected.
- To release: `python publish.py <version>` bumps the version in `pyproject.toml` and `src/zit/__init__.py`, updates `CHANGELOG.md`, commits, tags `v<version>`, and pushes. The tag triggers `publish.yml`.

## README images

PyPI renders `README.md` without the repo files, so relative image paths (`assets/foo.png`) break there. Always use absolute raw GitHub URLs:

```
https://raw.githubusercontent.com/juleshenry/zooplankton-image-tool/main/assets/<file>
```

New images must be committed and pushed to `main` before they show up. The PyPI page only picks up README changes on the next release.

## Commits

Use Conventional Commits prefixes: `feat(scope): ...`, `chore(scope): ...`, `bugfix(scope): ...`.
