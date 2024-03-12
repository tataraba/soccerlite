# Set shell for Windows OSs (PowerShell Core):
set windows-shell := ["powershell.exe", "-NoLogo", "-c"]
set dotenv-load := false

bool_prefix := if os_family() == "windows" { "$" } else { "" }
python_dir := if os_family() == "windows" { ".venv/Scripts" } else { ".venv/bin" }
python := python_dir + if os_family() == "windows" { "/python.exe" } else { "/python" }
venv_exists := bool_prefix + path_exists(".venv")
venv_activate := python_dir + if os_family() == "windows" { "/activate.bat" } else { "/activate" }
debug := "--port 8000 --debug --reload"

# The `python_dir` directive is the equivalent of running commands from your virtual environment after activating the environment. 
# In other words, you don't have to worry about `activating` your virtual environment when using `just` commands.

@_default:
    just --list

@run:
    {{ python_dir }}/litestar run {{ debug }}

@tw_watch:
    {{ python_dir }}/tailwindcss -i ./app/static/tailwind/input.css -o ./app/static/css/main.css --watch

@make_migration message:
    {{ python_dir }}/alembic revision --autogenerate -m "{{ message }}"
    {{ python_dir }}/alembic upgrade head

@migrate:
    {{ python_dir }}/alembic upgrade head

@reqs:
    pdm export -o requirements.txt