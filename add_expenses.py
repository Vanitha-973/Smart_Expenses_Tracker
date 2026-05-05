import mysql.connector
from datetime import date, timedelta

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='root',
    database='smart_expenses_tracker'
)
cursor = conn.cursor()

# Get Vanitha's user_id
cursor.execute("SELECT id FROM users WHERE username = 'Vanitha'")
user_id = cursor.fetchone()[0]
print(f'Adding expenses for user_id: {user_id} (Vanitha)')

# Add expenses for last 7 days
expenses = [
    ('Coffee', 80, 'Food', date.today(), 'Morning coffee'),
    ('Groceries', 1200, 'Shopping', date.today() - timedelta(days=1), 'Weekly groceries'),
    ('Electricity Bill', 500, 'Utilities', date.today() - timedelta(days=2), 'Monthly bill'),
    ('Movie Tickets', 400, 'Entertainment', date.today() - timedelta(days=3), 'Cinema'),
    ('Fuel', 600, 'Travel', date.today() - timedelta(days=4), 'Petrol'),
    ('Dinner', 350, 'Food', date.today() - timedelta(days=5), 'Restaurant'),
    ('Gym Membership', 1000, 'Health', date.today() - timedelta(days=6), 'Monthly'),
]

for title, amount, category, exp_date, description in expenses:
    cursor.execute('''INSERT INTO expenses 
                      (user_id, title, amount, category, expense_date, description) 
                      VALUES (%s, %s, %s, %s, %s, %s)''',
                   (user_id, title, amount, category, exp_date, description))
    print(f'  Added: {title} (₹{amount}) on {exp_date}')

conn.commit()
cursor.close()
conn.close()

print(f'\n✓ Added 7 expenses for Vanitha in the last 7 days!')
