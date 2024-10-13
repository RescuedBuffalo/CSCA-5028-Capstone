from app import create_app
import os

config_name = os.getenv('FLASK_CONFIG')
app = create_app('development')  # You can change 'development' to 'production' when deploying

if __name__ == '__main__':
    app.run(debug=True)