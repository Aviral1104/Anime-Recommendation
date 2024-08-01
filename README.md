# Anime-Recommendation

Sparse Matrix Creation: 
A sparse matrix is created using the user ratings data. This is more memory-efficient for large datasets with many zero values.

KNN Model Fitting: 
A Nearest Neighbors model is fitted using the sparse matrix. This model will be used to find similar users based on their rating patterns.

Genre Extraction: 
Extracts all unique genres from the anime dataset.

get_recommendations Function: 
This function takes a user_id and selected genres, and returns anime recommendations: 
  -	Finds similar users using the KNN model.
  -	Calculates weighted ratings based on user similarity.
  -	Filters anime by selected genres.
  -	Returns top recommendations based on the weighted scores.

AnimeRecommenderApp Class: This class creates the GUI for the recommendation system: 
  -	Initializes the window with a title and size.
  -	Creates an entry field for the user ID.
  -	Creates checkboxes for genre selection.
  -	Adds a button to get recommendations.
  -	Creates a text area to display recommendations.

get_recommendations Method (in AnimeRecommenderApp): This method is called when the "Get Recommendations" button is clicked: 
  -	Retrieves the entered user ID and selected genres.
  -	Calls the get_recommendations function.
  -	Displays the recommendations in the text area, formatting the genres nicely.
  -	Handles errors for invalid user IDs or when the user is not found in the dataset.

Main Execution: 
Creates the tkinter root window, initializes the AnimeRecommenderApp, and starts the main event loop.
Creates a user-friendly interface for getting anime recommendations based on a user's ID and preferred genres. It uses collaborative filtering (via KNN) to find similar users and recommend anime that those similar users have rated highly, while also considering the user's genre preferences.
