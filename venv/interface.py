import os
import pandas as pd
import plotly.express as px
# from langchain import OpenAI, SQLDatabase, SQLDatabaseChain
from dotenv import load_dotenv
# from sqlalchemy import create_engine
from google.cloud import bigquery
import google.generativeai as genai
#from openai import OpenAI


load_dotenv()

#OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
#os.environ["OPENAI_API_KEY"] = "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"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/rathore/Desktop/talktodatabase/venv/talk2urdatbase-8a46d9d3b3dc.json"
genai.configure()

# response = genai.TextCompletion.create(
#     model="gemini-1.5-t",
#     messages=[{"role": "user", "content": "Say hello"}]
# )
# print(response.last.message.get("content", "No response"))


# db_user = "your-db-user"
# db_pass = "your-db-password"
# db_name = "your-database-name"
# instance_connection_name = "your-project:region:instance-name"


client = bigquery.Client(project="talk2urdatbase")
#ai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
# ai = OpenAI(api_key=OPENAI_API_KEY)


# db_url = f"postgresql+pg8000://{db_user}:{db_pass}@/{db_name}?unix_sock=/cloudsql/{instance_connection_name}/.s.PGSQL.5432"


# db = SQLDatabase.from_uri(db_url)


# llm = OpenAI(temperature=0)

# Create database chain
# db_chain = SQLDatabaseChain(llm=llm, database=db, verbose=True)

# def ask_database(question: str):
#     try:
#         response = db_chain.run(question)
#         return response
#     except Exception as e:
#         return f"Error: {str(e)}"


# if __name__ == "__main__":
#     print("Welcome to AI Database Assistant! (Type 'exit' to quit)")
#     while True:
#         question = input("\nAsk a question about your database: ")
#         if question.lower() == 'exit':
#             break
#         response = ask_database(question)
#         print("\nResponse:", response)

def english_to_sql_gemini(question: str, schema_hint: str = "") -> str:
    """
    Converts natural language question to SQL using Google Gemini.
    """
    prompt = f"""
You are an expert BigQuery SQL generator.
Important: Do not use backticks (`) in column names or table names.
Given the following schema: {schema_hint}
Convert this natural language question into a correct BigQuery SQL query:

Question: {question}

Rules:
1. give only the SQL query as the answer, nothing else.
2. do not use backticks (```) at start or end.
3. use backticks (`) only for table names and column names that include spaces.
"""
    model = genai.GenerativeModel(model_name='gemini-2.5-pro')

    response = model.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(temperature=0)
    )

    #sql_query = response.choices[0].message.content.strip()
    sql_query = response.text.strip()
    return sql_query

#     response = genai.chat.completions.create(
#     model="gemini-1.5-t",
#     messages=[{"role": "user", "content": prompt}],
#     temperature=0
# )


# query = "SELECT e.Department,c.`Annual Salary`FROM`talk2urdatbase.Mac.employee` AS e JOIN `talk2urdatbase.handyman.common_database` AS c ON e.`Employee ID` = c.`Employee ID`;"
# results = client.query(query)

def run_query(sql: str) -> pd.DataFrame:
    """
    Executes SQL on BigQuery and returns a Pandas DataFrame.
    """
    query_job = client.query(sql)
    return query_job.to_dataframe()


def plot_dataframe(df: pd.DataFrame):
    """
    Automatically generates a bar chart if numeric columns exist.
    """
    if df.empty:
        print("No results to plot.")
        return


    numeric_cols = df.select_dtypes(include="number").columns
    if not numeric_cols.any():
        print("No numeric columns to plot.")
        return

   
    y_col = numeric_cols[0]
    x_cols = df.select_dtypes(exclude="number").columns
    x_col = x_cols[0] if len(x_cols) > 0 else df.index

    fig = px.bar(df, x=x_col, y=y_col, title=f"{y_col} by {x_col}")
    fig.show()




def get_bigquery_schema(project_id: str) -> str:
    """
    Connects to BigQuery and dynamically fetches the schema for all tables.
    """
    client = bigquery.Client(project=project_id)
    schema_parts = ["Tables:"]
    table_count = 1

    datasets = list(client.list_datasets())
    
    if not datasets:
        return "No datasets found in the project."

    for dataset in datasets:
        dataset_id = dataset.dataset_id
        # Get all tables in the dataset
        tables = list(client.list_tables(dataset_id))
        for table in tables:
            # Get the full table object to access schema
            table_ref = client.get_table(table.reference)
            
            # Get just the column names
            column_names = [field.name for field in table_ref.schema]
            
            # Format the schema string
            table_id = f"{table.project}.{table.dataset_id}.{table.table_id}"
            columns_str = ", ".join(f"`{name}`" for name in column_names)
            schema_parts.append(f"{table_count}. {table_id}({columns_str})")
            table_count += 1
            
    return "\n".join(schema_parts)



if __name__ == "__main__":
    print("🤖 Talk to Your Database — type 'exit' to quit\n")

    project_id = "talk2urdatbase"


    # schema_hint = """
    # Tables:
    # 1. talk2urdatbase.Mac.employee(`Employee ID`, `Full Name`, Department, `Job Title`)
    # 2. talk2urdatbase.handyman.common_database(`Employee ID`, `Annual Salary`, `Bonus %`, Country)
    # """
    try:
        schema_hint = get_bigquery_schema(project_id)
    except Exception as e:
        print(f"❌ Could not detect schema: {e}")
        exit()



    while True:
        question = input("🧍 You: ")
        if question.lower() in ["exit", "quit"]:
            break

        try:
            sql_query = english_to_sql_gemini(question, schema_hint)
            print("\n🧠 generated SQL:\n", sql_query)
        except Exception as e:
            print("❌ Gemini Error:", e)
            continue

        try:
            df = run_query(sql_query)
            print("\n📊 Query Results:")
            print(df.head())  
        except Exception as e:
            print("\n❌ Query Error:", e)
            continue


        try:
            plot_dataframe(df)
        except Exception as e:
            print("\n❌ Chart Error:", e)

# Fetch data
# for row in results:
#     print(row)
