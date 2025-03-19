import cv2  
import urllib.request  
import numpy as np  
import requests  
import os  
import time  

# ? Step 1: Configure Camera Stream & API
URL = "http://10.162.166.66:4747/mjpegfeed"  # Update with your DroidCam IP
IMAGE_PATH = "captured_image.jpg"

API_URL = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-base"
HEADERS = {"Authorization": "Bearer hf-key"}  # Replace with your API key

# ? Step 2: Function to Get Caption from Hugging Face API
def get_caption(image_path):
    try:
        with open(image_path, "rb") as image_file:
            image_bytes = image_file.read()
            response = requests.post(API_URL, headers=HEADERS, data=image_bytes)

        response_json = response.json()
        print("? API Response:", response_json)  # Debugging output

        if "error" in response_json:
            print("? API Error:", response_json["error"])
            if "loading" in response_json["error"]:
                print("? Model is still loading. Retrying in 10 seconds...")
                time.sleep(10)
                return get_caption(image_path)  # Retry
            return None

        if isinstance(response_json, list) and "generated_text" in response_json[0]:
            return response_json[0]["generated_text"]
        
        return response_json.get("generated_text", "No caption generated")
    except Exception as e:
        print(f"? Error while processing image: {str(e)}")
        return None

# ? Step 3: Faster TTS using `flite`
def speak_text(text):
    os.system(f'flite -t "{text}"')

# ? Step 4: Capture Video Stream with Lower Resolution
def main():
    stream = urllib.request.urlopen(URL)
    bytes_data = bytes()
    frame_count = 0  # Frame counter

    print("? Press 'c' to capture and caption an image. Press 'q' to quit.")

    while True:
        bytes_data += stream.read(1024)
        a = bytes_data.find(b'\xff\xd8')
        b = bytes_data.find(b'\xff\xd9')

        if a != -1 and b != -1:
            jpg = bytes_data[a:b+2]
            bytes_data = bytes_data[b+2:]
            
            # ? Convert frame to OpenCV format
            img = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
            
            # ? Reduce resolution for better performance
            img = cv2.resize(img, (320, 240))  

            cv2.imshow('DroidCam Feed (Press "C" to Capture)', img)

            frame_count += 1  # Increment frame counter

            # ? Process only every 30th frame to reduce CPU load
            if frame_count % 30 == 0:
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord('c'):  # Capture & process image
                    cv2.imwrite(IMAGE_PATH, img)
                    print(f"? Image saved as '{IMAGE_PATH}'")
                    
                    caption = get_caption(IMAGE_PATH)
                    if caption:
                        print(f"? Caption: {caption}")
                        speak_text(caption)
                    else:
                        print("? Could not generate a caption. Please check the API response.")

                elif key == ord('q'):  # Exit program
                    print("? Exiting...")
                    break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
