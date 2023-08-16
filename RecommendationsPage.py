import streamlit as st
from ast import literal_eval
import pandas as pd
def RenderPage(movie_ids: list, movies: pd.DataFrame, language: dict):
    
    for id in movie_ids:
        movie = movies.loc[id]
        col1, col2 = st.columns([1,3])
        with col1:
            st.image(movie['poster'], width=150)
        with col2:
            st.markdown(f"**{movie['title']}** (**{int(movie['release-year'])}**) | **{language[movie['language']]}**")
            st.markdown(f"**{movie['genre']}**")
            director = ', '.join([item['name'] for item in literal_eval(movie['directors'])])
            st.markdown(f"Director: {director}")
            cast = ', '.join([item['name'] for item in literal_eval(movie['cast'])])
            st.markdown(f"Cast: {cast}")
        st.markdown(f"Plot: {movie['overview']}")
        st.markdown('')
        st.markdown('')