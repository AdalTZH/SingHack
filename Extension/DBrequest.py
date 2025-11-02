import psycopg2

conn = psycopg2.connect(
    host="hackathon-db.ceqjfmi6jhdd.ap-southeast-1.rds.amazonaws.com",
    port=5432,
    database="hackathon_db",
    user="hackathon_user",
    password="Hackathon2025!"
)

cur = conn.cursor()
cur.execute("SET search_path TO hackathon;")
cur.execute("SELECT * FROM claims LIMIT 10;")
rows = cur.fetchall()

for row in rows:
    print(row)

cur.close()
conn.close()
