import importlib.metadata

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_autodoc_typehints",
    "autodocsumm",
    "myst_nb",
]
# "sphinxcontrib.autodoc_pydantic",
# "IPython.sphinxext.ipython_console_highlighting",
source_suffix = [".rst", ".md"]
master_doc = "index"

# General information about the project.
project = "swanplot"
copyright = "2025 Angus Forrest and Otautahi-Oxford Group"

version = importlib.metadata.version("swanplot")
release = importlib.metadata.version("swanplot")

# templates_path = ["_templates"]
exclude_patterns = ["_build", "_templates"]
html_theme = "pydata_sphinx_theme"
# html_theme = "sphinx_book_theme"
html_title = "swanplot"
html_static_path = ["_static"]
html_show_sourcelink = False
html_sidebars = {"**": []}
html_theme_options = {
    "use_edit_page_button": False,
    "navbar_start": ["navbar-logo"],
    "navbar_center": ["navbar-nav"],
    "navbar_end": ["navbar-icon-links"],
    "navbar_persistent": ["search-button"],
    "secondary_sidebar_items": [],
}
html_baseurl = "https://swanplot.readthedocs.io/en/latest/"
html_sourcelink_suffix = ""
autoclass_content = "class"
napoleon_use_param = True
napoleon_preprocess_types = True
always_use_bars_union = True
autodoc_typehints_format = "short"
python_use_unqualified_type_names = True
python_display_short_literal_types = True
autodoc_typehints = "none"
# autosummary_generate = True
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
