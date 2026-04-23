from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import requests

app = Flask(__name__)

# --- 1. DATABASE CONFIGURATION ---
# This tells Flask to create a file called 'weather.db' in your folder
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
db = SQLAlchemy(app)

# --- 2. THE DATABASE MODEL (OOP Returns!) ---
# This Class defines the columns in our database table
class SearchHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city_name = db.Column(db.String(100), nullable=False)

# This automatically creates the weather.db file the first time you run the app
with app.app_context():
    db.create_all()


@app.route("/", methods=["GET", "POST"])
def home():
    # --- 3. READ FROM DATABASE ---
    # Fetch every search we've ever saved to show on the page
    past_searches = SearchHistory.query.all()

    if request.method == "POST":
        city = request.form.get("city").strip()
        
        # --- 4. WRITE TO DATABASE ---
        # Spawn a new Object and save it to the database
        new_search = SearchHistory(city_name=city)
        db.session.add(new_search)
        db.session.commit() # The "Save" button for the database
        
        # Update our list so the new search shows up immediately
        past_searches = SearchHistory.query.all()
        
        try:
            # (Your API Logic remains exactly the same!)
            geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&format=json"
            geo_data = requests.get(geo_url).json()

            if "results" in geo_data:
                location = geo_data["results"][0]
                lat, lon = location["latitude"], location["longitude"]
                official_name = location["name"]
                
                weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
                weather_data = requests.get(weather_url).json()
                
                temp = weather_data["current_weather"]["temperature"]
                wind = weather_data["current_weather"]["windspeed"]
                
                # Notice we are now passing 'history=past_searches' to Jinja
                return render_template("index.html", 
                                       city_name=official_name, 
                                       temp=temp, 
                                       wind=wind,
                                       history=past_searches)
            else:
                return render_template("index.html", error="City not found. Try again.", history=past_searches)
                
        except Exception:
            return render_template("index.html", error="Error connecting to the internet.", history=past_searches)

    # If it's a GET request, just load the page with the history
    return render_template("index.html", history=past_searches)

if __name__ == "__main__":
    app.run(debug=False)