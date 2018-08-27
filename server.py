from mongoengine import connect
from app import create_app
from constants import DATABASE_NAME, DATABASE_HOST, APP_HOST

if __name__ == '__main__':

    # Connect to the DB
    connect(DATABASE_NAME, host=DATABASE_HOST)

    # Run the server
    create_app().run(host=APP_HOST, debug=True)