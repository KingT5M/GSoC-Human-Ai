import praw
import pandas as pd
import re
import spacy
from dotenv import load_dotenv
import os
import logging
from concurrent.futures import ThreadPoolExecutor
import time
import prawcore

# Load credentials from credentials.env
load_dotenv("credentials.env")
nlp = spacy.load("en_core_web_sm")
logging.basicConfig(level=logging.INFO)

# Updated crisis-related keywords to identify relevant posts
CRISIS_KEYWORDS = [
    "depressed", "suicidal", "overwhelmed", "relapse",
    "addiction", "self harm", "mental breakdown", "panic attack",
    "hopeless", "crisis line", "anxious", "therapy",
    "burnout", "grief", "lonely"
]

# List of mental health-related subreddits to fetch posts from
SUBREDDITS = [
    "mentalhealth", "depression", "suicidewatch", "anxiety",
    "BipolarReddit", "offmychest", "MMFB", "ADHD", "BPD",
    "ptsd", "therapy", "mentalillness", "sad", "stopselfharm",
    "CPTSD", "traumatoolbox", "socialanxiety", "selfimprovement",
    "breakups", "stress", "emotionalabuse"
]

def get_reddit_client():
    """Initialize and return a Reddit client using environment variables."""
    return praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        user_agent=os.getenv("REDDIT_USER_AGENT"),
        username=os.getenv("REDDIT_USERNAME"),
        password=os.getenv("REDDIT_PASSWORD")
    )

def clean_text(text):
    """Cleans text by removing URLs, special characters, and normalizing text."""
    text = re.sub(r'http\S+', '', text)  # Remove URLs
    text = re.sub(r'[^A-Za-z\s]', '', text)  # Remove special characters
    text = re.sub(r'\s+', ' ', text).strip().lower()  # Normalize whitespace and lowercase
    doc = nlp(text)  # Apply NLP for lemmatization
    return " ".join([token.lemma_ for token in doc])

def fetch_posts_praw(reddit, subreddit, limit=100):
    """Fetch posts from a given subreddit and filter based on crisis-related keywords."""
    try:
        for submission in reddit.subreddit(subreddit).hot(limit=limit):
            pass  # Ensure subreddit is accessible
    except prawcore.exceptions.Forbidden:
        print(f"Skipping subreddit {subreddit}: Access denied")
        return []
    
    posts = []
    for submission in reddit.subreddit(subreddit).hot(limit=limit):
        if not submission.title or not submission.selftext:
            continue  # Skip posts without titles or text
        
        if any(kw in submission.title.lower() for kw in CRISIS_KEYWORDS):
            posts.append({
                "id": submission.id,
                "timestamp": submission.created_utc,
                "content": clean_text(submission.title + " " + (submission.selftext or "")),
                "likes": submission.score,
                "shares": submission.num_crossposts,
                "comments": submission.num_comments
            })
    
    return pd.DataFrame(posts)

def fetch_comments(reddit, post_id):
    """Fetch and clean comments from a given post."""
    submission = reddit.submission(id=post_id)
    submission.comments.replace_more(limit=None)  # Expand all comments
    return [clean_text(comment.body) for comment in submission.comments.list()]

def process_posts_with_comments(subreddits=SUBREDDITS, limit=100):
    """Fetch posts and their comments, then save to CSV."""
    reddit = get_reddit_client()
    end_time = time.time() + 3600  # Run for 1 hour

    # Check if previous data exists and load existing post IDs
    if os.path.exists("crisis_posts_with_comments.csv"):
        existing_df = pd.read_csv("crisis_posts_with_comments.csv")
        existing_ids = set(existing_df["id"])
    else:
        existing_ids = set()
    
    subreddit_index = 0
    total_new_posts = 0
    
    while time.time() < end_time:
        current_subreddit = subreddits[subreddit_index]
        logging.info(f"Fetching from subreddit: {current_subreddit}")
        
        posts = fetch_posts_praw(reddit, subreddit=current_subreddit, limit=limit)
        
        # Ensure posts are in DataFrame format
        df = pd.DataFrame(posts) if isinstance(posts, list) else posts
        
        if df.empty:
            logging.info(f"No new posts found in {current_subreddit}.")
            subreddit_index = (subreddit_index + 1) % len(subreddits)
            time.sleep(60)
            continue
        
        # Remove already processed posts
        df = df[~df["id"].isin(existing_ids)]
        
        num_new_posts = len(df)
        total_new_posts += num_new_posts
        
        if num_new_posts > 0:
            # Fetch comments using multithreading for efficiency
            with ThreadPoolExecutor(max_workers=5) as executor:
                df = df.copy()
                df.loc[:,"comments_text"] = list(executor.map(lambda pid: fetch_comments(reddit, pid), df["id"]))
            
            # Append new posts to CSV file
            df.to_csv("crisis_posts_with_comments.csv", mode="a", header=not os.path.exists("crisis_posts_with_comments.csv"), index=False)
            existing_ids.update(df["id"])
            
            logging.info(f"Fetched {num_new_posts} new posts from {current_subreddit}. Total collected: {total_new_posts}")
        else:
            logging.info(f"No new posts found in {current_subreddit}.")
        
        subreddit_index = (subreddit_index + 1) % len(subreddits)
        time.sleep(60)  # Pause before fetching the next subreddit
    
    logging.info(f"Script finished. Total new posts collected: {total_new_posts}")

if __name__ == "__main__":
    start_time = time.time()
    process_posts_with_comments()
    logging.info(f"Script completed in {time.time() - start_time:.2f} seconds")
