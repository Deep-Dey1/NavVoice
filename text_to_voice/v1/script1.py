import cv2
import pytesseract
from gtts import gTTS
import os


pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'


DROIDCAM_IP = "192.168.114.233"  
VIDEO_URL = f"http://{DROIDCAM_IP}:4747/video" 

def capture_image():
    cap = cv2.VideoCapture(VIDEO_URL) 
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame. Check DroidCam connection.")
            break

        cv2.imshow("Capture Document (Press 's' to save)", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('s'):  
            img_path = "captured_image.jpg"
            cv2.imwrite(img_path, frame)
            break

    cap.release()
    cv2.destroyAllWindows()
    return img_path

def extract_text(img_path):
    img = cv2.imread(img_path)
    text = pytesseract.image_to_string(img)
    return text.strip()

def text_to_speech(text):
    if text:
        tts = gTTS(text=text, lang='en')
        audio_path = "output_audio.mp3"
        tts.save(audio_path)
        os.system(f"start {audio_path}")  
    else:
        print("No text found in the image.")

if __name__ == "__main__":
    img_path = capture_image()
    extracted_text = extract_text(img_path)
    print("Extracted Text:\n", extracted_text)
    text_to_speech(extracted_text)
