from typing import List, Set
import pandas as pd
from .utils import parse

class ContentBaseRecSys:
    def __init__(self, movies_dataset_filepath: str, distance_filepath: str):
        """
        Инициализация класса ContentBaseRecSys.

        Args:
            movies_dataset_filepath (str): Путь к файлу с данными о фильмах.
            distance_filepath (str): Путь к файлу с данными о расстоянии между фильмами.
        """
        self.distance = pd.read_csv(distance_filepath, index_col='id')
        self.distance.index = self.distance.index.astype(int)
        self.distance.columns = self.distance.columns.astype(int)
        self._init_movies(movies_dataset_filepath)

    def _init_movies(self, movies_dataset_filepath) -> None:
        """
        Инициализация данных о фильмах.

        Args:
            movies_dataset_filepath (str): Путь к файлу с данными о фильмах.
        """
        self.movies = pd.read_csv(movies_dataset_filepath, index_col='id')
        self.movies.index = self.movies.index.astype(int)
        self.movies['genres'] = self.movies['genres'].apply(parse)

    def get_title(self) -> List[str]:
        """
        Получение списка названий фильмов.

        Returns:
            List[str]: Список названий фильмов.
        """
        return self.movies['original_title'].values

    def get_genres(self) -> Set[str]:
        """
        Получение множества жанров фильмов.

        Returns:
            Set[str]: Множество жанров фильмов.
        """
        genres = [item for sublist in self.movies['genres'].values.tolist() for item in sublist]
        return set(genres)

    def get_country(self) -> Set[str]:
        """
        Получение множества стран производства фильмов.

        Returns:
            Set[str]: Множество стран производства фильмов.
        """
        country = self.movies['production_countries'].apply(lambda x: [country['name'] for country in eval(x)])
        country = [item for sublist in country.tolist() for item in sublist]
        return set(country)

    def recommendation(self, title: str, top_k: int = 5, genres: Set[str] = None, country: Set[str] = None) -> List[str]:
        """
        Получение рекомендаций для заданного фильма.

        Args:
            title (str): Название фильма.
            top_k (int, optional): Количество рекомендаций. Defaults to 5.
            genres (Set[str], optional): Множество жанров для фильтрации рекомендаций. Defaults to None.
            country (Set[str], optional): Множество стран для фильтрации рекомендаций. Defaults to None.

        Returns:
            List[str]: Список рекомендованных фильмов.
        """
        movie_index = self.movies[self.movies['original_title'] == title].index[0]
        if genres and country:
            filtered_movies = self.filter_movies_by_genre_and_country(genres, country)
        elif genres:
            filtered_movies = self.filter_movies_by_genre(genres)
        elif country:
            filtered_movies = self.filter_movies_by_country(country)
        else:
            filtered_movies = None

        top_movies_indices = self.get_top_k_movies(movie_index, top_k, filtered_movies, genres, country)

        return self.movies.loc[top_movies_indices, 'original_title'].tolist()

    def get_top_k_movies(self, movie_index: int, top_k, filtered_movies: List[int] = None, genres: Set[str] = None, country: Set[str] = None) -> List[str]:
        """
    Получение индексов топ-K фильмов на основе расстояний от заданного фильма.

    Args:
        movie_index (int): Индекс заданного фильма.
        top_k (int): Количество фильмов для выборки.
        filtered_movies (List[int], optional): Список фильмов для фильтрации. Defaults to None.
        genres (Set[str], optional): Множество жанров для фильтрации. Defaults to None.
        country (Set[str], optional): Множество стран для фильтрации. Defaults to None.

    Returns:
        List[str]: Список индексов топ-K фильмов.
    """
        distances = self.distance.loc[movie_index].sort_values(ascending=False)
        if filtered_movies:
            distances = distances[distances.index.isin(filtered_movies)]
        if genres:
            filtered_indices = []
            for index in distances.index:
                if any(genre in self.movies.loc[index, 'genres'] for genre in genres):
                    filtered_indices.append(index)
            distances = distances[distances.index.isin(filtered_indices)]
        else:
            filtered_indices = []  # Инициализация filtered_indices как пустого списка

        if country:
            for index in distances.index:
                if any(c in self.movies.loc[index, 'production_countries'] for c in country):
                    filtered_indices.append(index)
            distances = distances[distances.index.isin(filtered_indices)]

        top_movies_indices = distances.index[1:top_k+1]
        return top_movies_indices


    def update_recommendations(self, new_title: str, top_k: int = 5, genres: Set[str] = None, country: Set[str] = None) -> List[str]:
        """
    Обновление рекомендаций на основе нового фильма.

    Args:
        new_title (str): Новое название фильма.
        top_k (int, optional): Количество рекомендаций. Defaults to 5.
        genres (Set[str], optional): Множество жанров для фильтрации рекомендаций. Defaults to None.
        country (Set[str], optional): Множество стран для фильтрации рекомендаций. Defaults to None.

    Returns:
        List[str]: Список рекомендованных фильмов.
    """
        return self.recommendation(new_title, top_k, genres, country)

    def filter_movies_by_genre(self, genres: Set[str]) -> List[int]:
        """
    Фильтрация фильмов по жанрам.

    Args:
        genres (Set[str]): Множество жанров для фильтрации.

    Returns:
        List[int]: Список индексов отфильтрованных фильмов.
    """
        filtered_movies = []
        for index, row in self.movies.iterrows():
            if any(genre in row['genres'] for genre in genres):
                filtered_movies.append(index)
        return filtered_movies

    def filter_movies_by_country(self, country: Set[str]) -> List[int]:
        """
    Фильтрация фильмов по странам производства.

    Args:
        country (Set[str]): Множество стран для фильтрации.

    Returns:
        List[int]: Список индексов отфильтрованных фильмов.
    """
        filtered_movies = []
        for index, row in self.movies.iterrows():
            if any(country in row['production_countries'] for country in country):
                filtered_movies.append(index)
        return filtered_movies

    def filter_movies_by_genre_and_country(self, genres: Set[str], country: Set[str]) -> List[int]:
        """
    Фильтрация фильмов по жанрам и странам производства.

    Args:
        genres (Set[str]): Множество жанров для фильтрации.
        country (Set[str]): Множество стран для фильтрации.

    Returns:
        List[int]: Список индексов отфильтрованных фильмов.
    """
        filtered_movies = []
        for index, row in self.movies.iterrows():
            if any(genre in row['genres'] for genre in genres):
                filtered_movies.append(index)
            if any(country in row['production_countries'] for country in country):
                filtered_movies.append(index)
        return filtered_movies