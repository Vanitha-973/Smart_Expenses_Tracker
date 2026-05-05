from flask import current_app, g
import mysql.connector


def _connect(database=None):
    cfg = current_app.config
    return mysql.connector.connect(
        host=cfg["MYSQL_HOST"],
        user=cfg["MYSQL_USER"],
        password=cfg["MYSQL_PASSWORD"],
        database=database or cfg["MYSQL_DB"],
    )


def get_db():
    if "db" not in g:
        g.db = _connect()
    return g.db


def query_db(query, args=(), one=False):
    cursor = get_db().cursor(dictionary=True)
    cursor.execute(query, args)
    rows = cursor.fetchall()
    cursor.close()
    return (rows[0] if rows else None) if one else rows


def execute_db(query, args=()):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(query, args)
    conn.commit()
    last_id = cursor.lastrowid
    cursor.close()
    return last_id


def close_db(error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(app):
    with app.app_context():
        cfg = current_app.config
        admin_conn = mysql.connector.connect(
            host=cfg["MYSQL_HOST"],
            user=cfg["MYSQL_USER"],
            password=cfg["MYSQL_PASSWORD"],
        )
        admin_cursor = admin_conn.cursor()
        admin_cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{cfg['MYSQL_DB']}`")
        admin_cursor.close()
        admin_conn.close()

        conn = _connect()
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100) NOT NULL UNIQUE,
                email VARCHAR(150) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB;
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS expenses (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                title VARCHAR(150) NOT NULL,
                amount DECIMAL(10,2) NOT NULL,
                category VARCHAR(100) NOT NULL,
                expense_date DATE NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT fk_expenses_user
                    FOREIGN KEY (user_id) REFERENCES users(id)
                    ON DELETE CASCADE
            ) ENGINE=InnoDB;
            """
        )
        conn.commit()
        cursor.close()
        conn.close()
