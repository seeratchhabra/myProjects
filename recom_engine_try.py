# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
#Import libraries (tkinter is used for dialoguebox)
import tkinter as tk
from tkinter import simpledialog
import os
import pandas as pd

# the input dialog to get path from user 
ROOT = tk.Tk()
ROOT.withdraw()
USER_INP_Path = simpledialog.askstring(title="Path containing datasets",
                                  prompt="Please enter the complete path for datasets:")

print("Current working directory - ", os.getcwd())
#/Users/seeratchhabra/Desktop/Statistics/ml-100k
#change directory to where data is stored
try:
    os.chdir(USER_INP_Path)
    print("Directory changed to -" , os.getcwd())
except OSError:
    print("Can't change directory")
    

#Read ratings data containg ratings from users
rating_col_head = ['User_Id','Item_Id','Rating', 'Timestamp']
rating_data = pd.read_csv('u.data', sep = '\t',names = rating_col_head , encoding='latin-1')

#Read user data containing user information
users_col_head = ['User_Id','Age','Gender', 'Occupation', 'Zip_code']
users = pd.read_csv('u.user', sep = '|',names = users_col_head,  encoding='latin-1')

#Read Movie data  containg genre of each movie
item_col_head = ['Movie_id', "movie title" ,'release date','video release date', 'IMDb URL', 'unknown', 'Action', 'Adventure',
'Animation', 'Children\'s', 'Comedy', 'Crime', 'Documentary', 'Drama', 'Fantasy',
'Film-Noir', 'Horror', 'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Thriller', 'War', 'Western']
items = pd.read_csv('u.item', sep = '|',names = item_col_head,  encoding='latin-1')

# To see how data looks like
print()
print("Ratings Data - \n" ,rating_data.head())
print("Users Data - \n", users.head())
print("Items Data - \n", items.head())
print('User data -', users.shape , ' Ratings data - ', rating_data.shape, 'Items data -',
      items.shape)

# In order to get movie names in rating dataset, create a new dataframe to join
movie_names = pd.DataFrame(columns=['Movie_id', "movie title"])
movie_names = items[['Movie_id', "movie title"]].append(movie_names)
#Join rating data and movie names 
rating_data = pd.merge(rating_data, movie_names, how ='inner', left_on = 'Item_Id', 
                      right_on ='Movie_id')

#Mean movie rating and # of ratings per movie
movie_count_rating = pd.DataFrame(rating_data.groupby("movie title")["User_Id"].count())
movie_count_rating["Mean rating"] = pd.DataFrame(rating_data.groupby("movie title")["Rating"].mean())
movie_count_rating = movie_count_rating.rename(columns = {"User_Id": "# of ratings"})
movie_count_rating = movie_count_rating.sort_values("# of ratings", ascending = False)
print(movie_count_rating.head())

#Matrix with index as user ID and columns as movie names and values as ratings. 
#This matrix will be used to calculate pearsons correlation coefficient
user_movie_matrix = rating_data.pivot_table(index = "User_Id", columns = "movie title", values = 'Rating')
print(user_movie_matrix.head())

#Function to calculate similarity of the movie name passed with all other movies 
def fun_correlation(movie_name, user_movie_matrix):
    try:
        movie_similarity = user_movie_matrix .corrwith(user_movie_matrix [movie_name])
        movie_similarity = pd.DataFrame(movie_similarity, columns=['Correlation'])
        movie_similarity.dropna(inplace=True)
        movie_similarity = movie_similarity.sort_values('Correlation', ascending=False)
        movie_similarity = pd.merge(movie_similarity,movie_count_rating ,how ='inner', on = 'movie title')
        output = pd.DataFrame(movie_similarity[ (movie_similarity['# of ratings'] > 50) & (movie_similarity['Correlation'] > 0.5 )])
        print()
        print("Similar movies are:\n",output.index.tolist())
    except KeyError:
        print("\nMovie name does not exist in database!")

#Dropdown list asking user to select movie post which gives recommendation of similar movies

master = tk.Tk()
master.geometry("400x200")
master.title("Select movie name from dropdown")
tk.Label(master, text = "Movies dropdown list").grid(row=0)

# Create a Tkinter variable which stores the selection
tkvar = tk.StringVar()

# Names of all movies sorted
movie_names = movie_names.sort_values('movie title',ascending = False)
choices = movie_names['movie title']
tkvar.set('Star Wars (1977)') # set the default option

#Dropdpwn menu options
popupMenu = tk.OptionMenu(master, tkvar, *choices)
popupMenu.configure(font = ("Arial",10))
popupMenu.grid(row=2,column =4)

# continuously checks for selection and triggers the recommendation function
def change_dropdown(*args):
    print( tkvar.get() )
    fun_correlation(tkvar.get(),user_movie_matrix)

# link function to change dropdown
tkvar.trace('w', change_dropdown)

master.mainloop()



