import base64
from chalicelib.utils.utils import decode_base64, get_file_extension_from_base64


def test_decode_base64():
    # Simulate base64 encoded data
    encoded_data = b"VGhpcyBpcyBhIHRlc3Q="  # Example base64 encoded data

    # Encode the data for comparison
    expected_result = base64.b64decode(encoded_data)

    # Call the function being tested
    result = decode_base64(encoded_data)

    # Assertion to check if the function output matches expected result
    assert result == expected_result


def test_get_file_extension_from_base64():
    # Simulate base64 encoded data for different content types
    jpeg_base64 = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAAAAAAAAD"
    png_base64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAIAAAD8GO2jAA"
    pdf_base64 = "data:application/pdf;base64,JVBERi0xLjUNCg=="

    # Call the function being tested
    jpeg_extension = get_file_extension_from_base64(jpeg_base64)
    png_extension = get_file_extension_from_base64(png_base64)
    pdf_extension = get_file_extension_from_base64(pdf_base64)

    # Assertions to check if the function output matches expected extensions
    assert jpeg_extension == "jpg"
    assert png_extension == "png"
    assert pdf_extension == "pdf"

    pdf_base64 = "data:application/pdf;base64,JVBERi0xLjUNCg=="


def test_get_file_extension_invalid_data_uri():
    # Simulate base64 encoded data with an invalid format (no comma)
    invalid_base64 = (
        "data:image/jpeg;base64/iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAIAAAD8GO2jAA"
    )

    # Call the function being tested
    result = get_file_extension_from_base64(invalid_base64)

    # Assertion to check if the function returns None for an invalid data URI format
    assert result is None
