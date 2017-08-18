from shared import Database
import shared.models

db_name = input("Generate statistics for region: ")
db = Database(db_name)
for table in shared.models.Base.metadata.tables.values():
    print(f"Statistics for the {table.name} table.")
    total = db.query(table).count()
    for column in table.columns:
        print(f"{column.name} is used {db.query(table).filter(column!=None).count()} out of {total} times.")