import os

import streamlit as st
from dotenv import load_dotenv

from api.omdb import OMDBApi
from recsys import ContentBaseRecSys
from PIL import Image

# Загрузка градиентного фона для всего приложения
st.markdown(
    """
    <style>
        body {
            background-image: linear-gradient(to bottom, #232323, #131313);
            background-color: #131313;
            color: #E4DADA;
        }
        
        .css-1g7m0tk {
            background-color: #f9b033;
        }
    </style>
    """,
    unsafe_allow_html=True
)


# Настройки шрифта и размера шрифта в постерах
st.markdown(
    """
    <style>
        body {
            font-family: Arial, sans-serif;
        }
        .poster-title {
            font-size: 20px;
        }
        .poster-image {
            vertical-align: middle;
        }
    </style>
    """,
    unsafe_allow_html=True
)

def main():
    # Создание колонок
    col1, col2 = st.columns(2)
    
    # Загрузка изображения
    image = Image.open("C:/Users/evpet/Desktop/My Projects/DS14new/src/assets/hlop.png")
    
    # Вставка изображения в первую колонку
    with col1:
        st.image(image, width=250)
    
    # Вставка содержимого во вторую колонку
    with col2:
        st.markdown("""
            <style>
            .custom-textarea {
                font-size: 20px;
                height: 360px;
                border: none;
                width: 100%;
                background-color: inherit;
                color: inherit;
                font-family: inherit;
                text-align: right;
            }
            </style>
            <textarea class="custom-textarea">
            This service was developed to give you the opportunity to find a movie based on your viewing experience. Choose a movie that you like and the service will recommend you similar movies. You can also specify your favorite genre and the production country of the film.
            </textarea>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

TOP_K = 5
load_dotenv()

API_KEY = os.getenv("API_KEY") # Получение API ключа из переменных окружения
MOVIES = os.getenv("MOVIES") # Получение пути к файлу с данными о фильмах
DISTANCE = os.getenv("DISTANCE") # Получение пути к файлу с данными о расстоянии между фильмами

omdbapi = OMDBApi(API_KEY) # Создание экземпляра класса для работы с OMDB API

recsys = ContentBaseRecSys(
    movies_dataset_filepath=MOVIES,
    distance_filepath=DISTANCE,
)

# Работа с содержимым приложения (заголовки, графы, наименования, списки и т.д.)
st.markdown(
    "<h2 style='text-align: center; color: #E4DADA;'>Find an excellent film for your evening</h2>",
    unsafe_allow_html=True
)

selected_movie = st.selectbox( 
    "Choose the film you like:",
    recsys.get_title()
)

selected_genre = st.multiselect(
    "Select genre:",
    list(recsys.get_genres())
)

selected_country = st.multiselect(
    "Select country:",
    list(recsys.get_country())
)

if st.button('Show recommended'):
    st.write("Recommended films:")   

    recommended_movie_names = recsys.recommendation(selected_movie, top_k=TOP_K, genres=selected_genre, country=selected_country)
    recommended_movie_posters = omdbapi.get_posters(recommended_movie_names)   

    if recommended_movie_names:
        columns = st.columns(TOP_K)
        for index in range(min(len(recommended_movie_names), TOP_K)):
            with columns[index]:
                st.markdown(
                    '<div class="poster-container">'
                    '<img class="poster-image" src="{}"/>'
                    '<h2 class="poster-title">{}</h2>'
                    '</div>'.format(
                        recommended_movie_posters[index],
                        recommended_movie_names[index]
                    ),
                    unsafe_allow_html=True
                )

    else:
        st.write("Sorry, can't find anything. Try to choose other parameters.")

st.markdown(
    """
    <style>
        .poster-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
        }

        .poster-title {
            font-size: 20px;
            margin-top: 10px;
            word-wrap: break-word;
            text-align: center;
        }

        .poster-image {
            width: 100%;
            height: auto;
        }

    </style>
    """,
    unsafe_allow_html=True
)