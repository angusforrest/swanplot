from pydantic import BaseModel, ConfigDict
from annotated_types import Union, Gt, Ge, Lt, Le, Len, MinLen
from typing import Annotated, Sequence, Literal
import json
import numpy as np
import base64
from swanplot.cname import cname, pname, pythontocss
from PIL import Image
import io


class Model(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_default=True)


class Histogram(Model):
    timestep: Annotated[int, Ge(0)]
    bins: list[Sequence[int | float]]


class ColorScheme(Model):
    colors: Annotated[Sequence[cname], MinLen(2)] = ["black", "white"]
    positions: Annotated[Sequence[Annotated[float, Ge(0), Le(1)]], Len(len(colors))] = [
        0,
        1,
    ]


class AxisBounds(Model):
    start: float = 0
    end: float = 1
    length: float = 1


class Fig(Model):
    compact: bool = False
    time_unit: str = ""
    x_unit: str = ""
    y_unit: str = ""
    t_axis: Sequence[float] | AxisBounds | None = None
    x_axis: AxisBounds | None = None
    y_axis: AxisBounds | None = None
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


ColorStrings = Annotated[Sequence[cname | pname], MinLen(2)]
IntensityValues = Annotated[Sequence[Annotated[float, Ge(0), Le(1)]], MinLen(2)]

GraphTypes = Literal["frame", "histogram"]

DataAxes = Union[Literal["x", "y", "t"], Literal[0, 1, 2]]


class axes:
    """
    A class to represent axes for plotting data.

    Attributes:
        color_scheme (ColorScheme | cname): The color scheme for the axes.
        type (Literal["frame", "histogram"] | None): The type of data being plotted.
        data (list[Frame] | list[Histogram] | str | None): The data to be plotted.
        options (fig): Configuration options for the figure.
    """

    def __init__(self):
        self.color_scheme: ColorScheme = ColorScheme()
        self.type: GraphTypes | None = None
        self.data: str | None = None
        self.options: Fig = Fig()

    def cmap(
        self,
        colors: ColorStrings = ["black", "white"],
        positions: IntensityValues = [
            0,
            1,
        ],
    ):
        """
        Set the color map for the axes.

        :param colors: The colors to use in the color scheme.

        :param positions: The positions corresponding to the colors.
        """
        output = list()
        for color in colors:
            if color in pname:
                output.append(pythontocss[color])
            else:
                output.append(color)
        self.color_scheme = ColorScheme(colors=colors, positions=positions)
        return

    def _plot(
        self,
        a: np.ndarray,
    ):
        """
        Plot the data as frames.

        :param a: A 2D NumPy array where each column represents a point in
                  the format [timestep, x, y].
        """
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
        """
        Create a histogram from the data.

        :param a: A 3D NumPy array representing the image data.
        :param compact: If True, saves the histogram in a compact format.
        :param temp_tiff: If True, saves a temporary TIFF file.
        """
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

    def set_unit(self, unit: str = "", axis: DataAxes = "x"):
        """
        Set the unit for the x-axis.

        :param unit: The unit to set for the x-axis.
        """
        match axis:
            case "t" | 0:
                self.options.t_unit = unit
            case "x" | 1:
                self.options.x_unit = unit
            case "y" | 2:
                self.options.y_unit = unit

    def uniform_ticks(
        self,
        start: float,
        end: float,
        axis: DataAxes = "x",
    ):
        """
        Set the bounds for the x-axis.

        :param start: The start value for the x-axis.
        :param end: The end value for the x-axis.
        """
        if self.options.timesteps == None:
            raise Exception(
                f"Data has not been loaded and therefore ticks number cannot be verified"
            )
        input = np.linspace(start, end, self.options.timesteps).tolist()
        match axis:
            case "t" | 0:
                self.option.t_axis = input
            case "x" | 1:
                self.options.x_axis = input
            case "y" | 2:
                self.options.y_axis = input

    def custom_ticks(self, input: Sequence[float], axis: DataAxes = "x"):
        if self.options.timesteps == None:
            raise Exception(
                f"Data has not been loaded and therefore ticks number cannot be verified"
            )
        if len(input) != self.options.timesteps:
            raise Exception(
                f"The length of provided ticks is not the same as the number of timesteps in your data {self.options.timesteps}"
            )
        match axis:
            case "t" | 0:
                self.option.t_axis = input
            case "x" | 1:
                self.options.x_axis = input
            case "y" | 2:
                self.options.y_axis = input

    def uniform_t_ticks(self, start: float, end: float):
        """
        Set the bounds for the time axis.

        :param start: The start value for the time axis.
        :param end: The end value for the time axis.
        """
        self.options.t_axis = np.linspace(start, end, self.options.timesteps)

    def set_xlabel(self, string: str):
        """
        Set the label for the x-axis.

        :param string: The label to set for the x-axis.
        """
        self.options.x_label = string

    def set_ylabel(self, string: str):
        """
        Set the label for the y-axis.

        :param string: The label to set for the y-axis.
        """
        self.options.y_label = string

    def set_loop(self, loop: bool = True):
        """
        Set whether the plot should loop.

        :param loop: If True, the plot will loop.
        """
        self.options.loop = loop

    def savefig(
        self,
        fname: str,
        style: Literal["pretty", "compact"] = "pretty",
        format: Literal["json"] = "json",
        print_website: bool = True,
    ):
        """
        Save the figure to a file.

        :param fname: The filename to save the figure to.
        :param style: The style of the output (pretty or compact).
        :param format: The format to save the figure in (currently only json).
        :param print_website: If True, prints a message with the upload link.
        """
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
