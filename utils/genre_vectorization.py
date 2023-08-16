import pandas as pd
from sklearn.preprocessing import MultiLabelBinarizer, normalize
import pkl

#import movie data
df= pd.read_csv('MovieData/movie_database.csv')
genres_list = df['genre'].str.split(', ').tolist()

# fitting movie genres into binary 
multilabelb = MultiLabelBinarizer(sparse_output=True)
genre_vectors = multilabelb.fit_transform(genres_list)

#normalizing the genre vectors
genre_vectors = normalize(genre_vectors)

# save pickle of normalized genre vectors
pkl.save_pickle('pickles/vectors', 'genre_vectors', genre_vectors)

# save pickle of binarizer
pkl.save_pickle('pickles/vectorizers', 'genre_vectorizer', multilabelb)

#convert genre vectors to dataframe
# genres_df = pd.DataFrame(genre_vectors.todense(), index=df['imdb-id'], columns = multilabelb.classes_)