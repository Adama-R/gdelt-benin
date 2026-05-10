

# DASHBOARD INTERACTIF GDELT - BENIN

import pandas as pd
import streamlit as st
import plotly.express as px


# CONFIGURATION PAGE

st.set_page_config(page_title="Dashboard Bénin - GDELT", layout="wide")

st.title("Analyse des événements au Bénin")


# CHARGEMENT DES DONNÉES

# Veuillez changer le contenu de la variables "uploaded_file" afin de pointer vers vos données.
uploaded_file = r"C:\Users\adama\AllCodeProjets\gdelt-benin\data\processed\Analyse_Globale_F.csv"

df = pd.read_csv(uploaded_file)



# PRÉPARATION DES DONNÉES

# Conversion de la date
df["SQLDATE"] = pd.to_datetime(df["SQLDATE"], format="%Y%m%d", errors="coerce")


# FILTRES

st.sidebar.header("Filtres")

# Filtre temporel
date_min = df["SQLDATE"].min()
date_max = df["SQLDATE"].max()

date_range = st.sidebar.date_input(
    "Choisir une période",
    [date_min, date_max]
)

# Filtre acteur
actors = st.sidebar.multiselect(
    "Choisir Actor1",
    options=df["Actor1Name"].dropna().unique()
)

# Application des filtres
filtered_df = df.copy()

if len(date_range) == 2:
    filtered_df = filtered_df[
        (filtered_df["SQLDATE"] >= pd.to_datetime(date_range[0])) &
        (filtered_df["SQLDATE"] <= pd.to_datetime(date_range[1]))
    ]

if actors:
    filtered_df = filtered_df[filtered_df["Actor1Name"].isin(actors)]


# 1. EVOLUTION TEMPORELLE DES EVENEMENTS

st.subheader("Evolution des événements dans le temps")

timeline = filtered_df.groupby(filtered_df["SQLDATE"].dt.to_period("M")).size().reset_index(name="Count")
timeline["SQLDATE"] = timeline["SQLDATE"].astype(str)

fig1 = px.line(
    timeline,
    x="SQLDATE",
    y="Count",
    title="Nombre d'événements par mois"
)

st.plotly_chart(fig1, width='stretch')


# 2. TYPES D’EVENEMENTS VS IMPACT

st.subheader("Impact des types d'événements")

cross = pd.crosstab(filtered_df["Type_Evènement"], filtered_df["Impact_Evènement"]).reset_index()

fig2 = px.bar(
    cross,
    x="Type_Evènement",
    y=cross.columns[1:],
    title="Répartition des impacts par type d'événement",
    barmode="group"
)

st.plotly_chart(fig2, width='stretch')


# 3. ACTEURS LES PLUS ACTIFS

st.subheader("Acteurs les plus actifs")

actors_count = filtered_df["Actor1Name"].value_counts().head(10).reset_index()
actors_count.columns = ["Actor", "Count"]

fig3 = px.bar(
    actors_count,
    x="Count",
    y="Actor",
    orientation="h",
    title="Top 10 des acteurs les plus actifs"
)

st.plotly_chart(fig3, width='stretch')


# 4. SENTIMENT GLOBAL

st.subheader("Sentiments exprimés par les médias")

sentiment_count = filtered_df["Sentiment"].value_counts().reset_index()
sentiment_count.columns = ["Sentiment", "Count"]

fig4 = px.pie(
    sentiment_count,
    names="Sentiment",
    values="Count",
    title="Répartition des sentiments"
)

st.plotly_chart(fig4, width='stretch')


