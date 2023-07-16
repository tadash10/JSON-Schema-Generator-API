import json
from flask import Flask, request

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
    else:
        return "unknown"

def save_schema(schema, filename):
    with open(filename, "w") as file:
        json.dump(schema, file, indent=4)

@app.route("/generate-schema", methods=["POST"])
def handle_generate_schema():
    data = request.json
    schema = generate_schema(data)
    save_schema(schema, "schema.json")
    return "Schema generated successfully!"

if __name__ == "__main__":
    app.run()
