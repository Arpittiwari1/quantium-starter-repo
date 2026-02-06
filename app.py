import pathlib
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

ROOT = pathlib.Path(__file__).parent

df = pd.read_csv(ROOT / "formatted_sales_data.csv")
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
df['Region'] = df['Region'].astype(str).str.lower()

daily_by_region = (
    df.groupby(['Date', 'Region'], as_index=False)['Sales']
      .sum()
      .sort_values('Date')
)

REGIONS = ["north", "east", "south", "west"]
ALL_OPTION = "all"
CUTOFF = "2021-01-15"

app = Dash(__name__, assets_folder=str(ROOT / "assets"))
app.title = "Pink Morsel Sales Visualiser"

def make_figure(df_plot, title):
    fig = px.line(
        df_plot,
        x="Date",
        y="Sales",
        title=title,
        labels={"Date": "Date", "Sales": "Sales (Revenue)"},
        template="simple_white"
    )

    fig.add_shape(
        type="line",
        x0=CUTOFF, x1=CUTOFF,
        y0=0, y1=1,
        xref="x", yref="paper",
        line=dict(color="red", dash="dash"),
    )
    fig.add_annotation(
        x=CUTOFF,
        y=1.02,
        xref="x",
        yref="paper",
        showarrow=False,
        text="Price Increase (15 Jan 2021)",
        align="left",
        bgcolor="rgba(255,255,255,0.85)",
        bordercolor="rgba(0,0,0,0.06)",
        borderwidth=0.5
    )

    fig.update_layout(
        margin=dict(t=90, b=40, l=40, r=40),
        xaxis_title="Date",
        yaxis_title="Sales (Revenue)",
        hovermode="x unified"
    )
    return fig

daily_all = daily_by_region.groupby('Date', as_index=False)['Sales'].sum()
initial_fig = make_figure(daily_all, "Daily Sales of Pink Morsel — All Regions")

app.layout = html.Div(className="container", children=[
    html.Header(className="header", children=[
        html.H1("Pink Morsel Sales Over Time", className="title"),
        html.P("Filter by region to inspect how the price increase affected sales.", className="subtitle")
    ]),

    html.Div(className="controls card", children=[
        html.Div(className="control-block", children=[
            html.Label("Region", className="control-label"),
            dcc.RadioItems(
                id="region-radio",
                options=[{"label": r.capitalize(), "value": r} for r in REGIONS] + [{"label": "All", "value": ALL_OPTION}],
                value=ALL_OPTION,
                labelStyle={"display": "inline-block", "margin-right": "12px"},
                inputStyle={"margin-right": "6px"},
                className="radio-items",
                persistence=True,
                persistence_type="session"
            )
        ])
    ]),

    html.Div(className="chart card", children=[
        dcc.Graph(id="sales-line", figure=initial_fig, config={"displayModeBar": False})
    ]),

    html.Footer(className="footer", children=[
        html.Small("Data: Soul Foods — Pink Morsel transactions. Vertical line marks price increase on 15 Jan 2021.")
    ])
])

@app.callback(
    Output("sales-line", "figure"),
    Input("region-radio", "value")
)
def update_chart(selected_region):
    if selected_region == ALL_OPTION:
        df_plot = daily_by_region.groupby('Date', as_index=False)['Sales'].sum()
        title = "Daily Sales of Pink Morsel — All Regions"
    else:
        df_plot = daily_by_region[daily_by_region['Region'] == selected_region]
        title = f"Daily Sales of Pink Morsel — {selected_region.capitalize()}"
        if df_plot.empty:
            df_plot = pd.DataFrame({"Date": [], "Sales": []})

    return make_figure(df_plot, title)

if __name__ == "__main__":
    app.run(debug=True)
