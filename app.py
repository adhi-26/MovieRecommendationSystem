import streamlit as st
import utils.pkl as pkl
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import RecommendationsPage
import numpy as np
import os

st.set_page_config('Movie Recommendation System', layout='centered', page_icon=":film:")

@st.cache_data(show_spinner=False)
def load_data(path = 'pickles/features_series.pkl'):
    combined_series = pkl.load_pickle(path)
    return combined_series

def similarity_matrix(movie_ids: list, series: pd.Series):
    sim_scores = pd.Series(cosine_similarity(series.to_list(), series[movie_ids].to_list()).sum(axis = 1), index=series.index).sort_values(ascending=False)
    mask = ~sim_scores.index.str.contains('|'.join(movie_ids))
    return sim_scores.loc[mask]

def filter_df(df: pd.DataFrame, languages: list):
    return df[df['language'].str.contains('|'.join(languages))]

def get_top_ntitles(num_titles, sim_scores, df):
    top_titles = []

    for item in sim_scores.index:
        if item in df.index:
            top_titles.append(item)
        if len(top_titles)==num_titles:
            break
    return top_titles

def get_recommendations(movie_ids: list, ntitles: int, languages: list):
    sim_scores = similarity_matrix(movie_ids, features_series)
    df = filter_df(metadata, languages)

    # for when number of requested titles is greater than number of available titles
    n_unwatched = len(df) - len(movie_ids)
    ntitles = min(n_unwatched,ntitles)

    return get_top_ntitles(ntitles, sim_scores, df)


features_series = load_data()
metadata = pd.read_csv('MovieData/movie_database.csv', index_col='imdb-id')

language_codes = {  
                    'English' : 'en',
                    'French' : 'fr',
                    'Tamil' : 'ta', 
                    'Italian':'it', 
                    'Malayalam' : 'ml', 
                    'Hindi' : 'hi', 
                    'Korean' : 'ko', 
                    'Japanese': 'ja', 
                    'German' : 'de',
                    'Spanish' : 'es',
                    'Danish' : 'da',
                    'Chinese' : 'cmn'
                }

language_names = {code:language.capitalize() for language, code in language_codes.items()}

# Page Layout
for _ in range(10):
    st.header('')
st.title('Movie Recommendation System')

movie_ids = st.multiselect(
                        label= 'Select movies that you like',
                        options=metadata.index.values,
                        format_func= lambda x: f'{metadata.loc[x,"title"]} ({int(metadata.loc[x,"release-year"])})',
                        placeholder='Select movies'
                        )

languages = st.multiselect(
                        label = 'Select preferred languages',
                        options = language_codes.values(),
                        format_func = lambda x: language_names[x],
                        placeholder ='Select Languages'
                        )

if st.button('Get Recommendations'):
    with st.spinner('Finding similar movies...Hold on'):
        recommended_movies = get_recommendations(movie_ids, 10, languages)
    RecommendationsPage.RenderPage(recommended_movies, metadata, language_names)