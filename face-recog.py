import cv2
import requests
import pyttsx3
import time  # <-- Added for delay

# Flask Server Details (Laptop IP)
FLASK_SERVER_URL = "http://10.162.156.138:5000/process_image"

# DroidCam Settings (Replace with your DroidCam IP)
DROIDCAM_IP = "10.162.166.66"
DROIDCAM_PORT = 4747
DROIDCAM_URL = f"http://{DROIDCAM_IP}:{DROIDCAM_PORT}/video"

# Initialize Text-to-Speech
engine = pyttsx3.init()
engine.setProperty('rate', 125)  # ? Slow down the speech rate (default ~200)
engine.setProperty('volume', 1.0)  # Max volume

def speak(text):
    """Convert text to speech with a delay for clarity."""
    print(f"Speaking: {text}")
    engine.say(text)
    engine.runAndWait()  # ? Ensure speech completes before continuing
    time.sleep(1)  # ? Small delay for natural pacing

def capture_image():
    """Capture image from DroidCam and save it."""
    cap = cv2.VideoCapture(DROIDCAM_URL)
    if not cap.isOpened():
        print("Error: Could not connect to DroidCam.")
        return None

    print("Press 's' to capture the image...")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            break

        cv2.imshow("Capture Image", frame)

        # Press 's' to capture image
        if cv2.waitKey(1) & 0xFF == ord('s'):
            image_path = "captured_image.jpg"
            cv2.imwrite(image_path, frame)
            print(f"Image saved: {image_path}")
            cap.release()
            cv2.destroyAllWindows()
            return image_path

    cap.release()
    cv2.destroyAllWindows()
    return None

def send_image_to_server(image_path):
    """Send the captured image to the Flask server and return the response."""
    try:
        with open(image_path, 'rb') as image_file:
            files = {'image': image_file}  # Ensure key matches Flask server
            response = requests.post(FLASK_SERVER_URL, files=files)
            
            if response.status_code == 200:
                result = response.json()
                return result.get("message", "Unknown response from server")
            elif response.status_code == 400:
                return "Error: Server did not receive an image properly"
            elif response.status_code == 500:
                return "Error: Internal server error during analysis"
            else:
                return f"Error: Server returned status code {response.status_code}"

    except Exception as e:
        return f"Error sending image: {str(e)}"

if __name__ == "__main__":
    while True:
        print("\n=== Face Recognition System ===")
        print("1. Capture & Recognize Face")
        print("2. Exit")
        choice = input("Enter your choice: ")

        if choice == "1":
            image_path = capture_image()
            if image_path:
                print("Sending image to server for recognition...")
                result_text = send_image_to_server(image_path)
                print(f"Server Response: {result_text}")
                speak(result_text)  # ? Voice output of result (improved)
            else:
                print("Image capture failed. Try again.")
        elif choice == "2":
            print("Exiting system.")
            speak("Exiting the system. Goodbye!")  # ? Say goodbye before exiting
            break
        else:
            print("Invalid choice. Please try again.")
