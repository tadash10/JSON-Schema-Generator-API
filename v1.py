import json
import datetime
from flask import Flask, request
from jsonschema import validate, ValidationError

app = Flask(__name__)

def generate_schema(template):
    schema = {}
    
    for key, value in template.items():
        if isinstance(value, dict):
            schema[key] = generate_schema(value)
        else:
            schema[key] = {"type": determine_type(value)}
    
    return schema

def determine_type(value):
    if isinstance(value, str):
        return "string"
    elif isinstance(value, int):
        return "integer"
    elif isinstance(value, float):
        return "number"
    elif isinstance(value, bool):
        return "boolean"
    elif isinstance(value, list):
        if len(value) > 0:
            return {"type": "array", "items": determine_type(value[0])}
        else:
            return {"type": "array"}
    elif isinstance(value, datetime.date):
        return {"type": "string", "format": "date"}
    elif isinstance(value, datetime.datetime):
        return {"type": "string", "format": "date-time"}
    else:
        return "unknown"

def save_schema(schema, filename):
    with open(filename, "w") as file:
        json.dump(schema, file, indent=4)

def validate_request_data(data, schema):
    try:
        validate(data, schema)
        return True
    except ValidationError as e:
        return str(e)

@app.route("/generate-schema", methods=["POST"])
def handle_generate_schema():
    data = request.json
    schema = generate_schema(data)
    save_schema(schema, "schema.json")
    return "Schema generated successfully!"

@app.route("/validate-data", methods=["POST"])
def handle_validate_data():
    data = request.json
    with open("schema.json") as file:
        schema = json.load(file)
    result = validate_request_data(data, schema)
    if result == True:
        return "Data is valid!"
    else:
        return "Data validation failed: " + result

if __name__ == "__main__":
    app.run()
