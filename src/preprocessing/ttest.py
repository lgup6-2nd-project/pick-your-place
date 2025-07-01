import pymysql

conn = pymysql.connect(
    host="192.168.101.206", 
    port=3306,
    user="pypuser",
    password="pyppassword",
    database="pickyourplace-db"
)

cursor = conn.cursor()
cursor.execute("SHOW TABLES;")
print(cursor.fetchall())