# Data Barn Flask App

A Flask-based app for viewing aggregate win statistics using the data available in the free [Keeneland handicapping database](http://apps.keeneland.com/awstats/Default.asp, 'Keeneland handicapping database').  Users can currently view top all-time wins of interest to handicappers, including wins by jockeys, trainers, and sires.  These data are further presented in categories such as track surface.

Data is stored in a PostgreSQL database.  User registration and authentication is supported by werkzeug for encryption and flask_login for maintaining user authentication per session.  Interaction with the database is done using SQLalchemy.  The web interface requires Bootstrap 5.3.2 (the required CSS and JavaScript files are uploaded in data_barn/static for convenience), as well as WTForms.

## Project Structure

```
├── config.py
├── data
│   ├── keeneland.csv
│   ├── thoroughbreds_schema.sql
│   └── thoroughbreds_with_data.sql
├── data_barn
│   ├── __init__.py
│   ├── dashboard.py
│   ├── db_handler.py
│   ├── dbarn_forms.py
│   ├── helpers.py
│   ├── models.py
│   ├── static
│   │   ├── bootstrap.bundle.js
│   │   ├── bootstrap.bundle.min.js
│   │   ├── bootstrap.min.css
│   │   ├── fromsource.css
│   │   ├── login.css
│   │   └── popper.min.js
│   ├── templates
│   │   ├── auth
│   │   │   ├── login.html
│   │   │   └── register.html
│   │   ├── base.html
│   │   ├── main
│   │   │   ├── index.html
│   │   │   ├── jockeys.html
│   │   │   ├── sires.html
│   │   │   └── trainers.html
│   │   └── navbar.html
│   └── user_auth.py
├── documentation
│   ├── thoroughbred_api.pgerd
├── load_data.py
└── requirements.txt
```
### Required to Run App
`config.py` and the files in the `data_barn` directory are required for the app.  **Please note:*** The app also requires database migrations, which will need to be initialized with the database as part of app setup.

### Misc. and Helpers
Files in the `data` folder include the original Keeneland data in a CSV file and two SQL files, one with data and one with schemas only that can be used to recreate the database.  The `load_data.py` file included contains a helper class to batch load the original CSV file into an existing database.  This was meant to be used from within the Flask shell.

### Documentation
The ERD for the thoroughbred_api database is included (generated by PGAdmin).


