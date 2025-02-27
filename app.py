import pandas as pd
from flask import Flask, request ,render_template
import folium
import os
from dotenv import load_dotenv

load_dotenv() # Carga de variables de entorno

app = Flask(__name__)

def load_data() -> pd.DataFrame:

    """
    Esta función carga los datos desde la URL, además realiza una limpieza de los datos

    Retunrs:
        pd.DataFrame: Datos de las filmaciones ya filtrados
    """

    df = pd.read_csv(os.getenv("URL"))

    return df.dropna(subset=['locations','latitude','longitude'])


def create_map(filtered_df : pd.DataFrame) -> str | None:

    """
    Crea un mapa usando Folium con marcadores para cada ubicación

    Return:
        HTML del mapa
    """

    mapa = folium.Map(location=tuple(map(float,os.getenv("COORDS").split(','))),
                      zoom_start=int(os.getenv("ZOOM"))
                      )

    mapa_html = None

    if not filtered_df.empty:

        for _ , row in filtered_df.iterrows():

            latitude , longitude = float(row['latitude']) , float(row['longitude'])

            popup_text = f"{row['title']}<br>({row.get('release_year','N/A')})<br>{row['locations']}"

            popup = folium.Popup(popup_text, max_width=300)

            folium.Marker([latitude, longitude],popup=popup,tooltip=row['title']).add_to(mapa)
        
        mapa_html = mapa._repr_html_()

    return mapa_html

# Carga inicial de los datos
movies_df= load_data() 

@app.route('/', methods=['GET', 'POST'])

def index() -> str:

    """
    Renderiza la página principal con un mapa de ubicaciones de película

    Returns:
        str: Página HTML renderizada y posible mensaje de error
    """

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
    app.run(debug=False)






