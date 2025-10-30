"""
This is an SQL Agent that explores the SSURGO database given here - AZ649. 

The downloaded files are available in the Working with Soil/AZ649 directory. There's
a bash script called ssurgo-sqlite.sh that creates a SQLite database from the
SSURGO files. 

You can run it like this from the Working with Soil directory:

./ssurgo-to-sqlite.sh AZ649/soildb_US_2003.mdb

"""
import os
import json
import sqlite3
import openai
import dotenv


dotenv.load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Connect to the SSURGO database
conn = sqlite3.connect("ssurgo_az649.db")

def get_schema(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [t[0] for t in cursor.fetchall()]
    schema = {}
    for t in tables:
        cursor.execute(f"PRAGMA table_info({t});")
        schema[t] = [r[1] for r in cursor.fetchall()]
    return schema

schema = get_schema(conn)

def query_env(llm_query):
    """Run LLM-generated SQL and return reward + data sample"""
    try:
        cursor = conn.execute(llm_query)
        rows = cursor.fetchmany(5)
        if len(rows) > 0:
            return {"reward": 1, "rows": rows}
        else:
            return {"reward": 0, "rows": []}
    except Exception as e:
        return {"reward": -1, "error": str(e)}

def prompt_llm(schema):
    """Ask the model to generate a random valid SQL query"""
    prompt = f"""
    You are exploring a SQLite database of soil survey data.
    Here are the tables and their columns:
    {json.dumps(schema, indent=2)}

    Write one simple SQL SELECT query that joins or filters some of these tables.
    The query should be valid and return soil data.
    Only output the SQL statement, no commentary.
    """
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    sql = response.choices[0].message.content.strip()
    return sql

# Main RL-like loop
dataset = []
for step in range(20):
    sql = prompt_llm(schema)
    result = query_env(sql)
    dataset.append({"sql": sql, **result})
    print(f"Step {step+1}: {sql}\nReward: {result['reward']}\n")

# Save dataset
with open("sql_exploration_dataset.jsonl", "w") as f:
    for item in dataset:
        f.write(json.dumps(item) + "\n")
