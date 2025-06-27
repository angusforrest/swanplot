from pydantic import BaseModel, ConfigDict
from annotated_types import Gt, Ge, Lt, Le, Len, MinLen
from typing import Annotated, Sequence, Literal
import json
import numpy as np
import base64
from swanplot.cname import cname
from PIL import Image
import io


class Model(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_default=True)


class Histogram(Model):
    timestep: Annotated[int, Ge(0)]
    bins: list[Sequence[int | float]]


class ColorScheme(Model):
    colors: Annotated[Sequence[cname], MinLen(2)] = ["black", "steelblue"]
    positions: Annotated[Sequence[Annotated[float, Ge(0), Le(1)]], Len(len(colors))] = [
        0,
        1,
    ]


class axisBounds(Model):
    start: float = 0
    end: float = 1
    length: float = 1


class fig(Model):
    compact: bool = False
    time_unit: str = ""
    x_unit: str = ""
    y_unit: str = ""
    t_axis: Sequence[float] | axisBounds | None = None
    x_axis: axisBounds | None = None
    y_axis: axisBounds | None = None
    x_bins: int | None = None
    y_bins: int | None = None
    max_points: int | None = None
    max_intensity: float | None = None
    min_intensity: float | None = None
    width: int = 600
    height: int = 600
    margin: int = 40
    timesteps: int = 1
    x_label: str = ""
    y_label: str = ""
    loop: bool = False


class Point(Model):
    x: float
    y: float


class Frame(Model):
    timestep: Annotated[int, Ge(0)]
    pts: list[Point]


class axes(Model):
    color_scheme: ColorScheme | cname = "steelblue"
    type: Literal["frame", "histogram"] | None = None
    data: list[Frame] | list[Histogram] | str | None = None
    options: fig = fig()

    def cmap(self, colors="steelblue", positions=[1]):
        self.color_scheme = ColorScheme(colors=colors, positions=positions)
        return

    def plot(
        self,
        a: np.ndarray,
    ):
        pts = dict()
        frames = list()
        for i in range(a.shape[1]):
            t = float(a[0, i])
            x = float(a[1, i])
            y = float(a[2, i])
            if t in pts.keys():
                pts.update({float(t): [*pts[t], Point(x=x, y=y)]})
            else:
                pts.update({float(t): Point(x=x, y=y)})
        print(pts)
        for t in pts.keys():
            frames.append(Frame(timestep=t, pts=pts[t]))
        self.data = frames
        self.type = "frame"
        return

    def hist(
        self,
        a: np.ndarray,
        compact: bool = True,
        temp_tiff: bool = False,
    ):
        if compact == True:
            ims = list()
            for t in range(a.shape[0]):
                ims.append(Image.fromarray((a[t, ...]).astype(np.uint8), mode="L"))
            output = io.BytesIO()
            ims[0].save(output, "tiff", save_all=True, append_images=ims[1:])
            if temp_tiff:
                with open("test.tiff", "wb") as file:
                    file.write(output.getvalue())
            self.data = base64.b64encode(output.getvalue()).decode("utf-8")
            extremes = np.array([i.getextrema() for i in ims])
            self.options.max_intensity = int(extremes.max())
            self.options.min_intensity = int(extremes.min())
            self.options.compact = compact
        else:
            hist = list()
            for t in range(a.shape[0]):
                bins = list()
                for i in range(a.shape[1]):
                    for j in range(a.shape[2]):
                        if a[t, i, j] != 0:
                            bins.append([i, j, a[t, i, j]])
                hist.append(Histogram(timestep=t, bins=bins))
            self.data = hist
            self.options.max_intensity = a.max()
            self.options.min_intensity = a.min()
        if self.options.t_axis == None:
            self.t_axis(start=0, end=a.shape[0] - 1)
        self.options.timesteps = a.shape[0]
        if self.options.x_axis == None:
            self.x_axis(start=0, end=a.shape[1])
        self.options.x_bins = a.shape[1]
        if self.options.y_axis == None:
            self.y_axis(start=0, end=a.shape[2])
        self.options.y_bins = a.shape[2]
        self.type = "histogram"
        return

    def x_unit(self, unit: str = ""):
        self.options.x_unit = unit

    def y_unit(self, unit: str = ""):
        self.options.y_unit = unit

    def t_unit(self, unit: str = ""):
        self.options.time_unit = unit

    def y_axis(self, start: float, end: float):
        self.options.y_axis = axisBounds(start=start, end=end, length=end - start)

    def x_axis(self, start: float, end: float):
        self.options.x_axis = axisBounds(start=start, end=end, length=end - start)

    def t_axis(self, start: float, end: float):
        self.options.t_axis = axisBounds(start=start, end=end, length=end - start)

    def set_xlabel(self, string: str):
        self.options.x_label = string

    def set_ylabel(self, string: str):
        self.options.y_label = string

    def set_loop(self, loop: bool = True):
        self.options.loop = loop

    def savefig(
        self,
        fname: str,
        style: Literal["pretty", "compact"] = "pretty",
        format: Literal["json"] = "json",
        print_website: bool = True,
    ):
        with open(fname, "w") as file:
            indentation: int
            match style:
                case "pretty":
                    indentation = 4
                case "compact":
                    indentation = 0
            output = json.dumps(self.model_dump(), indent=indentation)
            file.write(output)
            if print_website:
                print(f"upload {fname} to https://animate.deno.dev")
