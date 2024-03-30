from flask import Flask
from py_eureka_client import eureka_client

app = Flask(__name__)

# Eureka server URL
eureka_server = "http://localhost:8761/eureka/"

# The name of your application as registered in Eureka
app_name = "tts-service"

# The port at which your Flask application will be accessible
port = 5000

eureka_client.init(eureka_server=eureka_server,
                   app_name=app_name,
                   instance_port=port)


@app.route('/')
def hello_world():
    return 'Hello, World!'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)
