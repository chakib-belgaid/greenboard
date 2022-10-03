import itertools

import matplotlib as mpl

plot_config = {
    "toImageButtonOptions": {
        "format": "svg",  # one of png, svg, jpeg, webp
        "filename": "plot",
        "height": 500,
        "width": 700,
        "scale": 1,  # Multiply title/legend/axis/canvas sizes by this factor
    },
    "modeBarButtonsToAdd": [
        "drawline",
        "drawopenpath",
        "drawclosedpath",
        "drawcircle",
        "drawrect",
        "eraseshape",
    ],
    "displaylogo": False,
}

style_header = {
    "backgroundColor": "white",
    "fontWeight": "bold",
    "padding": "0.75rem",
}
style_cell = {
    "fontFamily": '-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,"Noto Sans",sans-serif,"Apple Color Emoji","Segoe UI Emoji","Segoe UI Symbol","Noto Color Emoji"',
    "fontWeight": "400",
    "lineHeight": "1.5",
    "color": "#212529",
    "textAlign": "left",
    "whiteSpace": "normal",
    "height": "auto",
    "padding": "0.75rem",
    "border": "1px solid #dee2e6",
    "verticalAlign": "top",
}


default_colors = [
    "#1f77b4",  # muted blue
    "#ff7f0e",  # safety orange
    "#2ca02c",  # cooked asparagus green
    "#d62728",  # brick red
    "#9467bd",  # muted purple
    "#8c564b",  # chestnut brown
    "#e377c2",  # raspberry yogurt pink
    "#7f7f7f",  # middle gray
    "#bcbd22",  # curry yellow-green
    "#17becf",  # blue-teal
]


default_colors = itertools.cycle(default_colors)


def choose_frontcolor(background):
    """
    choose between black or white based on background color

    param: matplotlib.color
    """
    red, green, blue, *_ = background
    return (
        "#000000" if (red * 0.299 + green * 0.587 + blue * 0.114) > 0.60 else "#ffffff"
    )


def databar_heatmap(df, column="av_power_cpu", colormap="RdYlGn_r", log_scale=False):

    backgroundcolors = mpl.cm.get_cmap(colormap)
    values = df[column]

    if log_scale:
        values = [math.log(x) if x > 0 else x for x in values]
    data_values = dict(zip(values, df[column]))

    df_max = max(values)
    df_min = min(values)
    styles = []
    legend = []
    for value in values:
        ratio = (
            (value - df_min) / (df_max - df_min)
            if df_max - df_min > 0
            else (value - df_min)
        )
        background = backgroundcolors(ratio)
        frontcolor = choose_frontcolor(background)
        styles.append(
            {
                "if": {
                    "filter_query": "{{{}}} = {}".format(column, data_values[value]),
                    "column_id": column,
                },
                "backgroundColor": mpl.colors.to_hex(background),
                "color": frontcolor,
            }
        )
    return styles


def data_bars(df, column):
    n_bins = 100
    bounds = [i * (1.0 / n_bins) for i in range(n_bins + 1)]
    ranges = [
        ((df[column].max() - df[column].min()) * i) + df[column].min() for i in bounds
    ]
    styles = []
    for i in range(1, len(bounds)):
        min_bound = ranges[i - 1]
        max_bound = ranges[i]
        max_bound_percentage = bounds[i] * 100
        styles.append(
            {
                "if": {
                    "filter_query": (
                        "{{{column}}} >= {min_bound}"
                        + (
                            " && {{{column}}} < {max_bound}"
                            if (i < len(bounds) - 1)
                            else ""
                        )
                    ).format(column=column, min_bound=min_bound, max_bound=max_bound),
                    "column_id": column,
                },
                "background": (
                    """
                    linear-gradient(90deg,
                    #0074D9 0%,
                    #0074D9 {max_bound_percentage}%,
                    white {max_bound_percentage}%,
                    white 100%)
                """.format(
                        max_bound_percentage=max_bound_percentage
                    )
                ),
                "paddingBottom": 2,
                "paddingTop": 2,
            }
        )

    return styles


def data_bars_diverging(df, column, color_above="#3D9970", color_below="#FF4136"):
    n_bins = 100
    bounds = [i * (1.0 / n_bins) for i in range(n_bins + 1)]
    col_max = df[column].max()
    col_min = df[column].min()
    ranges = [((col_max - col_min) * i) + col_min for i in bounds]
    midpoint = (col_max + col_min) / 2.0

    styles = []
    for i in range(1, len(bounds)):
        min_bound = ranges[i - 1]
        max_bound = ranges[i]
        min_bound_percentage = bounds[i - 1] * 100
        max_bound_percentage = bounds[i] * 100

        style = {
            "if": {
                "filter_query": (
                    "{{{column}}} >= {min_bound}"
                    + (
                        " && {{{column}}} < {max_bound}"
                        if (i < len(bounds) - 1)
                        else ""
                    )
                ).format(column=column, min_bound=min_bound, max_bound=max_bound),
                "column_id": column,
            },
            "paddingBottom": 2,
            "paddingTop": 2,
        }
        if max_bound > midpoint:
            background = """
                    linear-gradient(90deg,
                    white 0%,
                    white 50%,
                    {color_above} 50%,
                    {color_above} {max_bound_percentage}%,
                    white {max_bound_percentage}%,
                    white 100%)
                """.format(
                max_bound_percentage=max_bound_percentage, color_above=color_above
            )
        else:
            background = """
                    linear-gradient(90deg,
                    white 0%,
                    white {min_bound_percentage}%,
                    {color_below} {min_bound_percentage}%,
                    {color_below} 50%,
                    white 50%,
                    white 100%)
                """.format(
                min_bound_percentage=min_bound_percentage, color_below=color_below
            )
        style["background"] = background
        styles.append(style)

    return styles
