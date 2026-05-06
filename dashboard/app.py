import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px

# Charger les données (veuillez changer la variables "PATH" selon votre ordinateur.)
PATH = "C:/Users/adama/3D Objects/obsidiant/iSheero/Hackathon/gdelt-benin/data/processed/GDELT_DATA_BENIN_2025-1.csv"

df = pd.read_csv(PATH, sep=",", encoding="latin1")

df["SQLDATE"] = pd.to_datetime(df["SQLDATE"], format="%Y%m%d")

app = Dash(__name__)

app.layout = html.Div([
    html.H1("Dashboard GDELT - Crises et Relations"),

    dcc.DatePickerRange(
        id="date-picker",
        start_date=df["SQLDATE"].min(),
        end_date=df["SQLDATE"].max()
    ),

    dcc.Dropdown(
        options=[{"label": str(i), "value": i} for i in sorted(df["QuadClass"].dropna().unique())],
        multi=True,
        id="quad-filter",
        placeholder="Filtrer par type d'événement"
    ),

    html.Label("Acteur 1"),
    dcc.Dropdown(
        options=[{"label": i, "value": i} for i in df["Actor1Name"].dropna().unique()],
        multi=True,
        id="actor1-filter"
    ),

    html.Label("Recherche"),
    dcc.Input(
        id="search",
        type="text",
        placeholder="ex: gouvernement, police..."
    ),

    dcc.Graph(id="time-series"),
    dcc.Graph(id="map"),
    dcc.Graph(id="relations")
])

@app.callback(
    [Output("time-series", "figure"),
     Output("map", "figure"),
     Output("relations", "figure")],
    [Input("date-picker", "start_date"),
     Input("date-picker", "end_date"),
     Input("quad-filter", "value"),
     Input("actor1-filter", "value"),
     Input("search", "value")]
)
def update_graphs(start_date, end_date, quad_values, actors, search):

    dff = df.copy()

    dff = dff[(dff["SQLDATE"] >= start_date) & (dff["SQLDATE"] <= end_date)]

    if quad_values:
        dff = dff[dff["QuadClass"].isin(quad_values)]

    if actors:
        dff = dff[dff["Actor1Name"].isin(actors)]

    if search:
        dff = dff[dff["Actor1Name"].str.contains(search, case=False, na=False)]

    if dff.empty:
        empty_fig = px.scatter(title="Aucune donnée disponible")
        return empty_fig, empty_fig, empty_fig

    df_daily = dff.groupby("SQLDATE").agg({
        "GoldsteinScale": "mean",
        "AvgTone": "mean"
    }).reset_index()

    fig_time = px.line(
        df_daily,
        x="SQLDATE",
        y=["GoldsteinScale", "AvgTone"],
        title="Évolution des crises"
    )

    try:
        dff_map = dff.dropna(subset=["ActionGeo_Fullname"])

        fig_map = px.scatter_geo(
            dff_map,
            locations="ActionGeo_Fullname",
            locationmode="country names",
            color="AvgTone",
            size="GoldsteinScale",
            hover_name="ActionGeo_Fullname",
            title="Carte des événements"
        )
    except:
        fig_map = px.scatter(title="Carte indisponible")

    try:
        rel = dff[["Actor1Name", "Actor2Name"]].dropna()

        if rel.empty:
            fig_rel = px.scatter(title="Pas de relations disponibles")
        else:
            rel = rel.value_counts().reset_index(name="count").head(15)
            rel["relation"] = rel["Actor1Name"] + " → " + rel["Actor2Name"]

            fig_rel = px.bar(
                rel,
                x="count",
                y="relation",
                orientation='h',
                title="Relations entre acteurs"
            )
    except:
        fig_rel = px.scatter(title="Erreur relations")

    return fig_time, fig_map, fig_rel

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=8050,
        debug=False,
        use_reloader=False
    )
