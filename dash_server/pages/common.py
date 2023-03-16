import pathlib
from dash import dcc
import dash
import plotly.express as px
import warnings
import dash_bootstrap_components as dbc
from dash import html
from dash import Output

number_regex = r"(?:\d+(?:\.\d+)?)"
depth_range_regex = rf"\[({number_regex}),\W?({number_regex})\]"
common_shape_for_bb_regex = (
    rf"\[({number_regex}|None),\W?({number_regex}|None),\W?({number_regex}|None)\]"
)


def get_dcc_graph(id_suffix):
    return dcc.Graph(
        id=f"my-graph-{id_suffix}",
        style={"height": "80vh"},
        figure=px.scatter(template="plotly_dark"),
    )


def query_to_dict(query):
    return dict(
        tuple(element.split("=")) for element in query.split("#") if element != ""
    )


def dict_to_query(query_dict: dict):
    return "".join([f"#{k}={v}" for k, v in query_dict.items()])


class Progress:
    def __init__(self, set_progress, total):
        self.set_progress = set_progress
        self.total = total - 1
        self.cnt = 0

    def step(self, *args):
        if self.cnt > self.total:
            raise StopIteration
        self.set_progress((self.cnt / self.total * 100, *args))
        self.cnt += 1

    def tqdm(self, iterator, *step_args):
        iterator = iter(iterator)
        for step in iterator:
            self.step(*step_args)
            yield step


def get_elements_of_status_bar(suffix):
    return [
        dbc.Progress(
            id=f"my-progress-bar-{suffix}",
            value=0,
            striped=True,
            animated=True,
            style={"visibility": "hidden"},
        ),
        html.Div(
            id=f"my-progressing-status-{suffix}",
            children="",
            style={"visibility": "hidden"},
        ),
    ]


def get_kwargs_to_callback_for_progress_bar(suffix):
    return dict(
        progress=[
            Output(f"my-progress-bar-{suffix}", "value"),
            Output(f"my-progressing-status-{suffix}", "children"),
        ],
        running=[
            (
                Output(f"my-progress-bar-{suffix}", "style"),
                {"visibility": "visible"},
                {"visibility": "hidden"},
            ),
            (
                Output(f"my-progressing-status-{suffix}", "style"),
                {"visibility": "visible"},
                {"visibility": "hidden"},
            ),
        ],
        background=True,
    )


def validate_layout_kwargs(given_kwargs: dict, default_query_kwargs: dict):
    unexpected_kwargs = set(given_kwargs.keys()) - set(default_query_kwargs.keys())
    if len(unexpected_kwargs) > 0:
        for key in unexpected_kwargs:
            warnings.warn(
                f"{key} not expected (value: {given_kwargs.pop(key)})", UserWarning
            )

    for key, default_value in default_query_kwargs.items():
        if key in given_kwargs.keys():
            given_value = given_kwargs[key]
            if key == "depth" and given_value == "original":
                value_to_replace = "0"
            elif key == "height" and given_value == "original":
                value_to_replace = "0"
            elif key == "width" and given_value == "original":
                value_to_replace = "0"
            else:
                value_to_replace = given_value
            given_kwargs[key] = value_to_replace
        else:
            given_kwargs[key] = default_value

        # if key == "uid":
        #    given_kwargs[key] = parse_uid_query(given_kwargs[key])
    return given_kwargs


class NotSelected:
    def __str__(self):
        return "NotSelected"

    def __repr__(self):
        return self.__str__()


not_selected = NotSelected()
