from itertools import groupby
import json
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

def init_df():
    table_MN = pd.read_html('https://www.cngsante.fr/chiron/celine/listing.html')[0]
    table_MN = pd.DataFrame(columns=table_MN.iloc[8], data=table_MN.iloc[9:].values)
    table = table_MN.drop(columns=['Désir (non officiel) en chirurgie générale','SubDis','Vœu','CESP','Etat','Absence'])

    def getRang(value):
        try:
            return int(value.split('/')[0])
        except:
            return np.nan
    def getEtudiant(value):
        try:
            return int(value)
        except:
            return int(value.split('(')[1].split(')')[0])
    def toInt(value):
        try:
            return int(value)
        except:
            return np.nan

    table['Rang'] = table['Rang'].apply(getRang).astype('Int64')
    table['Etudiant'] = table['Etudiant'].apply(getEtudiant).astype('Int64')
    table['Offre'] = table['Offre'].apply(toInt).astype('Int64')
    table['Discipline'] = table['Discipline'].apply(lambda x : x.split(': ')[1] if ':' in x else x)
    table = table.replace({' LA\xa0REUNION':'LA REUNION'})
    table = table.replace({'LA\xa0REUNION':'LA REUNION'})
    table = table.replace({'MARTINIQUE/POINTE A\xa0PITRE':'MARTINIQUE/POINTE A PITRE'})

    positions = json.load(open('./coordinates.json'))

    table = table.set_index('Etudiant')
    table = table.dropna()
    table = table.reset_index()

    data = pd.read_csv('places.csv',encoding='utf-8')
    data = data.replace({' LA\xa0REUNION':'LA REUNION'})
    data = data.replace({'LA\xa0REUNION':'LA REUNION'})
    data = data.replace({'MARTINIQUE/POINTE A\xa0PITRE':'MARTINIQUE/POINTE A PITRE'})
    data['Discipline'] = data['variable']
    data['Offre'] = data['value']
    data = data.reset_index()
    data = data[['Ville','Discipline','Offre']]
    table['Ville'] = table['Subdivision']
    result = pd.concat([table,data])
    result = result.drop(columns=['Subdivision']).fillna(0)
    longitude = []
    lattitude = []
    for i in range(len(result)):
        longitude.append(positions[result['Ville'].iloc[i]]['long'])
        lattitude.append(positions[result['Ville'].iloc[i]]['lat'])

    result['lattitude'] = lattitude
    result['longitude'] = longitude
    result['Rang'] = result['Rang'].fillna(0)
    result['Etudiant'] = result['Etudiant'].fillna(0)
    result = result.replace({'HCL':'LYON'})
    result = result.sort_values('Etudiant').reset_index()
    return result

def filter_df(df,rank,spe):
    df = df[(df.Etudiant == 0) | (df.Etudiant <= rank)]
    df = df[df.Discipline.isin(spe)]
    df = df[df.Offre !=0]
    df = df[['Etudiant','Ville','Discipline','Offre','Rang','lattitude','longitude']]\
        .groupby(['Ville','Discipline'])\
        .agg({
            "Rang":"max",
            "Offre":"first",
            'longitude':'first',
            'lattitude':'first'})
    df['Reste'] = df['Offre'] - df['Rang']
    return df.reset_index()

def get_map(fdf):
    df = fdf[["Ville","Discipline","Reste","lattitude","longitude"]]\
        .groupby(['Ville','Discipline'])\
        .agg({"lattitude":"first","longitude":"first","Reste":"min"})\
        .reset_index()
    df = df\
        .groupby('Ville')\
        .agg({"Discipline":"first","lattitude":"first","longitude":"first","Reste":"sum"})\
        .reset_index()
    rfig = px.scatter_mapbox(
            df,
            size=df["Reste"].values.astype('float32'),
            lat="lattitude",
            lon="longitude",
            color="Ville",
            zoom=5,
            center=dict(lat=45.83,lon=1.26)
            )

    rfig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        font={"color":"white"},
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=0,b=0,l=0,r=0),
        height=800)
    return rfig

def get_table(fdf):
    df = fdf[['Ville','Discipline','Reste']]
    df = df[df.Reste!=0]
    rtable = go.Figure(data=[
    go.Table(
        header=dict(values=['Ville','Discipline','Reste'],
        fill_color="#7858A6"),
        cells=dict(values=df.values.transpose(),
        fill_color="rgba(0,0,0,0)")
    )])
    rtable.update_layout(
    paper_bgcolor='rgba(0,0,0,0)',
    font={"color":"white"},
    plot_bgcolor="rgba(0,0,0,0)",
    height=550,
    margin=dict(t=20,l=20,r=20,b=20)
    )
    return rtable