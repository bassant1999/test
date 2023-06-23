import pandas as pd
import numpy as np

# variables
free_books_df = pd.read_csv('new_df_free_onwebsite.csv')
similarity_matrix_df = pd.read_csv('simmat3.csv')
similarity_mat = similarity_matrix_df.to_numpy()


# recommendation function for free books
def recommend (book_title, no_recommendations):
    index = np.where(free_books_df["title"] == book_title)[0][0]
    similar_books = sorted(enumerate(similarity_mat[index]) , key=lambda x:x[1]   , reverse=True)[1:no_recommendations+1]
#     print(similar_books)
#     for i in similar_books:
#         print (new_df['title'][i[0]], i[1])
    return similar_books
def recommend_with_user_history (user_history, no_recommendations):
    #user_history is a dictionary of book-rating pairs
    #example: {"Peter Pan": 5, "The Wonderful Wizard of Oz": 3, "Moby Dick": 4}
    recommended_books = []
    books_indicies_ratings = {}
    total_similar_books = {}
    for key in user_history:
        index = np.where(free_books_df["title"] == key)[0][0]
        books_indicies_ratings[index] = user_history[key] 
#         print(books_indicies_ratings)
        
    for i in user_history:
        similar_books = recommend(i,no_recommendations)
#         print(similar_books)
        for j in similar_books:
            if j[0] not in user_history:
                if j[0] in total_similar_books and (j[1]*user_history[i]< total_similar_books[j[0]]):
                    continue;
                else:
                    total_similar_books[j[0]] = j[1]*user_history[i]
        
    similar_books_2 = sorted(total_similar_books.items(), key=lambda x:x[1], reverse=True)[0:no_recommendations]
    for i in similar_books_2:
        recommended_books.append({"title": free_books_df['title'][i[0]], "author": free_books_df['author'][i[0]], "id": free_books_df['id'][i[0]]})
#         print (new_df['title'][i[0]], i[1])
    return recommended_books