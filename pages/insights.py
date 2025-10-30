import dash
from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
from utils.utils import load_data

dash.register_page(__name__, path="/insights", name="Category Insights")

CSV_PATH = "data/amazon-purchases.csv"
df = load_data(CSV_PATH)

layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.Label("Category"),
            dcc.Dropdown(sorted(df['Category'].dropna().unique()), multi=True, id="cat-dd")
        ], md=4),
        dbc.Col([
            html.Label("Year"),
            dcc.Dropdown(sorted(df['Year'].unique()), multi=True, id="year2-dd")
        ], md=4),
    ], className="mb-2"),

    dbc.Row([
        dbc.Col(html.Div([
            html.H5("Price vs. Quantity (bubble sized by Spend)", className="mb-2"),
            dcc.Graph(id="scatter")
        ], className="section-card"), md=12),
    ])
], fluid=True)

@dash.callback(
    Output("scatter", "figure"),
    Input("cat-dd", "value"),
    Input("year2-dd", "value"),
)
def update_scatter(cats, years):
    dff = df.copy()
    if cats:
        dff = dff[dff['Category'].isin(cats)]
    if years:
        dff = dff[dff['Year'].isin(years)]

    agg = (dff.groupby(['Title','Category'], as_index=False)
           .agg({'Purchase Price Per Unit':'mean','Quantity':'sum','Spend':'sum'}))
    if agg.empty:
        return px.scatter(title="No data for the selected filters.")

    fig = px.scatter(
        agg, x='Purchase Price Per Unit', y='Quantity',
        size='Spend', color='Category', hover_name='Title',
        labels={'Purchase Price Per Unit':'Avg Price', 'Quantity':'Total Quantity'}
    )
    fig.update_layout(margin=dict(l=0,r=0,t=0,b=0))
    return fig
