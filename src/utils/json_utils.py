import json


def write_json(data: dict | list, file_path: str, indent: int = 4) -> None:
    try:
        with open(file_path, "w") as file:
            json.dump(data, file, indent=indent)
    except Exception as e:
        print(f"Error writing to JSON file: {e}")


def read_json(file_path: str) -> dict | list | None:
    try:
        with open(file_path, "r") as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in '{file_path}'.")
        return None
