import json
import datetime
import logging
from flask import Flask, request
from jsonschema import validate, ValidationError
from werkzeug.exceptions import HTTPException

app = Flask(__name__)
app.config["DEBUG"] = False

# Set up logging
logging.basicConfig(filename="app.log", level=logging.ERROR, format="%(asctime)s %(levelname)s %(message)s")

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
        return True, None
    except ValidationError as e:
        return False, str(e)

def sanitize_input(data):
    # Implement input sanitization logic here
    sanitized_data = data  # Placeholder for actual sanitization
    return sanitized_data

@app.route("/generate-schema", methods=["POST"])
def handle_generate_schema():
    try:
        data = request.json
        sanitized_data = sanitize_input(data)
        schema = generate_schema(sanitized_data)
        save_schema(schema, "schema.json")
        return "Schema generated successfully!"
    except Exception as e:
        return handle_error(e)

@app.route("/validate-data", methods=["POST"])
def handle_validate_data():
    try:
        data = request.json
        with open("schema.json") as file:
            schema = json.load(file)
        sanitized_data = sanitize_input(data)
        is_valid, error = validate_request_data(sanitized_data, schema)
        if is_valid:
            return "Data is valid!"
        else:
            return "Data validation failed: " + error
    except Exception as e:
        return handle_error(e)

def handle_error(e):
    if isinstance(e, HTTPException):
        description = e.description
        code = e.code
    else:
        description = "An internal server error occurred."
        code = 500
        logging.exception(e)  # Log the error for debugging purposes
    response = {
        "error": description,
        "status_code": code
    }
    return json.dumps(response), code, {"Content-Type": "application/json"}

if __name__ == "__main__":
    app.run()
