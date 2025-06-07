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
    elif value is None:
        return None
    else:
        # Convert the value to a string and apply SHA-256 hash
        hash_object = hashlib.sha256(str(value).encode("utf-8"))
        hashed_value = hash_object.hexdigest()

        # Generate a random length between 7 and 20
        random_length = random.randint(7, 20)

        # Return a truncated version of the hashed value
        return hashed_value[:random_length]


def get_newsletter_css():
    """Returns the CSS styling for the newsletter."""
    return """
        <style>
            body {
                margin: 0;
                padding: 0;
                font-family: Arial, sans-serif;
                color: #333;
                background-color: #f5f5f5;
            }
            
            .newsletter-container {
                max-width: 650px;
                margin: 0 auto;
                background-color: #fff;
                padding: 0;
                text-align: left;
                border-left: 1px solid #ddd;
                border-right: 1px solid #ddd;
            }
            
            .newsletter-header {
                background-image: url('https://whyphi-public.s3.us-east-1.amazonaws.com/newsletter_cover.jpg');
                background-size: cover;
                background-position: center;
                padding: 30px 20px 10px;
                text-align: center;
                height: 100px; /* Fixed height to ensure proper display */
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            .newsletter-title {
                font-family: 'Times New Roman', Times, serif;
                font-size: 48px;
                font-weight: bold;
                color: #000;
                margin: 0;
                padding: 0;
                text-align: center;
            }
            
            .newsletter-subtitle {
                font-size: 20px;
                text-transform: uppercase;
                letter-spacing: 1px;
                border-top: 1px solid #888;
                border-bottom: 1px solid #888;
                padding: 5px 0;
                margin: 10px 0 20px;
                text-align: center;
            }
            
            .welcome-message {
                padding: 20px;
                background-color: #fff;
                text-align: center;
            }
            
            .main-content {
                padding: 0 20px;
            }
            
            .section-banner {
                width: 100%;
                margin: 0 0 15px 0;
                overflow: hidden;
            }
            
            .section-banner img {
                width: 100%;
                display: block;
            }
            
            .job-opportunities-banner {
                width: 100%;
                margin: 20px 0 0 0;
                overflow: hidden;
            }
            
            .job-opportunities-banner img {
                width: 100%;
                display: block;
            }
            
            .job-sources {
                background-color: #f9f9f9;
                padding: 15px;
                margin: 0 0 20px 0;
                font-size: 14px;
                line-height: 1.5;
                border-bottom: 1px solid #eee;
            }
            
            .section-title {
                font-size: 28px;
                text-transform: uppercase;
                text-align: center;
                background-color: #f2f2f2;
                padding: 15px;
                margin: 0 0 20px;
                border: none;
            }
            
            .jobs-section {
                margin-bottom: 40px;
            }
            
            .job-item {
                margin-bottom: 20px;
                padding: 0 0 15px 0;
                border-bottom: 1px dotted #ddd;
            }
            
            .job-title {
                font-weight: bold;
                margin-bottom: 5px;
            }
            
            .job-details {
                font-size: 14px;
            }
            
            .events-section {
                margin-bottom: 40px;
            }
            
            .footer {
                text-align: center;
                padding: 20px;
                border-top: 1px solid #ddd;
            }
            
            .social-links {
                text-align: center;
                margin: 20px 0;
            }
            
            .social-links a {
                margin: 0 10px;
                text-decoration: none;
            }
        </style>
    """
