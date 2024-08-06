import os
from transformers import pipeline

# Define paths for saving the models
fill_mask_path = "./app/models/fill-mask"
sentiment_analysis_path = "./app/models/sentiment-analysis"

# Create directories if they don't exist
os.makedirs(fill_mask_path, exist_ok=True)
os.makedirs(sentiment_analysis_path, exist_ok=True)

# Download and save the fill-mask model
fill_mask = pipeline("fill-mask")
fill_mask.save_pretrained(fill_mask_path)

# Download and save the sentiment-analysis model
sentiment_analysis = pipeline("sentiment-analysis")
sentiment_analysis.save_pretrained(sentiment_analysis_path)

print("Models have been downloaded and saved locally.")
