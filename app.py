from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# This route handles both viewing the page (GET) and submitting the form (POST)
@app.route("/", methods=["GET", "POST"])
def home():
    # If they just loaded the page, show the empty form
    if request.method == "GET":
        return render_template("index.html")
    
    # If they clicked 'Search', grab what they typed into the HTML input box
    if request.method == "POST":
        city = request.form.get("city")
        
        try:
            # 1. Geocoding API
            geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&format=json"
            geo_data = requests.get(geo_url).json()

            if "results" in geo_data:
                location = geo_data["results"][0]
                lat, lon = location["latitude"], location["longitude"]
                official_name = location["name"]
                
                # 2. Weather API
                weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
                weather_data = requests.get(weather_url).json()
                
                temp = weather_data["current_weather"]["temperature"]
                wind = weather_data["current_weather"]["windspeed"]
                
                # Render the HTML page, but inject our Python variables into the Jinja placeholders!
                return render_template("index.html", 
                                       city_name=official_name, 
                                       temp=temp, 
                                       wind=wind)
            else:
                return render_template("index.html", error="City not found. Try again.")
                
        except Exception:
            return render_template("index.html", error="Error connecting to the internet.")

# This starts the server
if __name__ == "__main__":
    app.run(debug=True)