# import cv2
# import numpy as np
# from insightface.app import FaceAnalysis

# def authentication(path):
#     app = FaceAnalysis(name='buffalo_l')
#     app.prepare(ctx_id=0, det_size=(640, 640))

# # Load registered user
#     # registered_path = "D:/Documents/python dsa/images/madival.jpg"
#     img_registered = cv2.imread(path)
#     faces_reg = app.get(img_registered)

#     if len(faces_reg) == 0:
#         raise ValueError("No face found in the registered image!")

#     registered_emb = faces_reg[0].embedding  # 512-d embedding of registered face

# # Capture single frame from webcam
#     cap = cv2.VideoCapture(0)
#     ret, frame = cap.read()
#     cap.release()

#     if not ret:
#         raise RuntimeError("Failed to capture webcam frame!")

# # Detect face in captured frame
#     faces_live = app.get(frame)

#     if len(faces_live) == 0:
#         print(False)  # No face detected
#     else:
#         live_emb = faces_live[0].embedding
#     # Cosine similarity
#     similarity = np.dot(live_emb, registered_emb) / (np.linalg.norm(live_emb) * np.linalg.norm(registered_emb))
    
#     # Threshold (adjust if needed, 0.35–0.45 typical)
#     if similarity >= 0.4:
#         return True  # Face matched
#     else:
#         return False  # Face does not match

# res=authentication("images/mahadev.jpg")
# print(res)

# import cv2
# import numpy as np

# def check_user_liveness_fast():
#     """
#     Ultra-fast blink detection - returns in ~1 second
#     """
#     cap = cv2.VideoCapture(0)
#     face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
#     eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
    
#     # Set camera to lower resolution for faster processing
#     cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
#     cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
    
#     print("Quickly blink now...")
    
#     for _ in range(20):  # Check only 20 frames (~0.6-1 second)
#         ret, frame = cap.read()
#         if not ret:
#             break
            
#         gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#         faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
#         if len(faces) > 0:
#             (x, y, w, h) = faces[0]
#             face_roi = gray[y:y+h, x:x+w]
            
#             eyes = eye_cascade.detectMultiScale(face_roi, 1.1, 3)
            
#             # If no eyes detected for 1 frame, consider it a blink
#             if len(eyes) == 0:
#                 cap.release()
#                 cv2.destroyAllWindows()
#                 print("✅ Blink detected! Live user verified.")
#                 return True
            
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break
    
#     cap.release()
#     cv2.destroyAllWindows()
#     print("❌ No blink detected")
#     return False

# # Fastest usage:
# is_live = check_user_liveness_fast()
# print(f"User is live: {is_live}")

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import base64
import os

# ----------------------------
# AES-256-GCM KEY (32 bytes)
# IMPORTANT: store this securely! Not inside code.
# For demo, generating one if not exists.
# ----------------------------

# On first run, generate a key and save it to a file:
KEY_FILE = "aes_key.bin"

if not os.path.exists(KEY_FILE):
    key = AESGCM.generate_key(bit_length=256)
    with open(KEY_FILE, "wb") as f:
        f.write(key)

# Load key
with open(KEY_FILE, "rb") as f:
    AES_KEY = f.read()

aesgcm = AESGCM(AES_KEY)



# ----------------------------
# ENCRYPT PIN (returns iv + ciphertext)
# ----------------------------
def encrypt_pin(pin: str):
    iv = os.urandom(12)  # 96-bit nonce
    encrypted = aesgcm.encrypt(iv, pin.encode(), None)

    return base64.b64encode(iv).decode(), base64.b64encode(encrypted).decode()



# ----------------------------
# DECRYPT PIN
# ----------------------------
def decrypt_pin(iv_b64: str, enc_b64: str):
    iv = base64.b64decode(iv_b64)
    encrypted = base64.b64decode(enc_b64)

    decrypted = aesgcm.decrypt(iv, encrypted, None)
    return decrypted.decode()


res,enc=encrypt_pin("2536")

decy=decrypt_pin(res,enc)

print(decy)