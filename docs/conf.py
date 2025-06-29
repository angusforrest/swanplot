import importlib.metadata

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.mathjax",
    "sphinx.ext.napoleon",
    "sphinx_autodoc_typehints",
    "sphinx.ext.autosummary",
    "myst_nb",
]
# "sphinxcontrib.autodoc_pydantic",
# "autodocsumm",
# "IPython.sphinxext.ipython_console_highlighting",
source_suffix = [".rst", ".md"]
master_doc = "index"
autodoc_pydantic_model_show_json = True
autodoc_pydantic_settings_show_json = False

# General information about the project.
project = "swanplot"
copyright = "2025 Angus Forrest and Otautahi-Oxford Group"

version = importlib.metadata.version("swanplot")
release = importlib.metadata.version("swanplot")

templates_path = ["_templates"]
exclude_patterns = ["_build", "_templates"]
html_theme = "pydata_sphinx_theme"
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
    "use_edit_page_button": False,
    "use_issues_button": True,
    "use_repository_button": True,
    "use_download_button": True,
}
html_baseurl = "https://swanplot.readthedocs.io/en/latest/"
nb_execution_mode = "force"
html_sourcelink_suffix = ""
autoclass_content = "class"
napoleon_use_param = True
napoleon_preprocess_types = True
always_use_bars_union = True
autodoc_typehints_format = "short"
python_use_unqualified_type_names = True
python_display_short_literal_types = True
autodoc_typehints = "none"
autosummary_generate = True
autodoc_default_options = {
    "autosummary": True,
    "members": True,
    "member-order": "bysource",
    "undoc-members": True,
    "exclude-members": "__weakref__",
    "private-members": False,
}
autodoc_type_aliases = dict(
    ColorStrings="ColorStrings",
    IntensityValues="IntensityValues",
    GraphTypes="GraphTypes",
    DataAxes="DataAxes",
    StringInput="StringInput",
    AxesInput="AxesInput",
)
