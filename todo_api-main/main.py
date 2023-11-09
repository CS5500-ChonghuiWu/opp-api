from fastapi import FastAPI

from models import models
from db.database import engine
from routers import auth, todos, admin
from routers.payment import router as payment_router
from routers.generics import router as generics_router
import sqlite3

# Connect to SQLite3 database. This will create the file if it does not exist.
conn = sqlite3.connect('my_database.db')

cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    amount DECIMAL(10, 2),
    status TEXT,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')
cursor.execute('''
INSERT INTO transactions (user_id, amount, status) VALUES (?,?,?)
''', (123, 200.00, 'processed'))
conn.commit()
cursor.execute('SELECT * FROM transactions')
rows = cursor.fetchall()
for row in rows:
    print(row)
conn.close()


# application
app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

# sets up database defined in engine
models.Base.metadata.create_all(bind=engine)

# Set API endpoints on router
app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(generics_router)
app.include_router(payment_router)