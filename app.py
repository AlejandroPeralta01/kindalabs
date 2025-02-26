import pandas as pd
from flask import Flask, request ,render_template
import folium

# Iniciamos la aplicación
app = Flask(__name__)


url = "https://data.sfgov.org/resource/yitu-d5am.csv"
coords = (37.7749, -122.4194) # coordenadas del centro de San Francisco, según google :)
zoom = 12

def load_data() -> pd.DataFrame:
    """
    Esta función carga los datos desde la URL, además realiza una limpieza de los datos

    Retunrs:
        pd.DataFrame: Datos de las filmaciones ya filtrados
    """

    df = pd.read_csv(url)

    return df.dropna(subset=['locations','latitude','longitude'])


def create_map(filtered_df : pd.DataFrame) -> tuple:
    """
    Crea un mapa usando Folium con marcadores para cada ubicación

    Return:
        HTML del mapa
    """

    mapa = folium.Map(location=coords, zoom_start=zoom, width="50%",height="50%")

    mapa_html = None

    if not filtered_df.empty:

        for index , row in filtered_df.iterrows():

            latitude , longitude = float(row['latitude']) , float(row['longitude'])

            popup_text = f"{row['title']} ({row.get('release_year','Desconocido')}) -- {row['locations']}"

            folium.Marker([latitude, longitude],popup=popup_text,tooltip=row['title']).add_to(mapa)
        
        mapa_html = mapa._repr_html_()

    return mapa_html


movies_df= load_data()

@app.route('/', methods=['GET', 'POST'])

def index():

    movie_name = request.form.get('movie','')

    message = None

    if movie_name:

        filtered_df = movies_df[movies_df['title'].str.contains(movie_name, case=False, na=False)]

        if filtered_df.empty:
            message = 'No se encuentraron resultados, ingrese un título válido'

    else:
        
        filtered_df = movies_df

    mapa_html = create_map(filtered_df)

    return render_template('index.html', mapa_html=mapa_html, movie_name=movie_name, message=message)

if __name__ == '__main__':
    app.run(debug=True)






