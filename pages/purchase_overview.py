# resused from Mayara Daher

import dash
from dash import callback, dcc, html, Input, Output
import dash_bootstrap_components as dbc
from utils.functions import create_card
import pandas as pd
import plotly.express as px
import warnings

warnings.filterwarnings("ignore")

dash.register_page(
    __name__,
    suppress_callback_exceptions=True,
    path="/"
)

# Load your CSV (edit filename if needed)
df = pd.read_csv("data/amazon-purchases.csv")

# Basic cleaning
df['Order Date'] = pd.to_datetime(df['Order Date'])
df['Year'] = df['Order Date'].dt.year
df['Month'] = df['Order Date'].dt.month_name().str[:3]
df['Spend'] = df['Purchase Price Per Unit'] * df['Quantity']

# Layout
layout = dbc.Container(
    [
        html.Div(
            [
                html.H2("Purchase Overview", className="title"),
                html.Br(),
                dbc.Row([
                    dbc.Col([
                        html.H5("Select Year", className="subtitle-small"),
                        dcc.Dropdown(
                            id="year-dropdown",
                            options=[{"label": "All Years", "value": "All"}] +
                                    [{"label": y, "value": y} for y in sorted(df['Year'].unique())],
                            value="All",
                            clearable=False,
                            className="custom-dropdown"
                        )
                    ], width=4),
                ]),
                html.Br(),
                dbc.Row([
                    dbc.Col(create_card("Purchases", "purchases-card", "fa-list"), width=4),
                    dbc.Col(create_card("Total Spend", "spend-card", "fa-coins"), width=4),
                    dbc.Col(create_card("Top Category", "category-card", "fa-tags"), width=4),
                ]),
                html.Br(),
                dbc.Row([
                    dbc.Col(dcc.Loading(
                        dcc.Graph(id="sales-chart", config={"displayModeBar": False}, style={"height": "400px"}),
                        type="circle", color="#f79500"
                    ), width=6),
                    dbc.Col(dcc.Loading(
                        dcc.Graph(id="category-chart", config={"displayModeBar": False}, style={"height": "400px"}),
                        type="circle", color="#f79500"
                    ), width=6),
                ]),
            ],
            className="page-content",
        )
    ],
    fluid=True,
)

# Callbacks
@callback(
    [
        Output("purchases-card", "children"),
        Output("spend-card", "children"),
        Output("category-card", "children"),
        Output("sales-chart", "figure"),
        Output("category-chart", "figure"),
    ],
    Input("year-dropdown", "value"),
)
def update_values(selected_year):
    dff = df.copy()

    if selected_year != "All":
        dff = dff[dff["Year"] == selected_year]

    purchases = f"{dff['Quantity'].count():,}"
    spend = f"$ {dff['Spend'].sum():,.0f}"
    topcat = dff["Category"].value_counts().idxmax() if not dff.empty else "—"

    # Monthly Spend
    monthly = dff.groupby("Month", observed=True)["Spend"].sum().reset_index()
    fig_sales = px.bar(
        monthly, x="Month", y="Spend", text_auto=".2s",
        title="Total Monthly Spend", color_discrete_sequence=["#F79500"]
    )
    fig_sales.update_layout(
        xaxis_title=None, yaxis_title=None,
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=30, r=30, t=40, b=30)
    )

    # Top 5 Categories
    top_cats = dff["Category"].value_counts().head(5).reset_index()
    top_cats.columns = ["Category", "Count"]
    fig_cat = px.treemap(
        top_cats, path=["Category"], values="Count", color="Category",
        color_discrete_sequence=["#cb7721", "#b05611", "#ffb803", "#F79500", "#803f0c"],
        title="Top 5 Purchase Categories"
    )
    fig_cat.update_traces(textfont=dict(size=13))
    fig_cat.update_layout(margin=dict(l=30, r=30, t=40, b=30))

    return purchases, spend, topcat, fig_sales, fig_cat