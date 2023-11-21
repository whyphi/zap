import base64
import imghdr


def decode_base64(base64_data):
    """Decodes base64 data into binary data."""
    binary_data = base64.b64decode(base64_data)
    return binary_data

def get_file_extension_from_base64(base64_data):
    parts = base64_data.split(',')
    if len(parts) != 2:
        return None  # Invalid data URI format

    metadata = parts[0]

    # Extract content type from metadata.
    content_type = metadata.split(';')[0][5:]  # Remove "data:" prefix

    # Map content type to file extension.
    extension_map = {
        "image/jpeg": "jpg",
        "image/png": "png",
        "application/pdf": "pdf",
        # Add more content type to extension mappings as needed.
    }

    # Use the mapping to get the extension (default to 'dat' if not found).
    extension = extension_map.get(content_type, 'dat')

    return extension