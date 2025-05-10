import base64
import random
import hashlib


def decode_base64(base64_data):
    """Decodes base64 data into binary data."""
    binary_data = base64.b64decode(base64_data)
    return binary_data


def get_file_extension_from_base64(base64_data):
    parts = base64_data.split(",")
    if len(parts) != 2:
        return None  # Invalid data URI format

    metadata = parts[0]

    # Extract content type from metadata.
    content_type = metadata.split(";")[0][5:]  # Remove "data:" prefix

    # Map content type to file extension.
    extension_map = {
        "image/jpeg": "jpg",
        "image/png": "png",
        "application/pdf": "pdf",
        # Add more content type to extension mappings as needed.
    }

    # Use the mapping to get the extension (default to 'dat' if not found).
    extension = extension_map.get(content_type, "dat")

    return extension


def get_prev_image_version(version: str):
    return "v" + str(int(version[1:]) - 1)


def hash_value(value):
    """Helper function to hash a single value."""
    # If value is a dictionary or list, recursively hash the nested data
    if isinstance(value, dict):
        return {key: hash_value(val) for key, val in value.items()}
    elif isinstance(value, list):
        return [hash_value(item) for item in value]
    else:
        # Convert the value to a string and apply SHA-256 hash
        hash_object = hashlib.sha256(str(value).encode("utf-8"))
        hashed_value = hash_object.hexdigest()

        # Generate a random length between 7 and 20
        random_length = random.randint(7, 20)

        # Return a truncated version of the hashed value
        return hashed_value[:random_length]


def to_camel_case(snake_str):
    components = snake_str.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


def convert_to_camel_case(data):
    if isinstance(data, list):
        return [convert_to_camel_case(item) for item in data]
    elif isinstance(data, dict):
        return {
            to_camel_case(key): convert_to_camel_case(value)
            for key, value in data.items()
        }
    return data
