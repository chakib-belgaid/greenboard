# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import itertools
import json
import math
from collections import OrderedDict
import os
import dash
import dash_bootstrap_components as dbc
import matplotlib as mpl
import pandas as pd
import plotly.express as px
import plotly.io as pio
from dash import ALL, MATCH, Dash, Input, Output, State, dcc, html
from dash.dash_table import DataTable, FormatTemplate
from dash.dash_table.Format import Format, Scheme, Symbol, Trim
from dash_extensions.enrich import DashProxy, MultiplexerTransform
import shutil

from columns import *
from labels import *
from styles import *


pio.kaleido.scope.mathjax = None
pio.kaleido.scope.default_format = "pdf"


# TODO : change style


app = DashProxy(
    __name__,
    transforms=[MultiplexerTransform()],
    external_stylesheets=[dbc.themes.BOOTSTRAP],
)

### plotly configs

##BLOCK constants

DURATION = 20
PAGE_SIZE = 20

columns = columns_name + columns_performance + create_energy_columns()

##BLOCK data gathering
def load_data(filename="recap_frameworkbenchmark.csv"):
    data = pd.read_csv(filename)
    data["av_power_cpu"] = data["cpu"].apply(lambda x: x / DURATION / 2)
    data["av_power_dram"] = data["dram"].apply(lambda x: x / DURATION / 2)
    data["av_cpu_per_request"] = data["cpu"] / data["totalRequests"]
    data["av_dram_per_request"] = data["dram"] / data["totalRequests"]
    data["scenario"] = data.apply(
        lambda row: "idle" if row["level"] == 0 else row["scenario"], axis=1
    )
    data["RPS"] = data["totalRequests"] / DURATION

    return data


def clean_data(data):
    df = data.loc[data["status"] == "sucess"]
    return df


def calculate_effeciency(dt):
    """calculate the ratio of the
    "latencyAvg",
    "totalRequests",
    "rps",
    "latency99"
     "dram",
    "av_power_dram",
    "av_dram_per_request",]
    "cpu",
    "av_power_cpu",
    "av_cpu_per_request",
    on the max  while grouped by
    name and scenario"""


##BLOCK plotting


def line_plot(data1, scenario="db", metric="av_power_cpu", subcategory="language"):
    displaynames = dict(zip(data1["name"], data1["display_name"]))

    labels = Y_labels | {"name": "Frameworks", "level": X_labels[scenario]}
    fig = px.line(
        data1,
        x="level",
        y=metric,
        color="name",
        symbol=subcategory,
        hover_name="display_name",
        labels=labels,
        template="plotly_white",
        color_discrete_map=custom_palette,
    )
    fig.for_each_trace(lambda t: t.update(name=displaynames[t.name.split(",")[0]]))
    fig.update_layout(legend_title_text="Frameworks")
    return fig


def idle_power_plot(dt, scope="cpu", colors=None):
    displaynames = dict(zip(dt["name"], dt["display_name"]))
    data1 = dt[dt["scenario"] == "idle"].groupby("name").mean().reset_index()
    labels = Y_labels | {"name": "Frameworks"}
    fig = px.bar(
        data1,
        y="name",
        x=f"av_power_{scope}",
        color="name",
        labels=labels,
        template="plotly_white",
        orientation="h",
        color_discrete_map=custom_palette,
    )
    fig.update_yaxes(
        tickmode="array",
        tickvals=(vals := dt["name"].unique()),
        ticktext=[displaynames[x] for x in vals],
    )
    fig.update_layout(showlegend=False)
    return fig


##BLOCK initialisation

df = load_data()
df = clean_data(df)
custom_palette = dict(zip(df["name"].unique(), px.colors.qualitative.Plotly))
##BLOCK layout
graphs_requests = dcc.Graph(
    config=plot_config,  # id={"role": "plot", "scenario": "requests", "index": 0}
)
graphs_latency = dcc.Graph(
    config=plot_config,  # id={"role": "plot", "scenario": "requests", "index": 1}
)
graphs_energy_request = dcc.Graph(
    config=plot_config,  # id={"role": "plot", "scenario": "energy_request", "index": 2}
)
graphs_av_power = dcc.Graph(
    config=plot_config,  # id={"role": "plot", "scenario": "av_power", "index": 3}
)
graphs_idle_power = dcc.Graph(
    config=plot_config,  # id={"role": "plot", "scenario": "idle_power", "index": 4}
)

languages = [{"label": lang, "value": lang} for lang in df["language"].unique()]
languagesDIV = html.Div(
    [
        # using bootstrap make this list of checkboxes fit with the rest of the page
        languages_list := dbc.Checklist(
            options=languages,
            class_name=" btn-group flex-wrap  ",
            input_class_name="btn-check ",
            label_class_name="btn  btn-outline-primary check-labels col-12",
            # label_checked_class_name="active",
            value=["php"],
            label_style={"min-width": "120px", "margin-bottom": "5px"}
            # inline=True,
        ),
    ],
    className=" languages-category  d-flex flex-wrap  ",
)


categoriesDIV = html.Div(
    [
        dbc.Card(
            [
                dbc.CardHeader(cat),
                dbc.CardBody(
                    dcc.Dropdown(
                        options=df[cat].unique(),
                        id={
                            "index": f"id_categorie_{cat}",
                            "scenario": "category_filter",
                        },
                        className="category_filter",
                        placeholder=f"all",
                        multi=True,
                    ),
                ),
            ],
            className="category-card",
        )
        for cat in categories
    ],
    className="row p-2 bg-dark m-0 rounded-3 ",
)

scenariosDIV = html.Div(
    [
        scenarios := dcc.Dropdown(
            options=[
                {"label": "Single query", "value": "db"},
                {"label": "Multiple queries", "value": "query"},
                {"label": "Update queries", "value": "update"},
                {"label": "Fortunes", "value": "fortune"},
                {"label": "JSON Serialization", "value": "json"},
                {"label": "Plain text", "value": "plaintext"},
            ],
            value="db",
            clearable=False,
        ),
    ]
)


filtersDIV = html.Div(
    [
        scenariosDIV,
        dbc.Accordion(
            [
                dbc.AccordionItem(
                    [languagesDIV],
                    title="Languages",
                ),
                dbc.AccordionItem(
                    [categoriesDIV],
                    title="Additional filters",
                ),
            ],
            start_collapsed=True,
        ),
    ],
    className="vstack gap-1 filters",
)
infoTalbeDiv = html.Div(
    [
        infoSecondTable := html.Div(),
        selectedRowsStore := dcc.Store("selectedRows"),
    ],
    className="row",
)


rawTableDIV = html.Div(
    [
        html.H1("raw data"),
        html.Span(
            rawTable := DataTable(
                ## selection
                # row_selectable="multi",
                # selected_rows=[],
                sort_action="native",
                sort_mode="single",
                sort_by=[],
                page_action="native",
                page_size=PAGE_SIZE,
                page_current=0,
                style_table={
                    "fontFamily": '-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,"Noto Sans",sans-serif,"Apple Color Emoji","Segoe UI Emoji","Segoe UI Symbol","Noto Color Emoji"'
                },
                style_header=style_header,
                style_cell=style_cell,
                # style_data_conditional=styles
                # fixed_columns={"headers": True, "data": 2},
            ),
            className="table table-striped col-12",
        ),
    ],
    className="row",
)
# DownloadBtn := html.Button("Download"),
downloadDiv = html.Div(
    [
        html.Div(
            dbc.InputGroup(
                [
                    DownloadBtn := dbc.Button("Download"),
                    testsuitname := dbc.Input(
                        placeholder="testsuit", class_name="col-xs-3"
                    ),
                    dbc.InputGroupText(".pdf"),
                ],
                className="",
            ),
            className="col-8 ",
        ),
        downloader := dcc.Download(),
    ]
)


scopesDiv = html.Div(
    [
        html.P(
            "Device Scope",
            className="col-4  text-center  ",
        ),
        html.Div(
            [
                cached_categories := dcc.Store(id="cached_categories"),
                energy_scope := dbc.RadioItems(
                    className="btn-group",
                    inputClassName="btn-check",
                    labelClassName="btn btn-outline-primary m-0",
                    labelCheckedClassName="active",
                    options=[
                        {"label": "CPU", "value": "cpu"},
                        {"label": "DRAM", "value": "dram"},
                    ],
                    value="cpu",
                    switch=True,
                ),
            ],
            className="col-8  hstack radio-group p-3 rounded-3 ",
        ),
    ],
    className="row hstack mt-2",
)

levelsDiv = html.Div(
    [
        scenarioLevels := dcc.Dropdown(
            options=[],
            className="",
            placeholder=f"all",
            multi=True,
        ),
    ]
)
controlsDIV = html.Div(
    [downloadDiv, scopesDiv, levelsDiv],
    className="col-4",
)


energyPlotsDIV = html.Div(
    children=[
        html.P("Energy consumption per Request", className="graph-title"),
        graphs_energy_request,
        html.P("Average Power Consumptions", className="graph-title"),
        graphs_av_power,
    ],
    className="col-6",
)
performancePlotsDIV = html.Div(
    children=[
        html.P("total requests", className="graph-title"),
        graphs_requests,
        html.P("tail Latency", className="graph-title"),
        graphs_latency,
    ],
    className="col-6",
)

idlePlotDiv = html.Div(
    children=[
        html.P("Idle Power Consumption", className="graph-title"),
        graphs_idle_power,
    ],
    className="col-8",
)


graphsDIV = html.Div(
    [
        html.Div(
            children=[
                controlsDIV,
                idlePlotDiv,
            ],
            className=" hstack",
        ),
        html.Div(
            [
                performancePlotsDIV,
                energyPlotsDIV,
            ],
            className=" hstack",
        ),
    ],
    className="vstack",
)

##BLOCK mainLayout
app.layout = html.Div(
    [
        html.Div(id="placeholder"),
        html.H1("Filters"),
        filtersDIV,
        infoTalbeDiv,
        # downloadDiv,
        scenarioTitle := html.H2(),
        graphsDIV,
        # idlePlotDiv,
        rawTableDIV,
    ],
    className="container vstack gap-2",
)


##BLOCK callbacks


@app.callback(
    Output(scenarioTitle, "children"),
    Input(scenarios, "value"),
)
def update_title(scenario):
    return TITLES[scenario]


@app.callback(
    Input(
        {"scenario": "category_filter", "index": ALL},
        "value",
    ),
    State(cached_categories, "data"),
    Output(cached_categories, "data"),
)
def update_filters_cache(selected_categories, previuous_categories):

    try:
        l = {
            id["index"].replace("id_categorie_", ""): var["value"]
            for var in dash.callback_context.triggered
            if "scenario" in (id := json.loads(var["prop_id"].split(".")[0])).keys()
            and id["scenario"] == "category_filter"
        }
    except json.JSONDecodeError:
        # print("failed ")
        l = {}

    if previuous_categories == None:
        previuous_categories = {}
    else:
        for cat, vals in l.items():
            name = cat.replace("id_categorie_", "")
            previuous_categories[name] = vals
    return previuous_categories


def make_selectable(table):
    """add slection behaviour to the rows
    replace the id column with checkboxes"""

    table.children[0].children[0].children.pop(0)
    # head.children[0] = html.Th(children="", colSpan=1)
    # head.children = [h] + head.children
    for row in table.children[1].children:
        id = row.children.pop(0).children
        row.id = {"scenario": "row_selectable", "index": id}


@app.callback(
    Input(infoSecondTable, "children"),
    Input({"scenario": "row_selectable", "index": ALL}, "n_clicks"),
    State({"scenario": "row_selectable", "index": ALL}, "id"),
    Output(selectedRowsStore, "data"),
    Output({"scenario": "row_selectable", "index": ALL}, "style"),
    prevent_initial_call=True,
)
def select_rows(secondTable, checked, rows):

    row_ids = [row["index"] for row in rows]
    data = {
        row_ids[i]: checked[i] is not None and checked[i] % 2 == 1
        for i in range(len(checked))
    }
    styles = [
        {"backgroundColor": "#21b6a8A7"}
        if check is not None and check % 2 == 1
        else None
        for check in checked
    ]

    return data, styles


@app.callback(
    State(energy_scope, "value"),
    Input(scenarios, "value"),
    Input(languages_list, "value"),
    Input(cached_categories, "data"),
    Output(infoSecondTable, "children"),
)
def select_scope(scope, selected_scenario, selected_langauges, selected_categories):

    data = df.loc[df["language"].isin(selected_langauges)]
    data = data.loc[
        data["scenario"] == selected_scenario,
        [
            "name",
            "display_name",
            "language",
        ]
        + categories,
    ]

    for cat, vals in selected_categories.items():
        if len(vals) > 0:
            data = data.loc[data[cat].isin(vals)]

    data = data.drop_duplicates().rename(columns={"name": "id"})
    # secondData = None
    # data2 = data[["id", "display_name"] + categories]

    secondData = dbc.Table.from_dataframe(
        data,
        striped=True,
        bordered=True,
        hover=True,
        id="inputDataTable",
    )
    make_selectable(secondData)
    return secondData


@app.callback(
    Input(scenarios, "value"),
    Output(scenarioLevels, "options"),
)
def update_scenarioLevels(scenario):
    return list(df.loc[df["scenario"] == scenario]["level"].unique())


@app.callback(
    Output(rawTable, "columns"),
    Output(rawTable, "data"),
    Output(rawTable, "style_data_conditional"),
    Output(graphs_requests, "figure"),
    Output(graphs_latency, "figure"),
    Output(graphs_energy_request, "figure"),
    Output(graphs_av_power, "figure"),
    Output(graphs_idle_power, "figure"),
    # Input(infoTable, "selected_row_ids"),
    Input(selectedRowsStore, "data"),
    Input(energy_scope, "value"),
    State(scenarios, "value"),
    Input(scenarioLevels, "value"),
    prevent_initial_call=True,
)
def update_graphs(
    selected_rows,
    scope,
    selected_scenario,
    selected_levels,
):

    columns = (
        basecolumns + cpu_metrics if scope == "cpu" else basecolumns + dram_metrics
    )
    metrics = [
        "RPS",
        "latencyAvg",
        f"av_{scope}_per_request",
        f"av_power_{scope}",
    ]

    if selected_rows is None or len(selected_rows) == 0:
        return dash.no_update

    rows = [row for row, checked in selected_rows.items() if checked]
    if len(rows) > 0:
        data = df.loc[df["name"].isin(rows)]
    else:
        data = df.loc[df["name"].isin(selected_rows.keys())]

    data1 = data.loc[
        data["scenario"] == selected_scenario,
        [
            "name",
            "level",
            "display_name",
        ]
        + columns,
    ].fillna(0)

    if selected_levels:
        data1 = data1.loc[data1["level"].isin(selected_levels)]

    figs = [
        line_plot(
            data1,
            selected_scenario,
            metric,
        )
        for metric in metrics
    ]
    figs.append(
        idle_power_plot(
            data,
            scope,
        )
    )

    res = data1.to_dict(
        "records",
    )
    styles = databar_heatmap(data1, column=f"av_power_{scope}")
    styles += databar_heatmap(
        data1,
        column=f"av_{scope}_per_request",
    )
    # styles += data_bars(data1, "latency99")
    styles += data_bars(data1, "totalRequests")
    columns_name = [
        dict(
            id="name",
            name="name",
        ),
        dict(
            id="language",
            name="Langauge",
        ),
        dict(
            id="level",
            name=X_labels[selected_scenario],
            type="text",
            presentation="dropdown",
        ),
    ]
    return (
        columns_name + columns_performance + create_energy_columns(scope),
        res,
        styles,
        *figs,
    )


import plotly.graph_objects as go


@app.callback(
    Input(DownloadBtn, "n_clicks"),
    State(testsuitname, "value"),
    State(energy_scope, "value"),
    State(graphs_requests, "figure"),
    State(graphs_latency, "figure"),
    State(graphs_energy_request, "figure"),
    State(graphs_av_power, "figure"),
    State(graphs_idle_power, "figure"),
    Output(downloader, "data"),
    prevent_initial_call=True,
)
def Download(btn, suitnames, scope, *graphs):
    # TODO : ADD other formats png svg ..etc
    # TODO : add radar plot for comparaison
    metrics = [
        "RPS",
        "latencyAvg",
        f"av_{scope}_per_request",
        f"av_power_{scope}",
    ]
    try:
        os.mkdir(f"{suitnames}")
    except FileExistsError:
        pass
    figs = [go.Figure(g) for g in graphs]
    for fig, metric in zip(figs[:-1], metrics):
        fig.write_image(f"{suitnames}/line_plot_{metric}.pdf")
    figs[-1].write_image(f"{suitnames}/idle_power.pdf")
    # download the directory as zip file and delete it
    shutil.make_archive(suitnames, "zip", suitnames)
    shutil.rmtree(suitnames)
    files = dcc.send_file(f"{suitnames}.zip")
    os.remove(path=f"{suitnames}.zip")
    return files


if __name__ == "__main__":
    app.run_server(debug=True)
