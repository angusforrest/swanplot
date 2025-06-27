from __future__ import annotations
from pydantic import BaseModel, ConfigDict
from annotated_types import Union, Gt, Ge, Lt, Le, Len, MinLen
from typing import Annotated, Sequence, Literal
import json
import numpy as np
import base64
import os.path
from swanplot.cname import cname, pname, pythontocss
from PIL import Image
import io


class Model(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_default=True)


class ColorScheme(Model):
    colors: Annotated[Sequence[cname], MinLen(2)] = ["black", "white"]
    positions: Annotated[Sequence[Annotated[float, Ge(0), Le(1)]], Len(len(colors))] = [
        0,
        1,
    ]


class Fig(Model):
    compact: bool = False
    time_unit: str = ""
    x_unit: str = ""
    y_unit: str = ""
    t_axis: Sequence[float] | None = None
    x_axis: Sequence[float] | None = None
    y_axis: Sequence[float] | None = None
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


ColorStrings = Annotated[Sequence[cname | pname], MinLen(2)]
IntensityValues = Annotated[Sequence[Annotated[float, Ge(0), Le(1)]], MinLen(2)]

GraphTypes = Literal["histogram"]

DataAxes = Union[Literal["x", "y", "t"], Literal[0, 1, 2]]


class axes:
    def __init__(self):
        """
        A class to represent axes for plotting data.

        Attributes:
            color_scheme: The color scheme for the axes.
            type: The type of data being plotted.
            data: The data to be plotted.
            options: Configuration options for the figure.
        """

        self.color_scheme: ColorScheme = ColorScheme()
        self.type: GraphTypes | None = None
        self.data: str | None = None
        self.options: Fig = Fig()

    def _plot(
        self,
        a: np.ndarray,
    ):
        """
        Plot the data as frames.

        :param a: A 2D NumPy array where each column represents a point in
                  the format [timestep, x, y].
        """
        # pts = dict()
        # frames = list()
        # for i in range(a.shape[1]):
        #     t = float(a[0, i])
        #     x = float(a[1, i])
        #     y = float(a[2, i])
        #     if t in pts.keys():
        #         pts.update({float(t): [*pts[t], Point(x=x, y=y)]})
        #     else:
        #         pts.update({float(t): Point(x=x, y=y)})
        # print(pts)
        # for t in pts.keys():
        #     frames.append(Frame(timestep=t, pts=pts[t]))
        # self.data = frames
        # self.type = "frame"
        # return

    def hist(
        self,
        datacube: np.ndarray,
    ):
        """
        Create a histogram from the data.

        :param datacube: A 3D NumPy array representing the image data.
        :param temp_tiff: If True, saves a temporary TIFF file.
        """
        ims = list()
        for t in range(datacube.shape[0]):
            ims.append(Image.fromarray((datacube[t, ...]).astype(np.uint8), mode="L"))
        output = io.BytesIO()
        ims[0].save(output, "tiff", save_all=True, append_images=ims[1:])
        self.data = base64.b64encode(output.getvalue()).decode("utf-8")
        extremes = np.array([i.getextrema() for i in ims])
        self.options.max_intensity = int(extremes.max())
        self.options.min_intensity = int(extremes.min())
        self.options.compact = True
        if self.options.t_axis == None:
            self.t_axis(start=0, end=datacube.shape[0] - 1)
        self.options.timesteps = datacube.shape[0]
        if self.options.x_axis == None:
            self.x_axis(start=0, end=datacube.shape[1])
        self.options.x_bins = datacube.shape[1]
        if self.options.y_axis == None:
            self.y_axis(start=0, end=datacube.shape[2])
        self.options.y_bins = datacube.shape[2]
        self.type = "histogram"
        return

    def set_unit(self, unit: str, axis: DataAxes):
        """
        Set the unit for the specified axis.

        This method updates the unit of measurement for the specified axis
        (time, x, or y) in the figure options.

        :param unit: The unit to set for the specified axis.
        :param axis: The axis for which to set the unit. Can be "t", "x", "y",
                     or their corresponding integer values (0, 1, 2).
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
        axis: DataAxes,
    ):
        """
        Set uniform ticks for the specified axis.

        This method generates evenly spaced ticks between the specified start
        and end values for the given axis.

        :param start: The start value for the axis.
        :param end: The end value for the axis.
        :param axis: The axis for which to set the ticks. Can be "t", "x", "y",
                     or their corresponding integer values (0, 1, 2).
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

    def custom_ticks(self, input: Sequence[float], axis: DataAxes):
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

    def set_label(self, string: str, axis: DataAxes):
        """
        Set the label for the specified axis.

        This method updates the label for the specified axis (time, x, or y)
        in the figure options.

        :param string: The label to set for the specified axis.
        :param axis: The axis for which to set the label. Can be "t", "x", "y",
                     or their corresponding integer values (0, 1, 2).
        """
        match axis:
            case "t" | 0:
                self.options.t_label = string
            case "x" | 1:
                self.options.x_label = string
            case "y" | 2:
                self.options.y_label = string

    def set_loop(self, loop: bool = True):
        """
        Set whether the plot should loop.

        :param loop: If True, the plot will loop.
        """
        self.options.loop = loop

    def cmap(
        self,
        colors: ColorStrings,
        positions: IntensityValues,
    ):
        """
        Set the color map for the axes.

        This method defines the color scheme for the plot by specifying the
        colors and their corresponding positions in the color map.

        :param colors: A sequence of colors to use in the color scheme.
                       Can include color names or CSS color values.
        :param positions: A sequence of float values representing the positions
                          corresponding to the colors, ranging from 0 to 1.
        """
        output = list()
        for color in colors:
            if color in pname:
                output.append(pythontocss[color])
            else:
                output.append(color)
        self.color_scheme = ColorScheme(colors=colors, positions=positions)
        return

    def savefig(
        self,
        fname: str,
        style: Literal["pretty", "compact"] = "compact",
        format: Literal["json", "tiff"] = "json",
        force: bool = False,
        print_website: bool = True,
    ):
        """
        Save the figure to a file.

        :param fname: The filename to save the figure to.
        :param style: The style of the output (pretty or compact).
        :param format: The format to save the figure in (currently only json).
        :param print_website: If True, prints a message with the upload link.
        """
        ext = os.path.splitext(fname)[1]
        if not force and ext != format and ext != "":
            raise Exception(
                f"you choose the format {format} but your file extension is {ext}"
            )
        match format:
            case "tiff":
                with open(fname, "wb") as file:
                    file.write(base64.b64decode(self.data))
            case "json":
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
