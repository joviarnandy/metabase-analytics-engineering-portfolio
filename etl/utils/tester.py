from etl.utils.db import get_engine
engine = get_engine()
with engine.connect() as conn:
      result = conn.execute(__import__('sqlalchemy').text('SELECT schema_name FROM information_schema.schemata ORDER BY schema_name'))
for row in result:
	print(row)