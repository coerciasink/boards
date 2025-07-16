import psycopg2

conn = psycopg2.connect(
    dbname="boards",
    user="postgres",
    password="password",
    host="localhost"
)
cursor = conn.cursor()
cursor.execute("SELECT * FROM image_cache LIMIT 10;")
rows = cursor.fetchall()

for row in rows:
    print(row)

cursor.close()
conn.close()
