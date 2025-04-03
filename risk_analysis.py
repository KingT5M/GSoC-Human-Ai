import pandas as pd
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from sklearn.feature_extraction.text import TfidfVectorizer
import matplotlib.pyplot as plt
import seaborn as sns

# Initialize VADER and TF-IDF
nltk.download('vader_lexicon')
sia = SentimentIntensityAnalyzer()

# Load the dataset
df = pd.read_csv("crisis_posts_with_comments.csv")

# Sentiment Classification using VADER
def get_sentiment(text):
    score = sia.polarity_scores(text)['compound']
    if score >= 0.05:
        return "Positive"
    elif score <= -0.05:
        return "Negative"
    else:
        return "Neutral"

df['Sentiment'] = df['content'].apply(get_sentiment)

# High-Risk Crisis Term Detection using TF-IDF
high_risk_terms = ["suicide", "kill myself", "end it all", "hopeless", "can't go on"]
tfidf = TfidfVectorizer()
X = tfidf.fit_transform(df['content'])
feature_names = tfidf.get_feature_names_out()

def detect_high_risk(text):
    text_vector = tfidf.transform([text])
    for term in high_risk_terms:
        if term in feature_names and text_vector[0, feature_names.tolist().index(term)] > 0:
            return True
    return False

# Categorizing Risk Levels
def categorize_risk(text):
    if detect_high_risk(text):
        return "High-Risk"
    elif "help" in text or "lost" in text:
        return "Moderate Concern"
    else:
        return "Low Concern"

df['Risk_Level'] = df['content'].apply(categorize_risk)

# Visualization
grouped = df.groupby(['Risk_Level', 'Sentiment']).size().unstack().fillna(0)

# Heatmap
plt.figure(figsize=(10, 5))
sns.heatmap(grouped, annot=True, fmt='.0f', cmap='coolwarm', linewidths=0.5)
plt.title("Crisis Risk vs Sentiment Analysis")
plt.xlabel("Sentiment")
plt.ylabel("Risk Level")
plt.savefig("heatmap_crisis_risk_vs_sentiment.png")  # Save heatmap
plt.show()

# Bar Chart
plt.figure(figsize=(10, 5))
grouped.plot(kind='bar', stacked=True, colormap='viridis')
plt.title("Distribution of Posts by Risk Level and Sentiment")
plt.xlabel("Risk Level")
plt.ylabel("Number of Posts")
plt.xticks(rotation=0)
plt.legend(title="Sentiment")
plt.savefig("bar_chart_risk_vs_sentiment.png")  # Save bar chart
plt.show()

# Save processed data
df.to_csv("classified_posts.csv", index=False)
print("Classification complete. Data saved as 'classified_posts.csv'.")
