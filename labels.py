X_labels = {
    "db": "Number of clients",
    "json": "Number of clients",
    "fortune": "Number of clients",
    "plaintext": "Number of clients",
    "query": "size of the query",
    "update": "size of the query",
}

Y_labels = {
    "latencyAvg": "Latency (ms)",
    "totalRequests": "Number of requests",
    "rps": "RPS",
    "latency99": "Latency (ms)",
    "cpu": "Energy (J)",
    "av_power_cpu": "Power (W)",
    "av_cpu_per_request": "Energy (J)",
    "dram": "Energy (J)",
    "av_power_dram": "Power (W)",
    "av_dram_per_request": "Energy (J)",
}

testtypes = {
    "db": "concurrencyLevels",
    "fortune": "concurrencyLevels",
    "json": "concurrencyLevels",
    "update": "queryIntervals",
    "query": "queryIntervals",
    "plaintext": "pipelineConcurrencyLevels",
}
performance_metrics = [
    "latencyAvg",
    "totalRequests",
    "RPS",
]
cpu_metrics = ["cpu", "av_power_cpu", "av_cpu_per_request"]
dram_metrics = [
    "dram",
    "av_power_dram",
    "av_dram_per_request",
]


index = ["type", "name", "level"]

categories = [
    "classification",
    "database",
    # "language",
    "os",
    "framework",
    "webserver",
    "orm",
    "platform",
    "approach",
]

basecolumns = ["language"] + performance_metrics + categories
TITLES = {
    "db": f"Database-access responses per second for a single query request",
    "json": f"Database-access responses per second for a Json file serialization",
    "query": f"Database-access responses per second, with a query of multiple lines from 512 clients",
    "update": f"Database-access responses per second, with  updates of multiple lines from 512 clients",
    "plaintext": f'return the message "Hello, World" with high number of concurent clients',
    "fortune": f"rendering an html page containing unknown number of lines using multiple clients ",
}
