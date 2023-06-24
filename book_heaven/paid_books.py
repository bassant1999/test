import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import matplotlib.pyplot as plt
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Input
from tensorflow.keras.layers import Embedding,dot,Dot
from tensorflow.keras.utils import to_categorical
import matplotlib.pyplot as plt
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn import preprocessing
from tensorflow.keras.layers import Dropout, Flatten
from tensorflow.keras.optimizers import Adam
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
from .models import *



ids_list = list(paid_books.objects.filter().values_list('id', flat=True))
title_list = list(paid_books.objects.filter().values_list('title', flat=True))
author_list = list(paid_books.objects.filter().values_list('Authors', flat=True))

book_df = pd.DataFrame(list(zip(ids_list, title_list, author_list)),
               columns =['book_id', 'title', 'authors'])


#user history from paid books
def p_user_history(user):
    p_books = paid_books_rating.objects.filter(User_id = user)
    user_hist = {}
    for p_book in p_books:
        user_hist[p_book.Book_id.title] = p_book.rating
    return user_hist

def csv2dic(csv_path):
    df = pd.read_csv(csv_path,header= None)
    df = df.drop(df.index[0])
    df.iloc[:,1] = df.iloc[:,1].astype(int)
    df = df.set_index(1)
    df = df.drop(df.columns[0],axis=1)
    df.iloc[:,0] = df.iloc[:,0].astype(int)
    dic = df.to_dict()
    dicc = dic[2]
    return dicc

book2book_encoded = csv2dic("df_book2book_encoded.csv")
bookencoded2book = csv2dic("df_bookencoded2book.csv")
user2user_encoded = csv2dic("df_user2user_encoded.csv")
userencoded2user = csv2dic("df_userencoded2user.csv")
model1_path = "model_net_plain_2"
model2_path = "model_2_for_website"

def my_load_model(model_1_path):
    return keras.models.load_model(model_1_path)

#recommend function for paid books
def get_new_user_book_embeddings(book_df, model1_path, model2_path, user_books,  no_recommendations, embedding_layer_size= 150):
    books_list = list(user_books.keys())
    # print(books_list)
    books_ids_list = book_df[book_df["title"].isin(books_list)]["book_id"].values.tolist()
    # print(books_ids_list)

    model_2  = my_load_model(model2_path)
    model_1  = my_load_model(model1_path)
#     books_not_read_encoded = [[book2book_encoded.get(x)] for x in books_not_read]
    books_ids_list_encoded = [[book2book_encoded.get(x)] for x in books_ids_list]
    # print(books_ids_list_encoded)

    books_ids_list_encoded = np.asarray(books_ids_list_encoded).astype('float32')
    # print(books_ids_list_encoded)
    user_books_embeddings = model_2.predict(books_ids_list_encoded)
    user_books_embeddings = user_books_embeddings.reshape(len(user_books), embedding_layer_size)
    user_book_ratings = np.zeros(len(user_books))
    usr_books_keys =  list(user_books.keys())
    i = 0
    for index in range(len(user_books)):
        user_book_ratings[index] = user_books[usr_books_keys[i]]
        i += 1
    user_embedding, residuals, rank, s = np.linalg.lstsq(user_books_embeddings,user_book_ratings, rcond=-1) # Get embedding for new user
    user_embedding = user_embedding.reshape(1, embedding_layer_size) # User embedding based on choices of user
    user_embedding = np.squeeze(user_embedding)
    books_embeddings = model_1.get_layer('embedding_15').get_weights()
    books_embeddings = np.array(books_embeddings)
    books_embeddings = np.squeeze(books_embeddings)
    # print(np.shape(books_embeddings))
    # print(f"user embedding shape: {user_embedding.shape}")
    predicted_ratings = np.matmul(books_embeddings, user_embedding)
    predicted_dict = {}
    predicted_dict_2 = {}
    predicted_dict_temp = {}

    i = 0
    for rating in predicted_ratings:
#         if i not in books_ids_list: 
        predicted_dict[i] = rating
        i+=1
    temp_keys = [bookencoded2book.get(x) for x in predicted_dict.keys()]
    print(type(temp_keys))
    i = 0
    for key in predicted_dict:
        predicted_dict_temp[temp_keys[i]] = predicted_dict[key]
        i+=1
    for key in predicted_dict_temp:
        if key not in books_ids_list: 
            predicted_dict_2[key] = predicted_dict_temp[key]
    sorted_predicted_dict = sorted(predicted_dict_2.items(), key=lambda x:x[1], reverse = True)[:no_recommendations]
    # print(sorted_predicted_dict)
    # print(np.array(sorted_predicted_dict).shape)
    sorted_predicted_dict = dict(list(sorted_predicted_dict))
    # print(sorted_predicted_dict.keys())
    temp = book_df[book_df["book_id"].isin (sorted_predicted_dict.keys())]
    # print(temp.shape)
    recommendations = []
    for i in temp.itertuples():
        recommendations.append({"title":i.title, "author":i.authors})
    # print(recommendations)
    return recommendations