import os
import pandas as pd

def drop_nan(df: pd.DataFrame, subset: list):    
    return df.dropna(subset=subset)

ls = os.listdir('ScrapedData')
combined_df = pd.DataFrame()

for file in ls:
    if '.csv' in file:
        df = pd.read_csv(f'ScrapedData/{file}')
        combined_df = pd.concat([combined_df, df], join = 'outer', axis=0)

# drop duplicate values
combined_df.drop_duplicates(subset=['imdb-id'], inplace=True)
combined_df.set_index(['imdb-id'], inplace=True)

# drop nan values
combined_df = drop_nan(combined_df, ['overview', 'genre', 'release-year'])

# drop rows with certain genres
combined_df = combined_df[~combined_df['genre'].str.contains('Reality-TV|News')]

# convert to int dtype
# combined_df[['release-year','runtime', 'metascore']] = df[['release-year','runtime', 'metascore']].astype('Int64')

combined_df.to_csv('ScrapedData/movie_database.csv')
