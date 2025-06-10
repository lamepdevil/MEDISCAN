import os
import mimetypes
import requests

def upload_image_and_get_result(image_path, api_url="http://127.0.0.1:8000/upload/", timeout=15, debug=False):
    """
    Uploads an image to the MediScan API and returns the result.

    Args:
        image_path (str): Full path to the image file.
        api_url (str): Endpoint URL of the API.
        timeout (int): Request timeout in seconds.
        debug (bool): If True, prints debug information.

    Returns:
        dict: Parsed JSON result or structured error message.
    """
    if not os.path.isfile(image_path):
        return {"error": "File does not exist."}

    mime_type, _ = mimetypes.guess_type(image_path)
    if mime_type not in ("image/png", "image/jpeg"):
        return {"error": f"Unsupported file type: {mime_type}"}

    try:
        with open(image_path, "rb") as file:
            files = {'file': (os.path.basename(image_path), file, mime_type)}
            response = requests.post(api_url, files=files, timeout=timeout)

        if debug:
            print("Status Code:", response.status_code)
            print("Response:", response.text)

        response.raise_for_status()  # Raise an HTTPError on 4xx/5xx

        result = response.json()

        if not isinstance(result, dict):
            return {"error": "Invalid JSON structure returned by server."}

        if "report_type" not in result:
            return {"error": "Missing 'report_type' in response."}

        return result

    except requests.exceptions.Timeout:
        return {"error": "Request timed out."}
    except requests.exceptions.RequestException as e:
        return {"error": f"HTTP error occurred: {str(e)}"}
    except ValueError:
        return {"error": "Could not decode JSON response."}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}
