import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
import tkinter as tk
from tkinter import ttk, messagebox

print("Loading data...")
ratings_df = pd.read_csv('C:/Users/avi11/Downloads/Anime/animelist.csv')
anime_df = pd.read_csv('C:/Users/avi11/Downloads/Anime/anime.csv')

print("Preprocessing data...")
ratings_df = ratings_df[ratings_df['rating'] != 0]
ratings_df = ratings_df.dropna(subset=['user_id', 'anime_id', 'rating'])

anime_id_map = {id: idx for idx, id in enumerate(ratings_df['anime_id'].unique())}
ratings_df['anime_idx'] = ratings_df['anime_id'].map(anime_id_map)

user_id_map = {id: idx for idx, id in enumerate(ratings_df['user_id'].unique())}
ratings_df['user_idx'] = ratings_df['user_id'].map(user_id_map)

print("Creating sparse matrix...")
sparse_matrix = csr_matrix((ratings_df['rating'], (ratings_df['user_idx'], ratings_df['anime_idx'])))

print("Fitting KNN model...")
model_knn = NearestNeighbors(metric='cosine', algorithm='brute', n_neighbors=20, n_jobs=-1)
model_knn.fit(sparse_matrix)

all_genres = set()
for genres in anime_df['Genres'].dropna():
    all_genres.update(genre.strip() for genre in genres.split(','))
all_genres = sorted(list(all_genres))

def get_recommendations(user_id, selected_genres, n_recommendations=5):
    if user_id not in user_id_map:
        raise KeyError("User ID not found in the dataset.")
    
    user_idx = user_id_map[user_id]
    distances, indices = model_knn.kneighbors(sparse_matrix[user_idx], n_neighbors=20+1)
    
    similar_users = indices.flatten()[1:]
    user_distances = distances.flatten()[1:]
    
    similar_user_ratings = sparse_matrix[similar_users]
    weighted_ratings = similar_user_ratings.multiply(1 / (user_distances + 1e-8)[:, np.newaxis])
    
    recommendation_scores = weighted_ratings.sum(axis=0) / (1 / (user_distances + 1e-8)).sum()
    recommendation_scores = recommendation_scores.A1

    genre_mask = anime_df['Genres'].apply(lambda x: any(genre in str(x) for genre in selected_genres))
    filtered_anime = anime_df[genre_mask]

    filtered_anime_idx = np.array([anime_id_map.get(aid, -1) for aid in filtered_anime['MAL_ID']])
    valid_indices = filtered_anime_idx != -1
    filtered_anime_idx = filtered_anime_idx[valid_indices]
    filtered_anime = filtered_anime[valid_indices]
    
    if len(filtered_anime_idx) == 0:
        return pd.DataFrame(columns=['MAL_ID', 'Name', 'Score', 'Genres'])

    filtered_scores = recommendation_scores[filtered_anime_idx]
    top_indices = filtered_scores.argsort()[-n_recommendations:][::-1]
    
    recommended_anime = filtered_anime.iloc[top_indices]
    
    return recommended_anime[['MAL_ID', 'Name', 'Score', 'Genres']]

class AnimeRecommenderApp:
    def __init__(self, master):
        self.master = master
        master.title("Anime Recommender")
        master.geometry("600x400")

        # User ID
        self.user_id_label = ttk.Label(master, text="Enter User ID:")
        self.user_id_label.pack(pady=5)
        self.user_id_entry = ttk.Entry(master)
        self.user_id_entry.pack(pady=5)

        self.genre_label = ttk.Label(master, text="Select Genres:")
        self.genre_label.pack(pady=5)
        self.genre_frame = ttk.Frame(master)
        self.genre_frame.pack(pady=5)
        self.genre_vars = []
        for i, genre in enumerate(all_genres):
            var = tk.BooleanVar()
            cb = ttk.Checkbutton(self.genre_frame, text=genre, variable=var)
            cb.grid(row=i//3, column=i%3, sticky='w')
            self.genre_vars.append((genre, var))

        self.recommend_button = ttk.Button(master, text="Get Recommendations", command=self.get_recommendations)
        self.recommend_button.pack(pady=10)

        self.recommendations_text = tk.Text(master, height=10, width=70)
        self.recommendations_text.pack(pady=10)

    def get_recommendations(self):
        try:
            user_id = int(self.user_id_entry.get())
            selected_genres = [genre for genre, var in self.genre_vars if var.get()]
            
            if not selected_genres:
                messagebox.showwarning("Warning", "Please select at least one genre.")
                return
            
            recommendations = get_recommendations(user_id, selected_genres)
            
            self.recommendations_text.delete('1.0', tk.END)
            if recommendations.empty:
                self.recommendations_text.insert(tk.END, "No recommendations found for the selected genres.")
            else:
                for _, row in recommendations.iterrows():
                    self.recommendations_text.insert(tk.END, f"Name: {row['Name']}\n")
                    self.recommendations_text.insert(tk.END, f"Score: {row['Score']}\n")
                    
                    genres = row['Genres'].split(',')
                    formatted_genres = ', '.join(genre.strip() for genre in genres[:5])  # Limit to 5 genres
                    if len(genres) > 5:
                        formatted_genres += ", ..."
                    
                    self.recommendations_text.insert(tk.END, f"Genres: {formatted_genres}\n\n")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid User ID.")
        except KeyError:
            messagebox.showerror("Error", "User ID not found in the dataset.")

print("Initializing GUI...")
root = tk.Tk()
app = AnimeRecommenderApp(root)
root.mainloop()

#there is a slight issue in the output of the tkinter window
