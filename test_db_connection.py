import os

from dotenv import load_dotenv
from sqlalchemy import URL, create_engine, text

load_dotenv()

database_url = URL.create(
    drivername="mysql+pymysql",
    username=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD"),
    host=os.getenv("MYSQL_HOST", "127.0.0.1"),
    port=int(os.getenv("MYSQL_PORT", "3306")),
    database=os.getenv("MYSQL_DATABASE", "retail_support"),
)

engine = create_engine(database_url, pool_pre_ping=True)

try:
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT DATABASE(), VERSION()")
        )
        database, version = result.fetchone()

        print("MySQL connection successful!")
        print("Database:", database)
        print("MySQL version:", version)

except Exception as error:
    print("MySQL connection failed.")
    print(type(error).__name__, str(error))

finally:
    engine.dispose()
