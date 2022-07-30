#!/bin/zsh

# upgrade pip
python -m pip install --upgrade pip

# install poetry
curl -sSL https://install.python-poetry.org | python3 -

# zsh completions for poetry (may not actually work)
mkdir -p ~/.zfunc && poetry completions zsh > ~/.zfunc/_poetry
echo -e \"fpath+=~/.zfunc\nautoload -Uz compinit && compinit\" >> ~/.zshrc

# set virtualenv inside the project (at .venv)
# this allows vscode to use the venv for finding libs
poetry config virtualenvs.in-project true

# install deps
poetry install

# setup pre-commit hook
poetry run pre-commit install
