import mysql.connector
from werkzeug.security import generate_password_hash
from datetime import date

conn = mysql.connector.connect(host='localhost', user='root', password='root', database='smart_expenses_tracker')
cursor = conn.cursor(dictionary=True)

# Create or reuse a test user
password_hash = generate_password_hash('testpass123')
cursor.execute('SELECT id FROM users WHERE username = %s OR email = %s', ('john_doe', 'john@example.com'))
existing_user = cursor.fetchone()
if existing_user:
    user_id = existing_user['id']
    cursor.execute('UPDATE users SET password_hash = %s WHERE id = %s', (password_hash, user_id))
else:
    cursor.execute('INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)',
                   ('john_doe', 'john@example.com', password_hash))
    conn.commit()
    cursor.execute('SELECT LAST_INSERT_ID() as id')
    user_id = cursor.fetchone()['id']
conn.commit()
print(f'Test User Created - ID: {user_id}')

# Add some expenses for this user
expenses_data = [
    ('Lunch at Restaurant', 350, 'Food', date.today(), 'Lunch with colleagues'),
    ('Taxi to Office', 150, 'Travel', date.today(), None),
    ('Book Purchase', 500, 'Shopping', date.today(), 'Python Programming')
]

for title, amount, category, exp_date, description in expenses_data:
    cursor.execute('''INSERT INTO expenses (user_id, title, amount, category, expense_date, description) 
                      VALUES (%s, %s, %s, %s, %s, %s)''',
                   (user_id, title, amount, category, exp_date, description))
conn.commit()

# Verify data is stored correctly
cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
user = cursor.fetchone()
print(f'\nUser Data Stored:')
print(f'  ID: {user["id"]}')
print(f'  Username: {user["username"]}')
print(f'  Email: {user["email"]}')
print(f'  Created: {user["created_at"]}')

cursor.execute('SELECT * FROM expenses WHERE user_id = %s', (user_id,))
expenses = cursor.fetchall()
print(f'\nExpenses for user_id {user_id}:')
for exp in expenses:
    print(f'  - {exp["title"]}: ₹{exp["amount"]} ({exp["category"]}) on {exp["expense_date"]}')

# Verify total
cursor.execute('SELECT SUM(amount) as total FROM expenses WHERE user_id = %s', (user_id,))
total = cursor.fetchone()
print(f'\nTotal Spending: ₹{total["total"]}')

# Verify weekly expenses
cursor.execute('''SELECT SUM(amount) as weekly_total FROM expenses 
                  WHERE user_id = %s AND expense_date >= CURDATE() - INTERVAL 6 DAY''', (user_id,))
weekly = cursor.fetchone()
print(f'Last 7 Days Spending: ₹{weekly["weekly_total"]}')

# Show all users and linked expense summary (so user_id 3 is visible too)
cursor.execute('SELECT id, username, email, created_at FROM users ORDER BY id')
all_users = cursor.fetchall()
print('\nAll Users in Database:')
for row in all_users:
    print(f'  - ID {row["id"]}: {row["username"]} ({row["email"]})')

cursor.execute('''SELECT user_id, COUNT(*) AS count, COALESCE(SUM(amount), 0) AS total
                  FROM expenses
                  GROUP BY user_id
                  ORDER BY user_id''')
expense_summary = cursor.fetchall()
print('\nExpense Summary by User ID:')
for row in expense_summary:
    print(f'  - user_id {row["user_id"]}: {row["count"]} expenses, ₹{row["total"]}')

cursor.close()
conn.close()
print('\n✓ All data successfully stored in MySQL database with user_id linking!')
print('✓ Database is ready for the web application!')
