# Taxi-Fare-Prediction
The Intelligent Taxi Fare Prediction System solves problems with inaccurate fares by using real-time factors like traffic, weather, and demand. It provides fair and clear pricing, making it easy and reliable for passengers and drivers, improving trust and satisfaction for everyone

Requirements

#### 1. *Applications and Environments*

- *Python 3.8+*: Ensure you have Python installed for running the backend scripts.
  - Download from [Python official website](https://www.python.org/downloads/).

- *Flask Framework*: For creating the web application (backend).
  - Install using pip:
    bash
    pip install Flask
    

- *HTML, CSS, JavaScript*: Used for the front end of the web application to build user interfaces.

#### 2. *Libraries and Dependencies*

Make sure to install the following Python libraries:

- *Flask*: Web framework to run the backend.
  bash
  pip install Flask
  

- *Pandas*: Data manipulation library.
  bash
  pip install pandas
  

- *Scikit-learn*: For machine learning algorithms like Linear Regression, Decision Trees, etc.
  bash
  pip install scikit-learn
  

- *OpenWeatherMap API*: To fetch weather data for predictions. You need an API key from [OpenWeatherMap](https://openweathermap.org/api).
  - Install requests for API interaction:
    bash
    pip install requests
    

- *OpenCage API*: Used for geocoding pickup and dropoff locations using latitude and longitude. Obtain an API key from [OpenCage Data](https://opencagedata.com/).
  - Use requests to call this API.

- *TomTom Traffic API*: To fetch real-time traffic data.
  - You will need an API key from [TomTom Developer](https://developer.tomtom.com/).
  - Install requests:
    bash
    pip install requests
    

- *NumPy*: For handling numerical data.
  bash
  pip install numpy
  

- *XGBoost*: For the Gradient Boosting models.
  bash
  pip install xgboost
  

#### 3. *APIs*

- *OpenWeatherMap API*: Used for fetching weather data based on the pickup location.
- *OpenCage Geocoding API*: For converting locations (addresses) to latitude and longitude and vice versa.
- *TomTom Traffic API*: To fetch real-time traffic predictions.
  
Make sure you add your API keys directly in the code.

#### 4. *Modeling Tools*

- *Linear Regression, Random Forest, Gradient Boosting, and XGBoost*: Implemented for fare prediction based on historical data.
  
#### 5. *Data Sources*

- Historical taxi trip data, including the following features:
  - pickup_latitude
  - dropoff_latitude
  - pickup_longitude
  - dropoff_longitude
  - trip_distance
  - passenger_count
  - fare_amount
  
This data can be stored as CSV files or in a database.

#### 6. *Running the Application*

1. *Clone the repository*:
   bash
   git clone <repository-url>
   

2. *Set up a virtual environment (optional but recommended)*:
   bash
   python -m venv venv
   source venv/bin/activate  # For Linux/Mac
   venv\Scripts\activate     # For Windows
   

3. *Install the required libraries*:
   bash
   pip install -r requirements.txt
   

4. *Set up your API keys*:
   - OpenWeatherMap API Key
   - OpenCage API Key
   - TomTom Traffic API Key
   
   Add these keys in the code wherever API calls are made.

5. *Run the Flask web application*:
   bash
   python app.py
   

6. *Access the web application*:
   Open a browser and go to http://127.0.0.1:5000.
