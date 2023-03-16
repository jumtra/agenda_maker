import dash_uploader as du
from pathlib import Path
import os
import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output
from flask import Flask, send_from_directory
from dash import Dash, html, dcc, DiskcacheManager, CeleryManager
import dash
import os
import diskcache
from celery import Celery
import dash_auth
from agenda_generator.dash_server.pages import *
import warnings
import shutil

warnings.simplefilter("ignore")

TEMP_DIR = "data"
if "REDIS_URL" in os.environ:
    # Use Redis & Celery if REDIS_URL set as an env variable
    celery_app = Celery(
        __name__, broker=os.environ["REDIS_URL"], backend=os.environ["REDIS_URL"]
    )
    background_callback_manager = CeleryManager(celery_app)
else:
    # Diskcache for non-production apps when developing locally
    cache = diskcache.Cache("./cache")
    background_callback_manager = DiskcacheManager(cache)
# Normally, Dash creates its own Flask server internally. By creating our own,
# we can create a route for downloading files directly:


server = Flask(__name__)

app = Dash(
    __name__,
    server=server,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
    use_pages=True,
    background_callback_manager=background_callback_manager,
    external_stylesheets=[
        # dbc.themes.GRID,
        dbc.themes.BOOTSTRAP,
        "https://cdn.jsdelivr.net/npm/bootstrap-dark-5@1.1.3/dist/css/bootstrap-night.min.css",
    ],
)


dash_auth.BasicAuth(app, {"agenda_ai": "$5rUfe!fi89#"})


# page list
list_page = html.Div(
    [
        html.Div(
            [
                html.H3(
                    dcc.Link(
                        f"{page['name']}",
                        href=page["relative_path"],
                    )
                )
                for page in dash.page_registry.values()
            ]
        ),
        html.Hr(),
    ]
)


def layout():
    return dbc.Container(
        [
            dbc.Row(
                [
                    html.Hr(),
                    html.H1(app.title),
                    html.Hr(),
                ],
                style={"height": "20vh"},
            ),
            dbc.Row(
                [
                    dbc.Col(
                        list_page,
                        width=3,
                    ),
                    dbc.Col(dash.page_container, width=9),
                ],
                style={"height": "80vh"},
            ),
        ],
        fluid=True,
    )


app.title = "議事メモ作成AI ver.0.0.1(試用バージョン)"
app.layout = layout

if __name__ == "__main__":
    try:
        app.run_server(
            debug=True, dev_tools_hot_reload=False, port=8888, host="0.0.0.0"
        )
    finally:
        shutil.rmtree("data")
        Path("data").mkdir()
