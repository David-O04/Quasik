import asyncio
import os
import json
import asyncpg

async def connect_to_postgres():
    try:
        # Connect to PostgreSQL
        conn = await asyncpg.connect(
            host="localhost",       
            port=5434,              
            user="davoberi",
            password="1234",
            database="davoberi",
        )
        return conn
    except Exception as e:
        print(f"Error connecting to PostgreSQL: {e}")
        return None

async def create_table(conn):
    try:
        # Create table if not exists
        result = await conn.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                insert_id VARCHAR(255),
                log_name VARCHAR(255),
                audit_type VARCHAR(255),
                authentication_info JSONB,
                authorization_info JSONB[],
                method_name VARCHAR(255),
                request JSONB,
                request_metadata JSONB,
                resource_name VARCHAR(255),
                service_name VARCHAR(255),
                status JSONB,
                principal_email VARCHAR(255)
            );
        """)
        print("Table creation result:", result)

    except Exception as e:
        print(f"Error creating table: {e}")


async def insert_data(conn, log_data):
    proto_payload = log_data.get("protoPayload", "")
    
    # Access nested data using get with default values
    insert_id = log_data.get("insertId", "")
    log_name = log_data.get("logName", "")
    authentication_info = proto_payload.get("authenticationInfo", {})
    principal_email = authentication_info.get("principalEmail", "")
    service_name = proto_payload.get("serviceName", "")
    method_name = proto_payload.get("methodName", "")
    status = proto_payload.get("status", "")
    
    # Determine audit_type based on the log data structure
    audit_type = "type.googleapis.com/google.cloud.audit.AuditLog"
    if "@type" in proto_payload:
        audit_type = proto_payload["@type"]

    try:
        # Insert data into the PostgreSQL table
        result =  await  conn.execute("""
    INSERT INTO audit_logs 
    (insert_id, log_name, audit_type, authentication_info, principal_email, service_name, method_name, request_metadata, status) 
    VALUES 
    ($1, $2, $3, $4::jsonb, $5, $6, $7, $8::jsonb, $9::jsonb);
""", 
   insert_id,
   log_name,
   audit_type,
   json.dumps(authentication_info),  # Convert dictionary to JSON string
   authentication_info.get("principalEmail", ""),
   service_name,
   method_name,
   json.dumps(log_data.get("protoPayload", {}).get("requestMetadata", {})),  # Convert request_metadata to JSON string
   json.dumps(log_data.get("protoPayload", {}).get("status", {})),  # Convert status to JSON string
)
        print(f"result {result}")


    except Exception as e:
        print(f"Error inserting data: {e}")
    
async def select_data(conn):
    try: 
        result = await conn.fetch("SELECT * FROM audit_logs")
        print(f"result {len(result)}")
    except Exception as e:
         
        print(f"Error inserting data: {e}")

async def import_data_from_json_files():
    try:
        # Connect to PostgreSQL
        conn = await connect_to_postgres()
        if conn is None:
            return

        # Create table if not exists
        await create_table(conn)

        # Directory containing JSON log files
        log_directory = "logs"

        # Iterate over each log file in the directory
        for filename in os.listdir(log_directory):
            if filename.endswith(".json"):
                file_path = os.path.join(log_directory, filename)
                print(f"found file {filename}")

                # Read JSON log file
                with open(file_path, 'r') as file:
                    log_data = json.load(file)
                    print(f"loaded file{log_data}")
                   
                # Insert data into the PostgreSQL table
                await insert_data(conn, log_data)
                await select_data(conn)
        print("Data imported successfully.")
    except Exception as e:
        print(f"Error importing data: {e}")
    finally:
        # Close the connection
        await conn.close()

if __name__ == "__main__":
    asyncio.run(import_data_from_json_files())

    #flask server with roots that fetch stuff from database based on what user is searching for, drowpdown, visualization of when logs happen or which ones had info and severity 
    #simple html, javascrpt, (d3.js?), root in flask thats a get() or post fetching the value returning them javascript handles that and puts that in a chart or graph, have something in flask that fetches the values in the database and then displays it
    #done 
    