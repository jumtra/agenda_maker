import dash
from urllib.parse import quote as urlquote
from dash import html, dcc, callback, Input, Output
from agenda_generator.dash_server.asset import style
import dash_uploader as du
import uuid
from pathlib import Path
from agenda_generator.main import main
import pandas as pd
import zipfile
import io
import time

# from agenda_generator.dash_server.app import get_a_list

dash.register_page(__name__)

TEMP_DIR = "data"

app = dash.get_app()


def get_upload_component(id, uid):
    return du.Upload(
        id=id,
        filetypes=["wav", "mp3", "mp4"],
        max_file_size=1800,
        upload_id=uid,
        max_files=1,
    )


def get_app_layout():
    global uid
    global is_Fin
    global start_time
    start_time = None
    is_Fin = False
    uid = uuid.uuid1()
    return html.Div(
        [
            html.H2(f"Step1: データを入力してください"),
            html.Div(
                [
                    get_upload_component(id="dash-uploader", uid=uid),
                    html.Div(id="callback-output"),
                ],
                style={  # wrapper div style
                    "textAlign": "center",
                    "width": "600px",
                    "padding": "10px",
                    "display": "inline-block",
                },
            ),
            html.Br(),
            html.Br(),
            html.H2(f"Step2: 「議事メモ生成」を押してください"),
            html.Br(),
            html.Div(
                id="outputs",
                style={
                    "textAlign": "center",
                    "fontSize": 30,
                    "color": "white",
                },
            ),
            html.Div(
                html.Button(id="run-button", n_clicks=None, children="議事メモ生成"),
                style={  # wrapper div style
                    "textAlign": "center",
                    "width": "600px",
                    "padding": "10px",
                    "display": "inline-block",
                },
            ),
            dcc.Interval(
                id="interval-component",
                interval=1 * 1000,  # in milliseconds
                n_intervals=0,
            ),
            html.Div(id="elapsed-time"),
            html.H2(f"Step3: 「Download Agenda memo」を押して結果をダウンロードしてください"),
            html.Button("Download Agenda memo", id="btn_csv"),
            dcc.Download(id="download-dataframe-csv"),
            html.Br(),
            html.Br(),
            html.Br(),
            html.H5("結果を全てダウンロードする場合は以下のボタンを押してください"),
            html.Button("Download result.zip", id="btn_txt"),
            dcc.Download(id="download-text"),
        ],
        style={
            "textAlign": "center",
        },
    )


du.configure_upload(app, f"{TEMP_DIR}", use_upload_id=True)


@du.callback(
    output=Output("callback-output", "children"),
    id="dash-uploader",
)
def get_a_list(filenames):
    # path_parent = Path(filenames[0]).parent
    return html.Ul([filenames[0].split("/")[-1] + "を受け取りました。"])


@callback(
    Output(component_id="outputs", component_property="children"),
    Input(component_id="run-button", component_property="n_clicks"),
)
def run_model(n_clicks):
    global is_Fin
    path_root = TEMP_DIR + "/" + str(uid)
    config_path = "config/config_base.yaml"
    if Path(path_root).exists() and n_clicks is not None:
        input_name = list(Path(path_root).iterdir())[0].parts[-1]
        print(input_name)
        main(
            path_root=path_root,
            config_path=config_path,
            input_name=input_name,
        )
        is_Fin = True
        return "結果が出力されました"
    else:
        is_Fin = False
        return ""


@app.callback(
    dash.dependencies.Output("elapsed-time", "children"),
    [
        dash.dependencies.Input("interval-component", "n_intervals"),
        Input(component_id="run-button", component_property="n_clicks"),
    ],
)
def update_output(n, n_clicks):
    global start_time
    global is_Fin
    path_root = TEMP_DIR + "/" + str(uid)
    if (
        Path(path_root).exists()
        and n_clicks is not None
        and start_time is None
        and is_Fin == False
    ):
        # Start the timer
        start_time = time.time()
        return "【議事メモ生成中】経過時間: 0 秒"
    elif Path(path_root).exists() and n_clicks is not None and is_Fin == False:
        elapsed_time = time.time() - start_time
        return f"【議事メモ生成中】経過時間: {elapsed_time:.2f} 秒"
    else:
        return ""


@callback(
    Output("download-dataframe-csv", "data"),
    Input("btn_csv", "n_clicks"),
    prevent_initial_call=True,
)
def func(n_clicks):

    global is_Fin
    if is_Fin:
        path_root = TEMP_DIR + "/" + str(uid)
        df = pd.read_table(path_root + "/Agenda_memo.txt", encoding="utf-8")
        return dcc.send_data_frame(df.to_csv, "Agenda_memo.txt")
    else:
        return "議事メモを生成してください"


@callback(
    Output("download-text", "data"),
    Input("btn_txt", "n_clicks"),
    prevent_initial_call=True,
)
def save_zip(n_clicks):
    # CSVファイルを生成する

    path_root = TEMP_DIR + "/" + str(uid)
    list_csv = list(Path(path_root).glob("**/*.csv"))
    list_txt = list(Path(path_root).glob("**/*.txt"))

    def write_archive(bites_io):
        # Zipファイルを生成する
        with zipfile.ZipFile(bites_io, "w") as zf:
            for path in list_csv:
                with open(path, mode="r", encoding="utf-8") as f:
                    df = pd.read_csv(f)
                csv_buffer = io.StringIO()
                df.to_csv(csv_buffer, index=False, encoding="utf-8")
                # csv_buffer.write(df.to_string())
                zf.writestr(
                    str(path.parts[-1]).split(".")[-2] + ".txt",
                    csv_buffer.getvalue(),
                    compress_type=zipfile.ZIP_DEFLATED,
                )
            for path in list_txt:
                df = pd.read_table(
                    path,
                    encoding="utf-8",
                )
                txt_buffer = io.StringIO()
                # txt_buffer.write(df.to_string())
                df.to_csv(txt_buffer, index=False, encoding="utf-8")
                zf.writestr(
                    str(path.parts[-1]),
                    txt_buffer.getvalue(),
                    compress_type=zipfile.ZIP_DEFLATED,
                )

    if is_Fin:
        return dcc.send_bytes(write_archive, "result.zip")

    else:
        return "議事メモを生成してください"


# This way we can use unique session id's as upload_id's
layout = get_app_layout
