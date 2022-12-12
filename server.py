# Import the Flask class from the flask module
from flask import Flask, request
# Import the datetime class from the datetime module
from datetime import datetime

# Create a Flask application instance
app = Flask(__name__)

# Define a route for the /log endpoint that only accepts POST requests


@app.route('/log', methods=['POST'])
def receive_log():
    # Get the current datetime
    now = datetime.now()
    # Define a filename for the log data based on the current datetime
    file_name = f"log_{now.year}_{now.month}_{now.day}_{now.hour}_{now.minute}_{now.second}.txt"
    # Get the log data from the request body
    log_data = request.data
    # Open the log file for writing in binary mode
    with open(file_name, "wb") as f:
        # Write the log data to the log file
        f.write(log_data)

    # Return 'OK' to indicate that the request was successful
    return 'OK'


# If the script is run directly, start the Flask application
if __name__ == '__main__':
    app.run()
