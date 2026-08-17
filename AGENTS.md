# AGENTS.md — agent routing index

Agents: explore the repo directly; this file is a routing index, not a
contributor guide.

## Workflow

**For non-trivial planning**, inspect deps and tooling:
`tox.ini` · `.pre-commit-config.yaml` ·
`requirements.txt` · `test-requirements.txt`

**Tests**: Use `tox` or `stestr`; never use `pytest`.

**Routing:**
- Style, hacking, checks: [HACKING.rst](HACKING.rst)
- Unit test conventions: [HACKING.rst](HACKING.rst) (Unit Tests section)
- Functional test conventions: [HACKING.rst](HACKING.rst) (Functional Tests section)
- Contributing: [CONTRIBUTING.rst](CONTRIBUTING.rst)

## Guardrails

- **Tools:** Do not install missing tools with a package manager or `pip`.
- **Review**: openstacksdk uses Gerrit, not GitHub PRs. Do not create
  pull requests.
- **Commits**: Use the `Assisted-By:` trailer for AI-assisted contributions
  per the [OpenInfra AI policy](https://openinfra.org/legal/ai-policy).
- **Git**: Read-only operations (`git log`, `git diff`, `git status`) are
  fine. Do not run mutating operations (`add`, `commit`, `reset`, `push`,
  etc.) unless explicitly instructed.
