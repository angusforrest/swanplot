# Swanplot

Python plotting tool for datacubes

Utilises numpy, pillow, and pydantic

to use the package pip install and import swanplot and then upload to the (animate web endpoint)["https://animate.deno.dev"].
The data will be rendered client side (no scrapping of data) inside your browser.

```python
import swanplot as splt


ax = splt.axes()

ax.hist(data)

ax.savefig("animation.json")
  
```
