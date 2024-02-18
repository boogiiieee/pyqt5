# PyQt5

## Install

```bash
git clone https://dnomads.gitlab.yandexcloud.net/backend/evolution.git
python version 3.12
pipx install poetry
poetry install
```
## Run
```bash
# Create .env file
cp example.env .env

# Makefile command
make run
```

## Ruff
```bash
# Linter
make lint

# Formatting 
make format

# Fixing 
make fix
```

## Memray: memory profiler
```bash
# Create .env file
make memray

# Makefile command
make report
```
