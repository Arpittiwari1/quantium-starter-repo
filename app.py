import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html

# Load the formatted data
df = pd.read_csv("formatted_sales_data.csv")
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

# Aggregate sales by date and sort
daily = df.groupby('Date', as_index=False)['Sales'].sum().sort_values('Date')

app = Dash(__name__)
app.title = "Pink Morsel Sales Visualiser"

fig = px.line(
    daily,
    x="Date",
    y="Sales",
    title="Daily Sales of Pink Morsel",
    labels={"Date": "Date", "Sales": "Sales (Revenue)"}
)

# Add vertical marker for the price increase date using add_shape + annotation
cutoff = "2021-01-15"
fig.add_shape(
    type="line",
    x0=cutoff, x1=cutoff,
    y0=0, y1=1,
    xref="x", yref="paper",
    line=dict(color="red", dash="dash"),
)
fig.add_annotation(
    x=cutoff,
    y=1.02,
    xref="x",
    yref="paper",
    showarrow=False,
    text="Price Increase (15 Jan 2021)",
    align="left",
    bgcolor="rgba(255,255,255,0.8)"
)

fig.update_layout(
    margin=dict(t=80, b=40, l=40, r=40),
    xaxis_title="Date",
    yaxis_title="Sales (Revenue)"
)

app.layout = html.Div([
    html.H1("Pink Morsel Sales Over Time"),
    dcc.Graph(id="sales-line", figure=fig)
])

if __name__ == "__main__":
    app.run(debug=True)
