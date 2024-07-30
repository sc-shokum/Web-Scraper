import pandas as pd
import psycopg
from psycopg import sql
from dotenv import load_dotenv
import os

def load_data():
    load_dotenv()

    db_params = {
        'dbname': os.getenv('DB_NAME'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'host': os.getenv('DB_HOST'),
        'port': os.getenv('DB_PORT')
    }

    csv_file = 'entity_details.csv' 
    df = pd.read_csv(csv_file)

    df['Incorporation Date/Formation Date'] = pd.to_datetime(df['Incorporation Date/Formation Date'])

    conn = psycopg.connect(**db_params)
    cur = conn.cursor()

    create_table_query = '''
    CREATE TABLE IF NOT EXISTS entity_data (
        file_number INT,
        incorporation_date DATE,
        entity_name VARCHAR(255),
        entity_kind VARCHAR(50),
        entity_type VARCHAR(50),
        residency VARCHAR(50),
        state VARCHAR(50)
    );
    '''
    cur.execute(create_table_query)
    conn.commit()

    insert_query = '''
    INSERT INTO entity_data (file_number, incorporation_date, entity_name, entity_kind, entity_type, residency, state)
    VALUES (%s, %s, %s, %s, %s, %s, %s);
    '''

    for _, row in df.iterrows():
        cur.execute(insert_query, (
            row['File Number'],
            row['Incorporation Date/Formation Date'],
            row['Entity Name'],
            row['Entity Kind'],
            row['Entity Type'],
            row['Residency'],
            row['State']
        ))

    conn.commit()

    cur.close()
    conn.close()

    print("Data inserted successfully")
