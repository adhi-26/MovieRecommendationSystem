import pkl
import numpy as np
import pandas as pd

from gensim.models import Word2Vec
from scipy.sparse import csr_matrix
from gensim.models import KeyedVectors


from preprocessing import preprocesstext
from sklearn.preprocessing import normalize

from sklearn.feature_extraction.text import TfidfVectorizer


def create_proprocessed_df():
    df = pd.read_csv('MovieData/movie_database.csv', index_col=['imdb-id'])
    df['processed-overview'] = df['overview'].apply(preprocesstext)
    processed_df = df[['processed-overview']]
    return processed_df

def load_w2vmodel(path):
    w2v_model = KeyedVectors.load_word2vec_format(path, binary=True)
    return w2v_model

def tokenize(text:str):
    return text.split()

def train_w2v_model(corpus, path):
    
    # takes list of tokens as input and uses it to train the google model

    google_model = Word2Vec(corpus, vector_size=300, window=5, min_count = 2, workers=5)
    google_model.build_vocab(corpus)
    google_model.wv.vectors_lockf = np.ones(len(google_model.wv))
    google_model.wv.intersect_word2vec_format(path, lockf=1.0, binary=True )
    google_model.train(corpus, total_examples=google_model.corpus_count, epochs = 5)
    return google_model

def vectorizer(data):
    vectorizer = TfidfVectorizer(analyzer='word')
    plot_vectors = vectorizer.fit_transform(data.values)
    return vectorizer, plot_vectors

def tfidf_w2v(document, feature_names, model, tfidf_dict):


    # Combines word embeddings and their tfidf weights to produce a document vector

    #since we used model with 300 dimensions
    tfidf_weighted_vectors = []
    line = 0
    for overview in document:
        overview_vec = np.zeros(300)
        weight_sum = 0
        words = overview.split()
        for word in set(words):
            if word in model.wv.key_to_index.keys() and word in feature_names:
                vec = model.wv[word]
                tf_idf = tfidf_dict[word] * (words.count(word)/len(words))
                overview_vec += tf_idf * vec
                weight_sum += tf_idf
        if weight_sum != 0:
            overview_vec /= weight_sum
        tfidf_weighted_vectors.append(overview_vec)
        line+=1
        if line%100 == 0:
            print(f'{line} overviews done')
    return csr_matrix(np.array(tfidf_weighted_vectors))


if __name__ == '__main__':
    # process plot synopsis
    df = create_proprocessed_df()
    print('overviews processed')

    # 'gensim-data/word2vec-google-news-300/word2vec-google-news-300.gz'
    # Use the path to the google word2vec model here:
    google_w2v_path = ''
    google_w2v_model = load_w2vmodel(google_w2v_path)

    # Train your data with the pretrained model
    google_model = train_w2v_model(df['processed-overview'].apply(tokenize), google_w2v_path)
    
    # save trained google model
    pkl.save_pickle('pickles', 'google_model', google_model)
    print('model trained and saved')

    # tfidf vectorization to get tfidf weights of words
    tfidfvectorizer, plot_vectors = vectorizer(df['processed-overview'])
    print('tfidf weight calculated')

    # returns VOCABULARY in the vectorizer
    tfidf_featurenames = tfidfvectorizer.get_feature_names_out()

    # dictionary of words and their tfidf weights
    tfidf_list = dict(zip(tfidf_featurenames, tfidfvectorizer.idf_))
    print(tfidf_list)

    # save tfidf vectorizer
    pkl.save_pickle('pickles/vectorizers', 'tfidf_vectorizer', tfidfvectorizer)
    print('tfidf vectorizer saved')

    # Create vectors of Plots
    vectors = tfidf_w2v(df['processed-overview'].to_list(), tfidf_featurenames, google_model, tfidf_list)

    #normalizing plots
    vectors = normalize(vectors)

    print('plot vectors created')

    # save pickle of plot vectors
    pkl.save_pickle('pickles/vectors', 'plot_vectors', vectors)


