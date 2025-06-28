from __future__ import annotations
from pydantic import BaseModel, ConfigDict
from annotated_types import Union, Gt, Ge, Lt, Le, Len, MinLen, MaxLen
from typing import Annotated, Sequence, Literal, TypeAlias
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
    t_unit: str = ""
    x_unit: str = ""
    y_unit: str = ""
    c_unit: str = ""
    t_axis: Sequence[float] | None = None
    x_axis: Sequence[float] | None = None
    y_axis: Sequence[float] | None = None
    max_intensity: float | None = None
    min_intensity: float | None = None
    x_bins: int | None = None
    y_bins: int | None = None
    max_points: int | None = None
    width: int | None = None
    height: int | None = None
    margin: int = 40
    timesteps: int = 1
    x_label: str = ""
    y_label: str = ""
    t_label: str = ""
    c_label: str = ""
    loop: bool = False


ColorStrings: TypeAlias = Annotated[Sequence[cname | pname], MinLen(2)]
"""type for cmap's input of color string sequence. Allows css color names and python single letter color names. Requires the sequence to be a minimum of two strings"""

IntensityValues: TypeAlias = Annotated[
    Sequence[Annotated[float, Ge(0), Le(1)]], MinLen(2)
]
"""type for cmap's input of positions float sequence. Allows floats in the closed interval between 0 and 1. Requires the sequence to be a minimum of two floats"""

GraphTypes: TypeAlias = Literal["histogram"]
"""type for graphical representation"""

DataAxes: TypeAlias = Union[Literal["t", "x", "y", "c"], Literal[0, 1, 2, 3]]
"""type for datacube axes, allows the use of t,x,y,c or 0,1,2,3"""

StringInput: TypeAlias = str | Annotated[Sequence[str], MaxLen(4)]
"""type for set_label's input string that allows a single string or a sequence of strings with a maximum length of 4"""

AxesInput: TypeAlias = DataAxes | Annotated[Sequence[DataAxes], MaxLen(4)]
"""type for set_label's input axis that allows for a single axis or a sequence of axes with a maximum length of 4"""


class axes(Model):
    """
    A class to represent axes for plotting data, including color schemes,
    data options, and methods for plotting and saving figures.
    """

    color_scheme: ColorScheme = ColorScheme()
    type: GraphTypes | None = None
    data: str | None = None
    options: Fig = Fig()

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
        Create a histogram from the provided 3D image data.

        This method generates a TIFF image from the data and updates the
        figure options with intensity and axis information.

        :param datacube: A 3D NumPy array representing the image data, where
                         the first dimension corresponds to timesteps.
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
            self.uniform_ticks(start=0, end=datacube.shape[0] - 1, axis="t")
        self.options.timesteps = datacube.shape[0]
        if self.options.x_axis == None:
            self.uniform_ticks(start=0, end=datacube.shape[1], axis="x")
        self.options.x_bins = datacube.shape[1]
        if self.options.y_axis == None:
            self.uniform_ticks(start=0, end=datacube.shape[2], axis="y")
        self.options.y_bins = datacube.shape[2]
        if self.options.width == None:
            self.options.width = (
                datacube.shape[1] + 2 * self.options.margin
                if datacube.shape[1] >= 256
                else 256 + 2 * self.options.margin
            )
        if self.options.height == None:
            self.options.height = (
                datacube.shape[2] + 2 * self.options.margin
                if datacube.shape[2] >= 256
                else 256 + 2 * self.options.margin
            )
        self.type = "histogram"
        return

    def figsize(
        self,
        width: Annotated[int, Ge(256)],
        height: Annotated[int, Ge(256)],
        margin: Annotated[int, Ge(40)] | None = None,
    ):
        """
        Set the figure's dimensions and margin.

        If no margin is provided, and width and height are already set,
        the provided width and height are assumed to be the total width
        and total height of the figure.

        :param width: Width of the figure in pixels.
        :param height: Height of the figure in pixels.
        :param margin: Margin around the figure in pixels (optional).
        """
        if margin == None:
            if self.options.width == None and self.options.height == None:
                self.options.width = width + 2 * self.options.margin
                self.options.height = height + 2 * self.options.margin
            else:
                if width <= 296 or height <= 296:
                    raise Exception(
                        f"Total width or height is not large enough,{width},{height}"
                    )
                self.options.width = width
                self.options.height = height
        else:
            self.options.width = width + 2 * margin
            self.options.height = height + 2 * margin

    def set_unit(self, unit: str, axis: DataAxes):
        """
        Set the unit for the specified axis.

        This method updates the unit of measurement for the specified axis
        (time, x, y, or c) in the figure options.

        :param unit: The unit to set for the specified axis.
        :param axis: The axis for which to set the unit. Can be "t", "x", "y",
                     "c" or their corresponding integer values (0, 1, 2, 3).
        """
        match axis:
            case "t" | 0:
                self.options.t_unit = unit
            case "x" | 1:
                self.options.x_unit = unit
            case "y" | 2:
                self.options.y_unit = unit
            case "c" | 3:
                self.options.y_unit = unit

    def uniform_ticks(
        self,
        start: float,
        end: float,
        axis: DataAxes,
    ):
        """
        Generate and set uniform ticks for the specified axis.

        This method creates evenly spaced ticks between the specified start
        and end values for the given axis.

        :param start: The start value for the axis.
        :param end: The end value for the axis.
        :param axis: The axis for which to set the ticks. Can be "t", "x", "y",
                     "c" or their corresponding integer values (0, 1, 2, 3).
        :raises Exception: If the number of timesteps is not defined.
                           Set uniform ticks for the specified axis.
        """
        if self.options.timesteps == None:
            raise Exception(
                f"Data has not been loaded and therefore ticks number cannot be verified"
            )
        input = np.linspace(start, end, self.options.timesteps).tolist()
        match axis:
            case "t" | 0:
                self.options.t_axis = input
            case "x" | 1:
                self.options.x_axis = input
            case "y" | 2:
                self.options.y_axis = input
            case "c" | 3:
                self.options.c_axis = input

    def custom_ticks(self, input: Sequence[float], axis: DataAxes):
        """
        Set custom ticks for the specified axis.

        This method allows the user to define specific tick values for the
        given axis, ensuring the number of ticks matches the number of
        timesteps in the data.

        :param input: A sequence of float values representing the custom ticks.
        :param axis: The axis for which to set the custom ticks. Can be "t",
                     "x","y","c" or their corresponding integer values (0, 1, 2, 3).
        :raises Exception: If the number of timesteps is not defined or if the
                          length of provided ticks does not match the number of timesteps.
        """
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
                self.options.t_axis = input
            case "x" | 1:
                self.options.x_axis = input
            case "y" | 2:
                self.options.y_axis = input
            case "c" | 3:
                self.options.c_axis = input

    def set_label(self, string: StringInput, axis: AxesInput):
        """
        Assign labels to the specified axis.

        This method updates the label for the specified axis (time, x, y, or c)
        in the figure options. It can handle both single strings and sequences
        of strings.

        :param string: The label(s) to set for the specified axis.
        :param axis: The axis for which to set the label. Can be "t", "x", "y",
                     "c" or their corresponding integer values (0, 1, 2, 3).
        :raises Exception: If the provided string and axis types do not match
                          or if their lengths are inconsistent.
        """
        if isinstance(string, Sequence) != isinstance(axis, Sequence):
            raise Exception("Provided a list and a single value for string and axis")
        if isinstance(string, Sequence) and isinstance(axis, Sequence):
            if len(string) != len(axis):
                raise Exception("Provided string and axis are not of the same length")
        input = [string] if isinstance(string, str) else string
        axes = [axis] if isinstance(axis, str) or isinstance(axis, int) else axis

        for a, b in zip(input, axes):
            match b:
                case "t" | 0:
                    self.options.t_label = a
                case "x" | 1:
                    self.options.x_label = a
                case "y" | 2:
                    self.options.y_label = a

    def set_loop(self, loop: bool = True):
        """
        Configure whether the plot should loop.

        This method sets the looping behavior of the plot, allowing it to
        repeat indefinitely if desired.

        :param loop: If True, the plot will loop; otherwise, it will not.
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
        format: Literal["json", "tiff"] | None = None,
        force: bool = False,
        print_website: bool = True,
    ):
        """
        Save the figure to a specified file.

        This method allows the user to save the figure in either JSON or TIFF
        format, with options for output style and file extension verification.

        :param fname: The filename to save the figure to.
        :param style: The style of the output (pretty or compact).
        :param format: The format to save the figure in (currently supports json and tiff) defaults to json if no extension is filename is bare.
        :param force: If True, allows saving with a different file extension than the specified format.
        :param print_website: If True, prints a message with the upload link after saving.
        :raises Exception: If the specified format does not match the file extension and force is False.
        """
        ext = os.path.splitext(fname)[1]
        if ext == "" and format == None:
            input = "json"
        if ext != "" and format == None:
            if ext[1:] not in ["json", "tiff"] and not force:
                raise Exception("extension provided is not a supported extension")
            elif force:
                input = "json"
            else:
                input = ext[1:]
        input = ext[1:] if format == None else format
        fname = fname + "." + str(format) if ext == "" else fname

        if not force and ext != "." + input and ext != "":
            raise Exception(
                f"you choose the format {format} but your file extension is {ext}"
            )
        match input:
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
