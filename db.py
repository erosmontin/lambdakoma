import sqlite3
import os
import struct

def interpret_binary_data(blob):
    # Placeholder function to interpret the binary data.
    # You'll need to implement the specific logic to parse the binary format.
    # This is an example that reads the first 4 bytes as a float.
    
    # Example interpretation (this needs to be adjusted based on actual format):
    values = []
    try:
        # Example: assuming the binary blob consists of a series of floats (adjust as needed)
        num_floats = len(blob) // 4  # Each float is 4 bytes
        for i in range(num_floats):
            value = struct.unpack('f', blob[i*4:(i+1)*4])[0]
            values.append(value)
    except Exception as e:
        print(f"Error interpreting binary data: {e}")
    
    return values

def fetch_and_save_vectors(database_path):
    # Connect to the SQLite database
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # Query to select material properties with vectors
    query = """
    SELECT m.name AS material_name, p.name AS property_name, p.physics, p.variable, v.vals
    FROM properties p
    JOIN vectors v ON p.prop_id = v.prop_id
    JOIN materials m ON v.mat_id = m.mat_id
    WHERE p.physics = 'mri'
    """
    
    # Execute the query
    cursor.execute(query)

    # Fetch all results
    results = cursor.fetchall()

    # Output directory for files
    output_dir = '/g/output_vectors'
    os.makedirs(output_dir, exist_ok=True)

    for material_name, property_name, physics, variable, blob in results:
        # Interpret the binary data
        interpreted_values = interpret_binary_data(blob)
        
        # Create a filename for the UTF-8 text file
        filename = f"{material_name.replace(' ', '_')}_{property_name.replace(' ', '_')}_{physics}_{variable}.txt"
        file_path = os.path.join(output_dir, filename)

        # Save the interpreted values as UTF-8 text
        with open(file_path, 'w', encoding='utf-8') as txt_file:
            for value in interpreted_values:
                txt_file.write(f"{value}\n")

    # Close the database connection
    conn.close()

# Example usage
database_path = 'your_database.db'  # Replace with your actual database path
fetch_and_save_vectors(database_path)
