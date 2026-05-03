from psycopg_pool import ConnectionPool

pool = ConnectionPool(
    conninfo="postgresql://postgres:StrongPasswordHere@localhost:5432/ocrdb",
    max_size=10
)
