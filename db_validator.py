import os
import pandas as pd
from sqlalchemy import create_engine, inspect, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_db_structure(db_url, db_label):
    """
    Connects to a database and retrieves table structure information.
    """
    try:
        engine = create_engine(db_url)
        # Test connection
        with engine.connect() as conn:
            pass
            
        inspector = inspect(engine)
        
        tables_data = []
        
        # Get all table names
        table_names = inspector.get_table_names()
        
        print(f"Connected to {db_label}. Found {len(table_names)} tables.")
        
        for table_name in table_names:
            columns = inspector.get_columns(table_name)
            for column in columns:
                tables_data.append({
                    "Database": db_label,
                    "Table": table_name,
                    "Column": column['name'],
                    "Type": str(column['type']),
                    "Nullable": column['nullable'],
                    "Default": str(column.get('default', ''))
                })
                
        return tables_data
    except Exception as e:
        print(f"Error connecting to {db_label}: {e}")
        return []

def compare_databases(df1, df2):
    """
    Compares DB1 (Master) with DB2 and returns a DataFrame of differences.
    Focuses on what is missing or different in DB2 compared to DB1.
    """
    diffs = []

    if df1.empty:
        return pd.DataFrame()

    # Create dictionaries for easier lookup: Table -> {Column -> RowData}
    def create_lookup(df):
        lookup = {}
        if df.empty:
            return lookup
        for _, row in df.iterrows():
            table = row['Table']
            col = row['Column']
            if table not in lookup:
                lookup[table] = {}
            lookup[table][col] = row
        return lookup

    db1_lookup = create_lookup(df1)
    db2_lookup = create_lookup(df2)

    # 1. Check Tables
    db1_tables = set(db1_lookup.keys())
    db2_tables = set(db2_lookup.keys())

    # Tables in DB1 but not in DB2
    missing_tables = db1_tables - db2_tables
    for table in missing_tables:
        diffs.append({
            "Table": table,
            "Column": "ALL",
            "Difference Type": "Missing Table in DB2",
            "DB1 Value": "Exists",
            "DB2 Value": "Missing"
        })

    # Tables in DB2 but not in DB1 (Extra tables)
    extra_tables = db2_tables - db1_tables
    for table in extra_tables:
        diffs.append({
            "Table": table,
            "Column": "ALL",
            "Difference Type": "Extra Table in DB2",
            "DB1 Value": "Missing",
            "DB2 Value": "Exists"
        })

    # Compare common tables
    common_tables = db1_tables.intersection(db2_tables)
    for table in common_tables:
        db1_cols = db1_lookup[table]
        db2_cols = db2_lookup[table]

        db1_col_names = set(db1_cols.keys())
        db2_col_names = set(db2_cols.keys())

        # Columns in DB1 but not in DB2
        missing_cols = db1_col_names - db2_col_names
        for col in missing_cols:
            diffs.append({
                "Table": table,
                "Column": col,
                "Difference Type": "Missing Column in DB2",
                "DB1 Value": "Exists",
                "DB2 Value": "Missing"
            })

        # Columns in DB2 but not in DB1
        extra_cols = db2_col_names - db1_col_names
        for col in extra_cols:
            diffs.append({
                "Table": table,
                "Column": col,
                "Difference Type": "Extra Column in DB2",
                "DB1 Value": "Missing",
                "DB2 Value": "Exists"
            })

        # Compare common columns
        common_cols = db1_col_names.intersection(db2_col_names)
        for col in common_cols:
            row1 = db1_cols[col]
            row2 = db2_cols[col]

            # Compare Type
            if row1['Type'] != row2['Type']:
                diffs.append({
                    "Table": table,
                    "Column": col,
                    "Difference Type": "Type Mismatch",
                    "DB1 Value": row1['Type'],
                    "DB2 Value": row2['Type']
                })
            
            # Compare Nullable
            if row1['Nullable'] != row2['Nullable']:
                diffs.append({
                    "Table": table,
                    "Column": col,
                    "Difference Type": "Nullable Mismatch",
                    "DB1 Value": str(row1['Nullable']),
                    "DB2 Value": str(row2['Nullable'])
                })

    return pd.DataFrame(diffs)

def main():
    # Get database URLs from .env
    db_url_1 = os.getenv("DATABASE_URL1")
    db_url_2 = os.getenv("DATABASE_URL2")
    
    data_1 = []
    data_2 = []
    
    # Process DB1
    if db_url_1:
        print("Processing Database 1 (Master)...")
        data_1 = get_db_structure(db_url_1, "DB_1")
    else:
        print("DATABASE_URL1 not found in .env")

    # Process DB2
    if db_url_2:
        print("Processing Database 2...")
        data_2 = get_db_structure(db_url_2, "DB_2")
    else:
        print("DATABASE_URL2 not found in .env")
        
    # Create DataFrames
    df1 = pd.DataFrame(data_1)
    df2 = pd.DataFrame(data_2)
    
    if df1.empty and df2.empty:
        print("No data retrieved from either database.")
        return

    # Combined DataFrame
    df_combined = pd.concat([df1, df2], ignore_index=True)
    
    # Compare Databases
    print("Comparing databases...")
    df_diff = compare_databases(df1, df2)
    
    output_file = "estructura_base_datos.xlsx"
    
    try:
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Sheet 1: DB1
            if not df1.empty:
                df1.to_excel(writer, sheet_name='DB1', index=False)
            
            # Sheet 2: DB2
            if not df2.empty:
                df2.to_excel(writer, sheet_name='DB2', index=False)
                
            # Sheet 3: Combined
            if not df_combined.empty:
                df_combined.to_excel(writer, sheet_name='Combinado', index=False)
                
            # Sheet 4: Differences
            if not df_diff.empty:
                df_diff.to_excel(writer, sheet_name='Diferencias', index=False)
            else:
                # Create an empty sheet with columns if no differences found
                pd.DataFrame(columns=["Table", "Column", "Difference Type", "DB1 Value", "DB2 Value"]).to_excel(writer, sheet_name='Diferencias', index=False)
                
        print(f"Successfully exported database structure and differences to {output_file}")
        
    except Exception as e:
        print(f"Error writing to Excel: {e}")

if __name__ == "__main__":
    main()
