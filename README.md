# PyQt5

## Install

```bash
git clone https://github.com/boogiiieee/pyqt5.git
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
# Profiling
make memray

# Create report format html
make report FILE=<memray_name_file.bin>
```
