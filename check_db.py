import mysql.connector
from datetime import date

conn = mysql.connector.connect(
    host='localhost', 
    user='root', 
    password='root', 
    database='smart_expenses_tracker'
)
cursor = conn.cursor(dictionary=True)

cursor.execute('SELECT id, username FROM users')
users = cursor.fetchall()
print('Users in database:')
for u in users:
    print(f'  ID: {u["id"]}, Username: {u["username"]}')

cursor.execute('SELECT id, user_id, title, amount, category, expense_date FROM expenses')
expenses = cursor.fetchall()
print(f'\nExpenses in database ({len(expenses)} total):')
for e in expenses:
    days_ago = (date.today() - e["expense_date"]).days
    print(f'  ID: {e["id"]}, User: {e["user_id"]}, {e["title"]}, ₹{e["amount"]}, {e["category"]}, Date: {e["expense_date"]} ({days_ago} days ago)')

today = date.today()
cursor.execute('SELECT COUNT(*) as cnt FROM expenses WHERE expense_date >= DATE_SUB(CURDATE(), INTERVAL 6 DAY)')
recent_count = cursor.fetchone()['cnt']
print(f'\nExpenses in last 7 days: {recent_count}')

cursor.close()
conn.close()
