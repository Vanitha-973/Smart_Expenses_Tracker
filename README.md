# Smart Expenses Tracker

A Flask + MySQL expense tracker with authentication, expense CRUD, weekly analytics, monthly summaries, and Chart.js visualizations.

## Database

- Host: `localhost`
- User: `root`
- Password: `root`
- Database: `smart_expenses_tracker`

The app creates the database and tables automatically on startup if the MySQL server allows the root login.

## Run

1. Install dependencies:
   - `pip install -r requirements.txt`
2. Start the app:
   - `python app.py`
3. Open the local Flask URL shown in the terminal.

## Main Routes

- `/register`
- `/login`
- `/logout`
- `/dashboard`
- `/add-expense`
- `/view-expenses`
- `/edit-expense/<id>`
- `/delete-expense/<id>`
- `/last-7-days`
- `/monthly-summary`
- `/chart-data`

## Copyright

© 2026 Smart Expenses Tracker. All rights reserved.
