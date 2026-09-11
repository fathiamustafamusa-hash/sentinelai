# 🤝 Contributing to SentinelAI

First off, thank you for considering contributing! 🎉

## 📋 Code of Conduct

By participating, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

## 🐛 Reporting Bugs

Open an issue using the **Bug Report** template. Include:
- Clear description
- Steps to reproduce
- Expected vs actual behavior
- Environment (OS, Python, Docker versions)

## ✨ Suggesting Features

Open an issue using the **Feature Request** template. Describe:
- The problem it solves
- Proposed solution
- Alternatives considered

## 🛠️ Development Workflow

### 1. Fork and clone

```bash
git clone https://github.com/<your-username>/sentinelai.git
cd sentinelai
git remote add upstream https://github.com/fathiamustafamusa-hash/sentinelai.git
```

### 2. Create a branch

```bash
git checkout -b feat/short-description
```

### 3. Setup environment

```bash
cd src/backend
poetry install
cd ../..
cp .env.example .env
docker compose up -d postgres redis
```

### 4. Make your changes

- Follow **PEP 8** (enforced by ruff)
- Add **type hints** (checked by mypy)
- Add **tests** for new features
- Keep coverage ≥ 75%

### 5. Run all checks locally

```bash
cd src/backend
poetry run ruff check app
poetry run ruff format app
poetry run mypy app
poetry run pytest tests/ -v
poetry run bandit -r app -c pyproject.toml
```

### 6. Commit

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat(auth): add refresh token endpoint
fix(alerts): handle missing assigned_to field
docs(readme): update quick start
ci(security): add Trivy scanning
```

### 7. Push and open PR

- Target the `main` branch
- Fill out the PR template
- Reference related issues (Closes #123)

## ✅ Pull Request Checklist

- [ ] Code follows style guide (ruff clean)
- [ ] Types check (mypy clean)
- [ ] Tests added/updated
- [ ] Coverage maintained or improved
- [ ] Documentation updated
- [ ] Commit messages follow Conventional Commits
- [ ] CI passes (green ✅)

## 📜 License

By contributing, you agree your contributions will be licensed under the [MIT License](LICENSE).
