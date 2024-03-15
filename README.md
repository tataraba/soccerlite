# soccerlite

Hi! This repo is the backbone of a web app I am building for my local amateur soccer league. It is built using the [Litestar web framework](https://litestar.dev), and utilizes the [PyHAT](https://github.com/PyHAT-stack/awesome-python-htmx) stack. What this means is that the frontend is mostly handled by HTML and [htmx](https://htmx.org)*, and styling is included using [TailwindCSS](https://tailwindcss.com). Keep in mind that this site is being built specifically for the _Inland Empire Soccer League_, but you might be able to adapt it to your own purposes with some tweaks.

>**Note** Under the hood:
> Minimal JavaScript is used for date selection, using Alpine JS and the flatpickr library.

## Getting Started

Feel free to clone the repo. I use PDM as my package manager. Once you navigate to the project folder, you may be able to set metadata by using the `pdm init` command. This will also create your `.venv` virtual environment. You can then use the `pdm install` command to install the necessary dependencies.

However, I also have included a `requirements.txt` file in case you are not using PDM. If that is the case, after cloning the project, create a virtual environment first, then activate it:

```sh
# Windows
python -m venv .venv
.\.venv\Scripts\activate 
```

I will try to keep the requirement file updated, but you'll likely want to take a look at the dependencies in the `pyproject.toml` file to be sure.

You can either copy/replace contents of existing `requirements.txt` file, or you can try to install directly without doing that.

```sh
python -m pip install -r requirements.txt
```

Once your dependencies are installed, you should be able to run the website like so:

```sh
python -m litestar run --reload --debug
```
(Using the `--reload` and `--debug` flags are optional, but I find them useful while developing.)

That should send you over to http://127.0.0.1:8000 with a working copy of the site.

Even better, if you have `just` installed, you can _just_ type:

```sh
just run
```

That is the equivalent of activating your environment and running the command above.

>**Note** Under the hood:
>
> `just` is a command-runner, composed of "recipes" that correspond to specific CLI commands. For example, the `just run` command is the equivalent of running your Litestar application directly from the interpreter located in your virtual environment. If you are in your project root directory, it saves you from having to remember to activate your virtual environment and typing the entire command above.
>
> You can review the commands that are initiated by looking at the `justfile` in your project directory.
>
>Check out the [documentation](https://just.systems/man/en/).

### Database Migrations

The database will be empty until it is initialized using `alembic`.

You will generally need to use these commands when you are starting up the database for the first time, or when you've made changes to the database models.

```sh
# Create a revision with your own custom message
alembic revision --autogenerate -m "your message here"
# This actually generates/updates the tables
alembic upgrade head
```

Or... if you have `just` installed, you can type:

```sh
just makemigrations MESSAGE
```
That is the equivalent of the two commands above, where `MESSAGE` is the equivalent of `"your message here"` in the above example.

If you just want to run the second command `alembic upgrade head`, then you can use:

```sh
just migrate
```

(Borrowing heavily from a Django namespace here, even if the functionality differs in some form or another. (Sorry, not _as familiar_ with Django commands.))

### Tailwind Stuff

If you are making changes to the CSS, make sure to initialize the tailwind watcher. What's that? It watches for changes in your HTML files and re-compiles the CSS file that's included in the project.

The command to setup the watcher needs to include the location of the directives file, as well as the output directory where the css file is built (your static directory). Does that make any sense? No? Good thing all you need to do is type this command in another terminal window (make sure you've [installed](https://just.systems/man/en/chapter_3.html) `just` into your system):

```sh
just tw_watch
```

Now you can make changes to the Tailwind classes in your HTML, and this will update your `main.css`.

If you want to run the command manually, take a peek at the `justfile` and run the tailwind commands in your shell.
