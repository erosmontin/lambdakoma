# app.py

import json
import pynico_eros_montin.pynico as pn
import subprocess

def handler(event, context):

    print("Received event: " + json.dumps(event, indent=2))


    command = ['julia','--project=.', 'japp.jl']
    print("command set")

    process = subprocess.Popen(command, stdout=subprocess.PIPE, text=True, universal_newlines=True)
    print("it started")
    
    process.wait()

    output,tt = process.communicate()
    
    # check if raw_data.jld2 exists
    if pn.Pathable("/tmp/raw.jld2").exists():
        print("raw.jdl exists")
    else:
        print("raw.jld2 does not exist")
    print (output)
    print (tt)
    return {
        'statusCode': 200,
        'body': output
    }
    
    

