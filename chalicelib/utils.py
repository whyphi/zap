import base64
import imghdr


def decode_base64(base64_data):
    """Decodes base64 data into binary data."""
    binary_data = base64.b64decode(base64_data)
    return binary_data

def get_image_extension_from_base64(base64_data):
    try:
        # Decode the Base64 data to bytes
        binary_data = base64.b64decode(base64_data)

        # Use imghdr to identify the image format
        image_format = imghdr.what(None, binary_data)

        if image_format:
            # Normalize the format to lowercase (e.g., 'JPEG' -> 'jpg')
            image_format = image_format.lower()

            # You can return the image format or the corresponding file extension
            # If you want the extension, you can map known formats to extensions
            format_to_extension = {
                'jpeg': 'jpg',  # 'jpeg' is returned by imghdr for JPEG files
                'png': 'png',
                'heic': 'heic',
                # Add more formats as needed
            }

            extension = format_to_extension.get(image_format)
            return extension

    except Exception as e:
        # Handle decoding or identification errors here
        print(f"Error: {str(e)}")

    # Return None if the format cannot be determined
    return None