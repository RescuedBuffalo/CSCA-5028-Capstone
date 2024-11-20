from app import create_app
import os
from dotenv import load_dotenv

load_dotenv('.env')

config_name = os.getenv('FLASK_CONFIG')
app = create_app(config_name=config_name)

if __name__ == '__main__':
    app.run(debug=(config_name != 'production'))