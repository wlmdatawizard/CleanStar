-- Return column definitions for one required table without changing it.
-- Python supplies the fully qualified table name as a connector parameter:
-- cursor.execute(sql, (table_name,))
-- A missing or inaccessible table raises an error for Python to handle.
DESCRIBE TABLE IDENTIFIER(%s);
