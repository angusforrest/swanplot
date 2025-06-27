import importlib.metadata

extensions = [
    "sphinx.ext.autodoc",
    "sphinxcontrib.autodoc_pydantic",
    "sphinx.ext.mathjax",
    "sphinx.ext.napoleon",
    "myst_nb",
    "IPython.sphinxext.ipython_console_highlighting",
]
source_suffix = [".rst", ".md"]
master_doc = "index"

# General information about the project.
project = "swanplot"
copyright = "2025 Angus Forrest and Otautahi-Oxford Group"

version = importlib.metadata.version("swanplot")
release = importlib.metadata.version("swanplot")

exclude_patterns = ["_build"]
html_theme = "sphinx_book_theme"
html_title = "swanplot"
html_static_path = ["_static"]
html_show_sourcelink = False
html_theme_options = {
    "path_to_docs": "docs",
    "repository_url": "https://github.com/angusforrest/swanplot",
    "repository_branch": "main",
    "launch_buttons": {
        "binderhub_url": "https://mybinder.org",
        "colab_url": "https://colab.research.google.com/",
        "notebook_interface": "jupyterlab",
    },
    "use_edit_page_button": True,
    "use_issues_button": True,
    "use_repository_button": True,
    "use_download_button": True,
}
html_baseurl = "https://swanplot.readthedocs.io/en/latest/"
nb_execution_mode = "force"
html_sourcelink_suffix = ""
autoclass_content = "both"
autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "undoc-members": True,
    "exclude-members": "__weakref__",
    "private-members": False,
}
