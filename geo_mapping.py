import pandas as pd
import spacy
from geopy.geocoders import Nominatim
import folium
from folium.plugins import HeatMap
import matplotlib.pyplot as plt
import seaborn as sns

# Load the dataset (Classified crisis-related posts)
df = pd.read_csv("classified_posts.csv")

# Load NLP model for Named Entity Recognition (NER)
nlp = spacy.load("en_core_web_sm")

def extract_location(text):
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "GPE":  # Geopolitical entity (City, State, Country)
            return ent.text
    return None

df['Location'] = df['content'].apply(extract_location)
df = df.dropna(subset=['Location'])  # Keep only posts with detected locations

# Convert location names to coordinates
geolocator = Nominatim(user_agent="crisis_mapper")
def get_coordinates(location):
    try:
        geo = geolocator.geocode(location, timeout=10)
        if geo:
            return geo.latitude, geo.longitude
    except:
        return None
    return None

df['Coordinates'] = df['Location'].apply(get_coordinates)
df = df.dropna(subset=['Coordinates'])  # Remove rows with no coordinates
df[['Latitude', 'Longitude']] = pd.DataFrame(df['Coordinates'].tolist(), index=df.index)

# Print all locations with coordinates
all_locations = df[['Location', 'Latitude', 'Longitude']]
print("List of all locations included in the heatmap:")
print(all_locations.to_string(index=False))


# Generate Heatmap
m = folium.Map(location=[df['Latitude'].mean(), df['Longitude'].mean()], zoom_start=4)
HeatMap(df[['Latitude', 'Longitude']].values, radius=15).add_to(m)
m.save("crisis_heatmap.html")  # Save heatmap

# Top 5 Locations with Most Crisis Posts
top_locations = df['Location'].value_counts().nlargest(5)

# Bar chart for top 5 locations
plt.figure(figsize=(10, 6))
sns.barplot(x=top_locations.index, y=top_locations.values, hue=top_locations.index, palette="Blues", legend=False)
plt.title("Top 5 Locations with Most Crisis-Related Posts")
plt.xlabel("Location")
plt.ylabel("Number of Posts")
plt.xticks(rotation=45)
plt.savefig("top_5_crisis_locations.png")
plt.show()

# Save processed data
df.to_csv("geolocated_crisis_posts.csv", index=False)
print("Geolocation and mapping complete. Heatmap and location analysis generated.")
