from dash.dash_table.Format import Format, Symbol, Scheme

columns_name = [
    dict(
        id="name",
        name="name",
    ),
    dict(
        id="language",
        name="Lnangauge",
    ),
    dict(
        id="level",
        name="Number of clients",
        type="text",
        presentation="dropdown",
    ),
]
columns_categories = [
    # dict(id="name", name="name", type="text", presentation="dropdown"),
    dict(id="display_name", name="display_name", type="text", presentation="dropdown"),
    dict(
        id="classification", name="classification", type="text", presentation="dropdown"
    ),
    dict(id="database", name="database", type="text", presentation="dropdown"),
    dict(id="language", name="language", type="text", presentation="dropdown"),
    dict(id="os", name="os", type="text", presentation="dropdown"),
    dict(id="framework", name="framework", type="text", presentation="dropdown"),
    dict(id="webserver", name="webserver", type="text", presentation="dropdown"),
    dict(id="orm", name="orm", type="text", presentation="dropdown"),
    dict(id="platform", name="platform", type="text", presentation="dropdown"),
    dict(id="approach", name="approach", type="text", presentation="dropdown"),
]
columns_performance = [
    # dict(
    #     id="latencyAvg",
    #     name="Average Latency",
    #     type="numeric",
    #     format=Format(
    #         precision=2,
    #         symbol=Symbol.yes,
    #         symbol_suffix="ms",
    #     ),
    # ),
    dict(
        id="latencyAvg",
        name="Average Latency",
        type="numeric",
        format=Format(
            precision=2,
            symbol=Symbol.yes,
            symbol_suffix="ms",
        ),
    ),
    dict(
        id="totalRequests",
        name="Total Requests",
        type="numeric",
        format=Format(precision=2, scheme=Scheme.decimal_si_prefix),
    ),
    # dict(
    #     id="rps",
    #     name="Average Requests per Second",
    #     type="numeric",
    #     format=Format(
    #         precision=2,
    #         scheme=Scheme.decimal_integer,
    #     ),
    # ),
]


def create_energy_columns(energy_domain="cpu"):
    columns_energy = [
        #     dict(
        #         id=f"{energy_domain}",
        #         name="Total Energy (Joules)",
        #         type="numeric",
        #         format=Format(
        #             precision=3,
        #             scheme=Scheme.decimal_si_prefix,
        #             symbol=Symbol.yes,
        #             symbol_suffix="j",
        #         ),
        #     ),
        dict(
            id=f"av_power_{energy_domain}",
            name="Average Power (W)",
            type="numeric",
            format=Format(
                precision=3,
                scheme=Scheme.decimal_si_prefix,
                symbol=Symbol.yes,
                symbol_suffix="W",
            ),
        ),
        # TODO : fixed  column width
        dict(
            id=f"av_{energy_domain}_per_request",
            name="Average energy consumption per request (Joules)",
            type="numeric",
            format=Format(
                precision=3,
                scheme=Scheme.decimal_si_prefix,
                symbol=Symbol.yes,
                symbol_suffix="j",
            ),
        ),
    ]
    return columns_energy
