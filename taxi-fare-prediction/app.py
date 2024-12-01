from flask import Flask, render_template, request
import mysql.connector
import requests
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, r2_score

app = Flask(__name__)

# OpenWeather API key, OpenCage API key, and Mapbox token
OPENWEATHER_API_KEY = '108b3fc52f3399e47ac637e6ec168b01'
MAPBOX_ACCESS_TOKEN = 'pk.eyJ1Ijoia2FhbGFrYXJpa2FsYW4iLCJhIjoiY20yYjl2dzdqMHAydjJ3c2ZjYng1d2Q3YyJ9._iDR65eR_qkzbtrrcRjqag'
OPENCAGE_API_KEY = '03bc532bb610454f8196da6bbeee8ab7'  # Your OpenCage API key

# MySQL connection configuration
db_config = {
    'host': 'localhost',  # Change to your host, e.g., 'localhost' or an IP address
    'user': 'root',  # Your MySQL username
    'password': 'Karthi@2004',  # Your MySQL password
    'database': 'fare_prediction'  # Your database name
}

# Function to get a MySQL connection
def get_db_connection():
    connection = mysql.connector.connect(**db_config)
    return connection

# Load the dataset
dataset_path = r"C:\Users\Admin\Documents\ML lab\CAT-2\Taxi-fare Prediction\Tamil_nadu_taxi_trips_.csv"
data = pd.read_csv(dataset_path)

# Calculate fare per km for each vehicle type
data['Fare_per_km'] = data['Fare_INR'] / data['Distance_km']

# Prepare the feature set (distance, vehicle type) and target (fare)
X = data[['Distance_km', 'Vehicle_Type']]  # Removed Weather_Condition as we will get it from API
y = data['Fare_INR']

# Encode the 'Vehicle_Type' using one-hot encoding (pandas' get_dummies)
X_encoded = pd.get_dummies(X, columns=['Vehicle_Type'], drop_first=True)

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X_encoded, y, test_size=0.2, random_state=42)

# Initialize models
models = {
    'Gradient Boosting': GradientBoostingRegressor(n_estimators=100, random_state=42)
}

# Train and evaluate models
best_model = None
best_mse = float('inf')
best_r2 = 0
best_model_name = ""

for name, model in models.items():
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    
    # Calculate performance metrics
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    print(f"{name}:")
    print(f"  R² Score: {r2:.4f}")
    print(f"  Mean Squared Error (MSE): {mse:.4f}\n")
    

# Define base fare amounts for each vehicle type
BASE_FARE = {
    'SUV': 14.88,       # Base fare in INR for SUV
    'Hatchback': 14.98, # Base fare in INR for Hatchback
    'Sedan': 14.98,      # Base fare in INR for Sedan
    'Mini Van': 15.10,  # Base fare in INR for Mini Van
    'Auto': 14.82   # Base fare in INR for Auto
}

@app.route('/')
def index():
    return render_template('index.html', mapbox_access_token=MAPBOX_ACCESS_TOKEN)

@app.route('/predict', methods=['POST'])
def predict():
    # Retrieve form data
    pickup_location = request.form['pickup_location']
    dropoff_location = request.form['dropoff_location']
    vehicle_type = request.form['vehicle_type']  # Assuming vehicle type is selected in the form
    
    # Fetch weather data for pickup and dropoff locations
    area_weather_data = get_weather_data(pickup_location)
    dropoff_area_weather_data = get_weather_data(dropoff_location)

    pickup_coords = get_coords_from_location(pickup_location)
    dropoff_coords = get_coords_from_location(dropoff_location)

    # Get multiple route data
    route_data = get_route_data(pickup_coords, dropoff_coords)

    # Get the distance for the first route for prediction
    distance_km = route_data[0]['distance'] if route_data else 0

    # Extract weather information for prediction
    pickup_temp = area_weather_data['main']['temp'] if 'main' in area_weather_data else 0
    pickup_humidity = area_weather_data['main']['humidity'] if 'main' in area_weather_data else 0

    # Predict fare using distance, vehicle type, and weather data
    predicted_fare = predict_fare(distance_km, vehicle_type, pickup_temp, pickup_humidity, pickup_location, dropoff_location)

    # Prepare climate information for display
    pickup_climate_info = f"Temperature: {pickup_temp} °C, Condition: {area_weather_data['weather'][0]['description']}" if 'main' in area_weather_data else 'N/A'
    
    # Extract relevant information for dropoff weather
    dropoff_temp = dropoff_area_weather_data['main']['temp'] if 'main' in dropoff_area_weather_data else 0
    dropoff_humidity = dropoff_area_weather_data['main']['humidity'] if 'main' in dropoff_area_weather_data else 0
    dropoff_climate_info = f"Temperature: {dropoff_temp} °C, Condition: {dropoff_area_weather_data['weather'][0]['description']}" if 'main' in dropoff_area_weather_data else 'N/A'

    # Find the shortest route data
    shortest_route = min(route_data, key=lambda x: x['distance']) if route_data else None

    if shortest_route:
        shortest_distance = shortest_route['distance']
        shortest_duration = shortest_route['duration']
    else:
        shortest_distance = 0
        shortest_duration = 0

    # Format duration to display in hours if it exceeds 60 minutes
    if shortest_duration >= 60:
        shortest_duration_hours = round(shortest_duration / 60, 2)
        duration_display = f"{shortest_duration_hours} hours"
    else:
        duration_display = f"{shortest_duration} minutes"

    # Store results in the MySQL database
    connection = get_db_connection()
    cursor = connection.cursor()

    # Insert the result into the 'fare_predictions' table
    insert_query = """
    INSERT INTO fare_predictions 
    (pickup_location, dropoff_location, distance, duration, 
    pickup_temperature, pickup_condition, dropoff_temperature, dropoff_condition, total_fare) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    cursor.execute(insert_query, (
        pickup_location, 
        dropoff_location, 
        shortest_distance, 
        shortest_duration, 
        pickup_temp, 
        area_weather_data['weather'][0]['description'] if 'main' in area_weather_data else 'N/A',
        dropoff_temp,
        dropoff_area_weather_data['weather'][0]['description'] if 'main' in dropoff_area_weather_data else 'N/A',
        predicted_fare
    ))

    connection.commit()
    cursor.close()
    connection.close()

    # Pass data to the template
    return render_template('result.html',
                           fare=predicted_fare,
                           pickup_climate_info=pickup_climate_info,
                           dropoff_climate_info=dropoff_climate_info,
                           pickup_location=pickup_location,
                           dropoff_location=dropoff_location,
                           shortest_distance=shortest_distance,
                           duration_display=duration_display,
                           pickup_coords=pickup_coords,
                           dropoff_coords=dropoff_coords,
                           route_data=route_data,
                           mapbox_access_token=MAPBOX_ACCESS_TOKEN)


def get_weather_data(location):
    # Fetch weather data for the area (could be city level)
    url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={OPENWEATHER_API_KEY}&units=metric"
    response = requests.get(url)
    return response.json()

def get_coords_from_location(location):
    url = f"https://api.opencagedata.com/geocode/v1/json?q={location}&key={OPENCAGE_API_KEY}"
    response = requests.get(url)
    data = response.json()
    
    if data and 'results' in data and len(data['results']) > 0:
        geometry = data['results'][0]['geometry']
        return {'lat': geometry['lat'], 'lng': geometry['lng']}
    return {'lat': 0, 'lng': 0}

import heapq

def dijkstra(graph, start):
    # Create a priority queue
    priority_queue = []
    heapq.heappush(priority_queue, (0, start))  # (distance, node)
    
    # Initialize distances and the path dictionary
    distances = {node: float('infinity') for node in graph}
    distances[start] = 0
    shortest_path = {node: None for node in graph}

    while priority_queue:
        current_distance, current_node = heapq.heappop(priority_queue)

        # Nodes can only get added once to the priority queue
        if current_distance > distances[current_node]:
            continue

        for neighbor, weight in graph[current_node].items():
            distance = current_distance + weight

            # Only consider this new path if it's better
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                shortest_path[neighbor] = current_node
                heapq.heappush(priority_queue, (distance, neighbor))

    return distances, shortest_path


def get_route_data(pickup_coords, dropoff_coords):
    # Fetch traffic-aware route data from Mapbox
    url = (f"https://api.mapbox.com/directions/v5/mapbox/driving-traffic/"
           f"{pickup_coords['lng']},{pickup_coords['lat']};{dropoff_coords['lng']},{dropoff_coords['lat']}"
           f"?geometries=geojson&access_token={MAPBOX_ACCESS_TOKEN}&alternatives=true")
    
    response = requests.get(url)
    data = response.json()

    if data and 'routes' in data and len(data['routes']) > 0:
        routes = []
        for route in data['routes']:
            routes.append({
                'distance': round(route['distance'] / 1000, 2),  # Convert meters to kilometers
                'duration': round(route['duration'] / 60, 2),     # Convert seconds to minutes
                'geometry': route['geometry']  # Store the route geometry if needed
            })
        return routes
    return []


def predict_fare(distance_km, vehicle_type, temperature, humidity, pickup_location, dropoff_location):
    # Base fare based on vehicle type
    base_fare = BASE_FARE.get(vehicle_type, 0)  # Default to 0 if vehicle type is not found

    # Determine fare per kilometer based on weather condition
    if temperature < 10:
        fare_per_km = 12  # Increased fare due to cold weather
    elif temperature > 35:
        fare_per_km = 15  # Increased fare due to hot weather
    elif humidity > 80:
        fare_per_km = 14  # Increased fare due to high humidity
    else:
        fare_per_km = 10  # Normal fare

    # Calculate the predicted fare based on distance
    predicted_fare = base_fare + (distance_km * fare_per_km)

    # Additional adjustments based on pickup and dropoff location (optional)
    if pickup_location in ['City Center', 'Airport']:  # Example for premium pickup locations
        predicted_fare += 20  # Additional fee for high-demand areas
    if dropoff_location in ['City Center', 'Airport']:
        predicted_fare += 20  # Additional fee for high-demand areas

    return round(predicted_fare, 2)


if __name__ == '__main__':
    app.run(debug=True)