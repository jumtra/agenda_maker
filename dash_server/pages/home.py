import dash
from dash import html

dash.register_page(__name__, path="/")

layout = html.Div(
    children=[
        html.H1(children="Read me 工事中"),
        # html.H1(children="議事メモ作成AI使用方法"),
        # html.H2(children="Step1 データのアップロード"),
        # html.H2(children="Step2 データのアップロード"),
        # html.H2(children="Step3 データのアップロード"),
        html.Div(
            children="""
        This is our Home page content.
    """
        ),
    ]
)
