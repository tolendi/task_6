import os
from flask import Flask, render_template, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
import sys

app = Flask(__name__)

# Тщательно проверьте пароль и порт (5432 — стандарт для Postgres)
DB_CONFIG = {
    "dbname": "fakerdb",
    "user": "postgres",
    "password": "qwerty123", 
    "host": "127.0.0.1",
    "port": 5432
}

def get_db_data(locale, seed, batch_idx):
    try:
        # Пытаемся взять URL базы из переменной окружения Render
        db_url = os.environ.get('DATABASE_URL')
        
        if db_url:
            # Если мы на Render
            conn = psycopg2.connect(db_url)
        else:
            # Если мы запускаем локально на компьютере
            conn = psycopg2.connect(
                dbname="fakerdb",
                user="postgres",
                password="qwerty123", 
                host="127.0.0.1",
                port=5432
            )
            
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Ваш SQL запрос остается прежним
            cur.execute(
                "SELECT idx, full_name, address, email, phone, geo, height_cm FROM faker.get_batch(%s, %s, %s, 10)",
                (locale, seed, batch_idx)
            )
            return cur.fetchall()
    except Exception as e:
        print(f"--- DATABASE ERROR: {e} ---")
        return []
    
    finally:
        # Тот самый обязательный блок finally
        if conn:
            conn.close()

@app.route("/")
def index():
    locale = request.args.get("locale", "en_US")
    seed = int(request.args.get("seed", 123))
    batch = int(request.args.get("batch", 0))

    offset = batch_number * 10
    
    rows = get_db_data(locale, seed, batch)
    return render_template("index.html", rows=rows, locale=locale, seed=seed, batch=batch)

if __name__ == "__main__":
    # Render сам подставит нужный порт через переменную окружения PORT
    port = int(os.environ.get("PORT", 5000))

    app.run(debug=False, host="0.0.0.0", port=port)
