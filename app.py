# import cv2
# import easyocr
# import re
# import numpy as np
# import base64
# import io
# import os
# from flask import Flask, request, jsonify, render_template_string
# from flask_cors import CORS
# from ultralytics import YOLO
# from PIL import Image

# # Initialize Flask App
# app = Flask(__name__)
# CORS(app)

# # --- ENGINE INITIALIZATION ---
# print("🚀 Initializing Aadhaar Shield Engines... (This may take a minute)")
# try:
#     # Use the requested YOLO model - assuming 'yolo11n.pt' or 'best.pt' if exists
#     # Defaulting to yolo11n.pt as seen in previous apps
#     model_path = "yolo26n.pt"
#     model = YOLO(model_path)
#     reader = easyocr.Reader(['en'], gpu=False)
#     print(f"✅ Engines Loaded Successfully! using {model_path}")
# except Exception as e:
#     print(f"❌ Error loading engines: {e}")

# def ultimate_aadhaar_engine(img):
#     """
#     PORTED LOGIC: Strictly maintaining all functional steps from the user's request.
#     """
#     if img is None:
#         return None, False

#     h, w, _ = img.shape
#     processed_img = img.copy()

#     # --- STEP 1: Smart Image Preparation ---
#     if h > w:
#         print("Portrait detected. Rotating to Landscape...")
#         processed_img = cv2.rotate(processed_img, cv2.ROTATE_90_CLOCKWISE)
#         h, w = processed_img.shape[0], processed_img.shape[1]

#     # --- STEP 2: Custom YOLO Detection ---
#     results = model.predict(processed_img, conf=0.3, verbose=False)

#     masked_any_overall = False

#     # --- STEP 3: Multi-Box Verification Loop ---
#     for i, box in enumerate(results[0].boxes):
#         x1, y1, x2, y2 = map(int, box.xyxy[0])
#         # Safety bounds
#         x1, y1 = max(0, x1), max(0, y1)
#         x2, y2 = min(processed_img.shape[1], x2), min(processed_img.shape[0], y2)

#         base_crop = processed_img[y1:y2, x1:x2]

#         print(f"Checking Box #{i+1} (Confidence: {box.conf[0]:.2f})...")

#         # --- STEP 4: Orientation Correction (0, 90, 180, 270) ---
#         for angle in [None, cv2.ROTATE_90_CLOCKWISE, cv2.ROTATE_180, cv2.ROTATE_90_COUNTERCLOCKWISE]:
#             test_crop = base_crop.copy()
#             if angle is not None:
#                 test_crop = cv2.rotate(test_crop, angle)

#             # OCR Check
#             ocr_results = reader.readtext(test_crop)

#             # --- STAGE 5: FIND & MASK AADHAAR ---
#             found_and_masked = False
#             for (bbox, text, prob) in ocr_results:
#                 clean_text = text.replace(" ", "")
#                 if re.search(r"\d{4}\s\d{4}\s\d{4}", text) or (len(clean_text) == 12 and clean_text.isdigit()):
#                     print(f"✅ Aadhaar found in Box #{i+1} at angle {0 if angle is None else angle}")

#                     (tl, tr, br, bl) = bbox
#                     mx_start, my_start = int(tl[0]), int(tl[1])
#                     mx_end, my_end = int(br[0]), int(br[1])

#                     # --- IMPROVED BACKGROUND SAMPLING ---
#                     # Safely sample inside the card boundaries
#                     y_sample = min(test_crop.shape[0]-1, my_start + max(1, (my_end - my_start) // 4))
#                     x_sample = min(test_crop.shape[1]-1, mx_start + 2)
#                     bg_color = [int(c) for c in test_crop[y_sample, x_sample]]

#                     # MASKING LOGIC (64% Cut)
#                     total_width = mx_end - mx_start
#                     box_height = my_end - my_start
#                     available_mask_width = int(total_width * 0.64)
#                     new_x_end = mx_start + available_mask_width

#                     cv2.rectangle(test_crop, (mx_start, my_start), (new_x_end, my_end), bg_color, -1)

#                     mask_text = "xxxxxxxx"
#                     font = cv2.FONT_HERSHEY_DUPLEX # Cleaner font
#                     current_scale = box_height / 30.0
#                     while True:
#                         (tw, th), _ = cv2.getTextSize(mask_text, font, current_scale, 1)
#                         if tw <= available_mask_width * 0.95 or current_scale < 0.1:
#                             break
#                         current_scale -= 0.05

#                     y_center = my_start + (box_height // 2) + (th // 2) - int(box_height * 0.05)
#                     cv2.putText(test_crop, mask_text, (mx_start, y_center),
#                                 font, current_scale, (0, 0, 0), 1, cv2.LINE_AA)

#                     found_and_masked = True

#             if found_and_masked:
#                 return test_crop, True

#     # --- FINAL ROBUST FALLBACK (If YOLO fails or misses) ---
#     print("⚠️ YOLO missed detection. Running full-image deep search...")
#     # We rotate the whole image and check if OCR finds it
#     for angle in [None, cv2.ROTATE_90_CLOCKWISE, cv2.ROTATE_180, cv2.ROTATE_90_COUNTERCLOCKWISE]:
#         fallback_img = processed_img.copy()
#         if angle is not None:
#             fallback_img = cv2.rotate(fallback_img, angle)

#         ocr_results = reader.readtext(fallback_img)
#         found_and_masked = False

#         for (bbox, text, prob) in ocr_results:
#             clean_text = text.replace(" ", "")
#             if re.search(r"\d{4}\s\d{4}\s\d{4}", text) or (len(clean_text) == 12 and clean_text.isdigit()):
#                 print(f"✅ Aadhaar found in Fallback Mode at angle {0 if angle is None else angle}")
                
#                 (tl, tr, br, bl) = bbox
#                 mx_start, my_start = int(tl[0]), int(tl[1])
#                 mx_end, my_end = int(br[0]), int(br[1])
                
#                 # --- IMPROVED BACKGROUND SAMPLING ---
#                 # Safely sample inside the card boundaries
#                 y_sample = min(fallback_img.shape[0]-1, my_start + max(1, (my_end - my_start) // 4))
#                 x_sample = min(fallback_img.shape[1]-1, mx_start + 2)
#                 bg_color = [int(c) for c in fallback_img[y_sample, x_sample]]
                
#                 total_width = mx_end - mx_start
#                 box_height = my_end - my_start
#                 available_mask_width = int(total_width * 0.64)
#                 new_x_end = mx_start + available_mask_width
                
#                 cv2.rectangle(fallback_img, (mx_start, my_start), (new_x_end, my_end), bg_color, -1)
                
#                 mask_text = "xxxxxxxx"
#                 font = cv2.FONT_HERSHEY_DUPLEX # Cleaner font
#                 current_scale = box_height / 30.0
#                 while True:
#                     (tw, th), _ = cv2.getTextSize(mask_text, font, current_scale, 1)
#                     if tw <= available_mask_width * 0.95 or current_scale < 0.1: 
#                         break
#                     current_scale -= 0.05
                    
#                 y_center = my_start + (box_height // 2) + (th // 2) - int(box_height * 0.05)
#                 cv2.putText(fallback_img, mask_text, (mx_start, y_center), font, current_scale, (0, 0, 0), 1, cv2.LINE_AA)
#                 found_and_masked = True

#         if found_and_masked:
#             return fallback_img, True

#     return processed_img, False

# @app.route('/mask', methods=['POST'])
# def mask_image():
#     file = request.files['image']
#     img = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_COLOR)
#     p_img, found = ultimate_aadhaar_engine(img)
#     _, buf = cv2.imencode('.jpg', p_img)
#     return jsonify({"status": "success" if found else "no_aadhaar_found", "image": base64.b64encode(buf).decode('utf-8')})

# # HTML Template is omitted here for brevity but should be pasted back in your actual file
# HTML_TEMPLATE = """
# <!DOCTYPE html>
# <html lang="en">
# <head>
#     <meta charset="UTF-8">
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">
#     <title>Aadhaar Shield | Pastel Secure</title>
#     <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&display=swap" rel="stylesheet">
#     <style>
#         :root {
#             --pastel-blue: #b2e2f2;
#             --pastel-pink: #ffb7b2;
#             --pastel-purple: #e2cfea;
#             --pastel-bg: #fdfafe;
#             --text-dark: #2d3436;
#             --glass: rgba(255, 255, 255, 0.7);
#         }
        
#         * { box-sizing: border-box; margin: 0; padding: 0; }
        
#         body { 
#             font-family: 'Outfit', sans-serif; 
#             background: linear-gradient(135deg, var(--pastel-bg), #fff5f7); 
#             color: var(--text-dark); 
#             min-height: 100vh;
#             display: flex;
#             flex-direction: column;
#             align-items: center;
#             padding: 40px 20px;
#         }

#         .container { max-width: 1000px; width: 100%; }

#         header { text-align: center; margin-bottom: 50px; }
#         header h1 { 
#             font-size: 3.5rem; 
#             font-weight: 600;
#             background: linear-gradient(to right, #6c5ce7, #ff7675);
#             -webkit-background-clip: text;
#             -webkit-fill-color: transparent;
#             margin-bottom: 10px;
#         }
#         header p { color: #636e72; font-size: 1.1rem; }

#         .main-card { 
#             background: var(--glass);
#             backdrop-filter: blur(15px);
#             border-radius: 30px;
#             padding: 50px;
#             border: 1px solid rgba(255, 255, 255, 0.4);
#             box-shadow: 0 15px 35px rgba(0,0,0,0.05);
#             transition: transform 0.3s ease;
#         }

#         .upload-area {
#             border: 3px dashed var(--pastel-blue);
#             border-radius: 20px;
#             padding: 60px 20px;
#             text-align: center;
#             cursor: pointer;
#             transition: all 0.3s ease;
#             background: rgba(178, 226, 242, 0.05);
#         }
#         .upload-area:hover {
#             border-color: #74b9ff;
#             background: rgba(178, 226, 242, 0.15);
#             transform: translateY(-2px);
#         }
#         .upload-area .icon { font-size: 60px; margin-bottom: 15px; display: block; }
#         .upload-area h3 { font-weight: 600; color: #0984e3; margin-bottom: 10px; }

#         .btn {
#             background: linear-gradient(135deg, #a29bfe, #81ecec);
#             color: white;
#             border: none;
#             padding: 15px 40px;
#             border-radius: 50px;
#             font-weight: 600;
#             font-size: 1rem;
#             cursor: pointer;
#             box-shadow: 0 8px 20px rgba(162, 155, 254, 0.3);
#             transition: all 0.3s ease;
#             margin-top: 25px;
#         }
#         .btn:hover {
#             transform: scale(1.05);
#             box-shadow: 0 10px 25px rgba(162, 155, 254, 0.4);
#         }

#         .result-section { display: none; margin-top: 50px; animation: fadeIn 0.8s ease; }
#         @keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }

#         .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 30px; }
#         .preview-box { background: white; border-radius: 20px; padding: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.03); }
#         .preview-box h4 { margin-bottom: 15px; color: #b2bec3; font-weight: 400; text-transform: uppercase; font-size: 0.8rem; letter-spacing: 1px; text-align: center; }
#         img { width: 100%; border-radius: 12px; }

#         .loader {
#             display: none;
#             width: 50px;
#             height: 50px;
#             border: 5px solid var(--pastel-blue);
#             border-top: 5px solid #a29bfe;
#             border-radius: 50%;
#             animation: spin 1s linear infinite;
#             margin: 30px auto;
#         }
#         @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

#         .footer { margin-top: 50px; color: #b2bec3; font-size: 0.9rem; }
#     </style>
# </head>
# <body>
#     <div class="container">
#         <header>
#             <h1>Aadhaar Shield</h1>
#             <p>Smart, Secure, and Seamless Information Protection</p>
#         </header>

#         <div class="main-card">
#             <div class="upload-area" id="dropArea" onclick="document.getElementById('fileInput').click()">
#                 <span class="icon">🌸</span>
#                 <h3>Upload Your Aadhaar Card</h3>
#                 <p>Drag and drop or click to browse</p>
#                 <input type="file" id="fileInput" style="display:none" accept="image/*">
#                 <button class="btn">Select Image</button>
#             </div>

#             <div class="loader" id="loader"></div>

#             <div class="result-section" id="resultArea">
#                 <div class="grid">
#                     <div class="preview-box">
#                         <h4>Original Document</h4>
#                         <img id="origImg">
#                     </div>
#                     <div class="preview-box">
#                         <h4>Shielded Result</h4>
#                         <img id="maskedImg">
#                         <button class="btn" id="dlBtn" style="width:100%; margin-top: 15px;">✨ Download Shielded Card</button>
#                     </div>
#                 </div>
#             </div>
#         </div>

#         <div class="footer">
#             Built with ❤️ for Privacy
#         </div>
#     </div>

#     <script>
#         const fileInput = document.getElementById('fileInput');
#         const loader = document.getElementById('loader');
#         const resultArea = document.getElementById('resultArea');

#         fileInput.onchange = async (e) => {
#             const file = e.target.files[0];
#             if (!file) return;

#             // Preview original
#             const reader = new FileReader();
#             reader.onload = (ev) => document.getElementById('origImg').src = ev.target.result;
#             reader.readAsDataURL(file);

#             // Process
#             loader.style.display = 'block';
#             resultArea.style.display = 'none';

#             const fd = new FormData();
#             fd.append('image', file);

#             try {
#                 const res = await fetch('/mask', { method: 'POST', body: fd });
#                 const data = await res.json();

#                 if (data.image) {
#                     const maskedData = 'data:image/jpeg;base64,' + data.image;
#                     document.getElementById('maskedImg').src = maskedData;
#                     resultArea.style.display = 'block';

#                     document.getElementById('dlBtn').onclick = () => {
#                         const a = document.createElement('a');
#                         a.href = maskedData;
#                         a.download = 'aadhaar_shielded.jpg';
#                         a.click();
#                     };
#                 } else {
#                     alert('Could not find Aadhaar number in this image.');
#                 }
#             } catch (error) {
#                 alert('Connection Error. Please check if server is running.');
#             } finally {
#                 loader.style.display = 'none';
#             }
#         };
#     </script>
# </body>
# </html>
# """

# @app.route('/')
# def home(): return render_template_string(HTML_TEMPLATE)

# if __name__ == '__main__':
#     # PORT 7860 is required for Hugging Face Spaces
#     app.run(host='0.0.0.0', port=7860)
# #####
# import cv2
# import easyocr
# import re
# import numpy as np
# import base64
# import io
# import os
# from flask import Flask, request, jsonify, render_template_string
# from flask_cors import CORS
# from ultralytics import YOLO
# from PIL import Image

# # Initialize Flask App
# app = Flask(__name__)
# CORS(app)

# # --- ENGINE INITIALIZATION ---
# print("🚀 Initializing Aadhaar Shield Engines... (This may take a minute)")
# try:
#     # Defaulting to yolo26n.pt
#     model_path = "yolo26n.pt"
#     model = YOLO(model_path)
#     reader = easyocr.Reader(['en'], gpu=False)
#     print(f"✅ Engines Loaded Successfully! using {model_path}")
# except Exception as e:
#     print(f"❌ Error loading engines: {e}")

# def ultimate_aadhaar_engine(img):
#     """
#     PORTED LOGIC: Fixes rotation tracking so masking accurately applies.
#     """
#     if img is None:
#         return None, False

#     processed_img = img.copy()

#     # --- STEP 1: Custom YOLO Detection ---
#     results = model.predict(processed_img, conf=0.3, verbose=False)

#     # --- STEP 2: Multi-Box Verification Loop ---
#     for i, box in enumerate(results[0].boxes):
#         x1, y1, x2, y2 = map(int, box.xyxy[0])
#         # Safety bounds
#         x1, y1 = max(0, x1), max(0, y1)
#         x2, y2 = min(processed_img.shape[1], x2), min(processed_img.shape[0], y2)

#         base_crop = processed_img[y1:y2, x1:x2]

#         print(f"Checking Box #{i+1} (Confidence: {box.conf[0]:.2f})...")

#         # --- STEP 3: Orientation Correction (0, 90, 180, 270) ---
#         for angle in [None, cv2.ROTATE_90_CLOCKWISE, cv2.ROTATE_180, cv2.ROTATE_90_COUNTERCLOCKWISE]:
#             test_crop = base_crop.copy()
#             if angle is not None:
#                 test_crop = cv2.rotate(test_crop, angle)

#             # OCR Check
#             ocr_results = reader.readtext(test_crop)

#             # --- STAGE 4: FIND & MASK AADHAAR ---
#             found_and_masked = False
#             for (bbox, text, prob) in ocr_results:
#                 clean_text = text.replace(" ", "")
#                 if re.search(r"\d{4}\s\d{4}\s\d{4}", text) or (len(clean_text) == 12 and clean_text.isdigit()):
#                     print(f"✅ Aadhaar found in Box #{i+1} at angle {0 if angle is None else angle}")

#                     (tl, tr, br, bl) = bbox
#                     mx_start, my_start = int(tl[0]), int(tl[1])
#                     mx_end, my_end = int(br[0]), int(br[1])

#                     # Safely sample inside the card boundaries
#                     y_sample = min(test_crop.shape[0]-1, my_start + max(1, (my_end - my_start) // 4))
#                     x_sample = min(test_crop.shape[1]-1, mx_start + 2)
#                     bg_color = [int(c) for c in test_crop[y_sample, x_sample]]

#                     # MASKING LOGIC 
#                     total_width = mx_end - mx_start
#                     box_height = my_end - my_start
#                     available_mask_width = int(total_width * 0.64)
#                     new_x_end = mx_start + available_mask_width

#                     cv2.rectangle(test_crop, (mx_start, my_start), (new_x_end, my_end), bg_color, -1)

#                     mask_text = "xxxxxxxx"
#                     font = cv2.FONT_HERSHEY_DUPLEX
#                     current_scale = box_height / 30.0
#                     while True:
#                         (tw, th), _ = cv2.getTextSize(mask_text, font, current_scale, 1)
#                         if tw <= available_mask_width * 0.95 or current_scale < 0.1:
#                             break
#                         current_scale -= 0.05

#                     y_center = my_start + (box_height // 2) + (th // 2) - int(box_height * 0.05)
#                     cv2.putText(test_crop, mask_text, (mx_start, y_center),
#                                 font, current_scale, (0, 0, 0), 1, cv2.LINE_AA)

#                     found_and_masked = True

#             if found_and_masked:
#                 # To prevent coordinate shifting when pasting the box back into the main image,
#                 # we must invert the rotation of the crop AFTER we draw the mask on it!
#                 if angle == cv2.ROTATE_90_CLOCKWISE:
#                     test_crop = cv2.rotate(test_crop, cv2.ROTATE_90_COUNTERCLOCKWISE)
#                 elif angle == cv2.ROTATE_180:
#                     test_crop = cv2.rotate(test_crop, cv2.ROTATE_180)
#                 elif angle == cv2.ROTATE_90_COUNTERCLOCKWISE:
#                     test_crop = cv2.rotate(test_crop, cv2.ROTATE_90_CLOCKWISE)
                
#                 # Now that it's un-rotated, paste it back in its exact original spot
#                 processed_img[y1:y2, x1:x2] = test_crop
#                 return processed_img, True

#     # --- FINAL ROBUST FALLBACK (If YOLO fails or misses) ---
#     print("⚠️ YOLO missed detection. Running full-image deep search...")
#     for angle in [None, cv2.ROTATE_90_CLOCKWISE, cv2.ROTATE_180, cv2.ROTATE_90_COUNTERCLOCKWISE]:
#         fallback_img = processed_img.copy()
#         if angle is not None:
#             fallback_img = cv2.rotate(fallback_img, angle)

#         ocr_results = reader.readtext(fallback_img)
#         found_and_masked = False

#         for (bbox, text, prob) in ocr_results:
#             clean_text = text.replace(" ", "")
#             if re.search(r"\d{4}\s\d{4}\s\d{4}", text) or (len(clean_text) == 12 and clean_text.isdigit()):
#                 print(f"✅ Aadhaar found in Fallback Mode at angle {0 if angle is None else angle}")
                
#                 (tl, tr, br, bl) = bbox
#                 mx_start, my_start = int(tl[0]), int(tl[1])
#                 mx_end, my_end = int(br[0]), int(br[1])
                
#                 y_sample = min(fallback_img.shape[0]-1, my_start + max(1, (my_end - my_start) // 4))
#                 x_sample = min(fallback_img.shape[1]-1, mx_start + 2)
#                 bg_color = [int(c) for c in fallback_img[y_sample, x_sample]]
                
#                 total_width = mx_end - mx_start
#                 box_height = my_end - my_start
#                 available_mask_width = int(total_width * 0.64)
#                 new_x_end = mx_start + available_mask_width
                
#                 cv2.rectangle(fallback_img, (mx_start, my_start), (new_x_end, my_end), bg_color, -1)
                
#                 mask_text = "xxxxxxxx"
#                 font = cv2.FONT_HERSHEY_DUPLEX
#                 current_scale = box_height / 30.0
#                 while True:
#                     (tw, th), _ = cv2.getTextSize(mask_text, font, current_scale, 1)
#                     if tw <= available_mask_width * 0.95 or current_scale < 0.1: 
#                         break
#                     current_scale -= 0.05
                    
#                 y_center = my_start + (box_height // 2) + (th // 2) - int(box_height * 0.05)
#                 cv2.putText(fallback_img, mask_text, (mx_start, y_center), font, current_scale, (0, 0, 0), 1, cv2.LINE_AA)
#                 found_and_masked = True

#         if found_and_masked:
#             # Un-rotate the full image before returning it to the user
#             if angle == cv2.ROTATE_90_CLOCKWISE:
#                 fallback_img = cv2.rotate(fallback_img, cv2.ROTATE_90_COUNTERCLOCKWISE)
#             elif angle == cv2.ROTATE_180:
#                 fallback_img = cv2.rotate(fallback_img, cv2.ROTATE_180)
#             elif angle == cv2.ROTATE_90_COUNTERCLOCKWISE:
#                 fallback_img = cv2.rotate(fallback_img, cv2.ROTATE_90_CLOCKWISE)
            
#             return fallback_img, True

#     return processed_img, False

# @app.route('/mask', methods=['POST'])
# def mask_image():
#     file = request.files['image']
#     img = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_COLOR)
#     p_img, found = ultimate_aadhaar_engine(img)
#     _, buf = cv2.imencode('.jpg', p_img)
#     return jsonify({"status": "success" if found else "no_aadhaar_found", "image": base64.b64encode(buf).decode('utf-8')})

# # HTML TEMPLATE
# HTML_TEMPLATE = """
# <!DOCTYPE html>
# <html lang="en">
# <head>
#     <meta charset="UTF-8">
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">
#     <title>Aadhaar Shield | Pastel Secure</title>
#     <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&display=swap" rel="stylesheet">
#     <style>
#         :root {
#             --pastel-blue: #b2e2f2;
#             --pastel-pink: #ffb7b2;
#             --pastel-purple: #e2cfea;
#             --pastel-bg: #fdfafe;
#             --text-dark: #2d3436;
#             --glass: rgba(255, 255, 255, 0.7);
#         }
        
#         * { box-sizing: border-box; margin: 0; padding: 0; }
        
#         body { 
#             font-family: 'Outfit', sans-serif; 
#             background: linear-gradient(135deg, var(--pastel-bg), #fff5f7); 
#             color: var(--text-dark); 
#             min-height: 100vh;
#             display: flex;
#             flex-direction: column;
#             align-items: center;
#             padding: 40px 20px;
#         }

#         .container { max-width: 1000px; width: 100%; }

#         header { text-align: center; margin-bottom: 50px; }
#         header h1 { 
#             font-size: 3.5rem; 
#             font-weight: 600;
#             background: linear-gradient(to right, #6c5ce7, #ff7675);
#             -webkit-background-clip: text;
#             -webkit-fill-color: transparent;
#             margin-bottom: 10px;
#         }
#         header p { color: #636e72; font-size: 1.1rem; }

#         .main-card { 
#             background: var(--glass);
#             backdrop-filter: blur(15px);
#             border-radius: 30px;
#             padding: 50px;
#             border: 1px solid rgba(255, 255, 255, 0.4);
#             box-shadow: 0 15px 35px rgba(0,0,0,0.05);
#             transition: transform 0.3s ease;
#         }

#         .upload-area {
#             border: 3px dashed var(--pastel-blue);
#             border-radius: 20px;
#             padding: 60px 20px;
#             text-align: center;
#             cursor: pointer;
#             transition: all 0.3s ease;
#             background: rgba(178, 226, 242, 0.05);
#         }
#         .upload-area:hover {
#             border-color: #74b9ff;
#             background: rgba(178, 226, 242, 0.15);
#             transform: translateY(-2px);
#         }
#         .upload-area .icon { font-size: 60px; margin-bottom: 15px; display: block; }
#         .upload-area h3 { font-weight: 600; color: #0984e3; margin-bottom: 10px; }

#         .btn {
#             background: linear-gradient(135deg, #a29bfe, #81ecec);
#             color: white;
#             border: none;
#             padding: 15px 40px;
#             border-radius: 50px;
#             font-weight: 600;
#             font-size: 1rem;
#             cursor: pointer;
#             box-shadow: 0 8px 20px rgba(162, 155, 254, 0.3);
#             transition: all 0.3s ease;
#             margin-top: 25px;
#         }
#         .btn:hover {
#             transform: scale(1.05);
#             box-shadow: 0 10px 25px rgba(162, 155, 254, 0.4);
#         }

#         .result-section { display: none; margin-top: 50px; animation: fadeIn 0.8s ease; }
#         @keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }

#         .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 30px; }
#         .preview-box { background: white; border-radius: 20px; padding: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.03); }
#         .preview-box h4 { margin-bottom: 15px; color: #b2bec3; font-weight: 400; text-transform: uppercase; font-size: 0.8rem; letter-spacing: 1px; text-align: center; }
#         img { width: 100%; border-radius: 12px; }

#         .loader {
#             display: none;
#             width: 50px;
#             height: 50px;
#             border: 5px solid var(--pastel-blue);
#             border-top: 5px solid #a29bfe;
#             border-radius: 50%;
#             animation: spin 1s linear infinite;
#             margin: 30px auto;
#         }
#         @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

#         .footer { margin-top: 50px; color: #b2bec3; font-size: 0.9rem; }
#     </style>
# </head>
# <body>
#     <div class="container">
#         <header>
#             <h1>Aadhaar Shield</h1>
#             <p>Smart, Secure, and Seamless Information Protection</p>
#         </header>

#         <div class="main-card">
#             <div class="upload-area" id="dropArea" onclick="document.getElementById('fileInput').click()">
#                 <span class="icon">🌸</span>
#                 <h3>Upload Your Aadhaar Card</h3>
#                 <p>Drag and drop or click to browse</p>
#                 <input type="file" id="fileInput" style="display:none" accept="image/*">
#                 <button class="btn">Select Image</button>
#             </div>

#             <div class="loader" id="loader"></div>

#             <div class="result-section" id="resultArea">
#                 <div class="grid">
#                     <div class="preview-box">
#                         <h4>Original Document</h4>
#                         <img id="origImg">
#                     </div>
#                     <div class="preview-box">
#                         <h4>Shielded Result</h4>
#                         <img id="maskedImg">
#                         <button class="btn" id="dlBtn" style="width:100%; margin-top: 15px;">✨ Download Shielded Card</button>
#                     </div>
#                 </div>
#             </div>
#         </div>

#         <div class="footer">
#             Built with ❤️ for Privacy
#         </div>
#     </div>

#     <script>
#         const fileInput = document.getElementById('fileInput');
#         const loader = document.getElementById('loader');
#         const resultArea = document.getElementById('resultArea');

#         fileInput.onchange = async (e) => {
#             const file = e.target.files[0];
#             if (!file) return;

#             // Preview original
#             const reader = new FileReader();
#             reader.onload = (ev) => document.getElementById('origImg').src = ev.target.result;
#             reader.readAsDataURL(file);

#             // Process
#             loader.style.display = 'block';
#             resultArea.style.display = 'none';

#             const fd = new FormData();
#             fd.append('image', file);

#             try {
#                 const res = await fetch('/mask', { method: 'POST', body: fd });
#                 const data = await res.json();

#                 if (data.image) {
#                     const maskedData = 'data:image/jpeg;base64,' + data.image;
#                     document.getElementById('maskedImg').src = maskedData;
#                     resultArea.style.display = 'block';

#                     document.getElementById('dlBtn').onclick = () => {
#                         const a = document.createElement('a');
#                         a.href = maskedData;
#                         a.download = 'aadhaar_shielded.jpg';
#                         a.click();
#                     };
#                 } else {
#                     alert('Could not find Aadhaar number in this image.');
#                 }
#             } catch (error) {
#                 alert('Connection Error. Please check if server is running.');
#             } finally {
#                 loader.style.display = 'none';
#             }
#         };
#     </script>
# </body>
# </html>
# """

# @app.route('/')
# def home(): return render_template_string(HTML_TEMPLATE)

# if __name__ == '__main__':
#     # PORT 7860 is required for Hugging Face Spaces
#     app.run(host='0.0.0.0', port=7860)
import cv2
import easyocr
import re
import numpy as np
import base64
import io
import os
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from ultralytics import YOLO

# Initialize Flask App
app = Flask(__name__)
CORS(app)

# --- ENGINE INITIALIZATION ---
print("🚀 Initializing Aadhaar Shield Engines... (This may take a minute)")
try:
    model_path = "yolo26n.pt"
    model = YOLO(model_path)
    reader = easyocr.Reader(['en'], gpu=False)
    print(f"✅ Engines Loaded Successfully! using {model_path}")
except Exception as e:
    print(f"❌ Error loading engines: {e}")


def preprocess_for_ocr(image):
    """
    ALTERNATIVE METHOD: Instead of harsh black/white thresholding, 
    we upscale the image by 200% to make the tiny text HUGE, and 
    apply a gentle Sharpening matrix so the edges pop out of the shadows!
    """
    # 1. Upscale by 200% (Makes tiny numbers readable on full 12MP photos)
    zoomed = cv2.resize(image, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
    
    # 2. Sharpening Filter (enhances edges without destroying the colors/shadows)
    kernel = np.array([[-1,-1,-1], 
                       [-1, 9,-1],
                       [-1,-1,-1]])
    sharpened = cv2.filter2D(zoomed, -1, kernel)
    
    # 3. Grayscale
    gray = cv2.cvtColor(sharpened, cv2.COLOR_BGR2GRAY)
    return gray


def ultimate_aadhaar_engine(img):
    if img is None:
        return None, False

    original_img = img.copy()
    
    # Test all 4 rotations
    for master_angle in [None, cv2.ROTATE_90_CLOCKWISE, cv2.ROTATE_180, cv2.ROTATE_90_COUNTERCLOCKWISE]:
        
        working_img = original_img.copy()
        if master_angle is not None:
            working_img = cv2.rotate(working_img, master_angle)
            
        results = model.predict(working_img, conf=0.1, verbose=False)
        
        for i, box in enumerate(results[0].boxes):
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(working_img.shape[1], x2), min(working_img.shape[0], y2)

            base_crop = working_img[y1:y2, x1:x2]
            
            for crop_angle in [None, cv2.ROTATE_90_CLOCKWISE, cv2.ROTATE_180, cv2.ROTATE_90_COUNTERCLOCKWISE]:
                test_crop = base_crop.copy()
                if crop_angle is not None:
                    test_crop = cv2.rotate(test_crop, crop_angle)

                # DUAL-PASS OCR
                for is_preprocessed, img_variant in [(False, test_crop), (True, preprocess_for_ocr(test_crop))]:
                    
                    # Alternative Method: We explicitly tell the AI to adjust contrast internally (`adjust_contrast=True`)
                    ocr_results = reader.readtext(img_variant, adjust_contrast=True, text_threshold=0.6)
                    found_and_masked = False
                    
                    for (bbox, text, prob) in ocr_results:
                        clean_text = text.replace(" ", "")
                        if re.search(r"\d{4}\s*[-]?\s*\d{4}\s*[-]?\s*\d{4}", text) or (len(clean_text) == 12 and clean_text.isdigit()):
                            
                            x_coords = [int(pt[0]) for pt in bbox]
                            y_coords = [int(pt[1]) for pt in bbox]
                            
                            # If we upscaled it by 200%, we must divide the coordinates by 2 to draw the mask on the normal image!
                            scale_factor = 2.0 if is_preprocessed else 1.0
                            mx_start, mx_end = int(min(x_coords)/scale_factor), int(max(x_coords)/scale_factor)
                            my_start, my_end = int(min(y_coords)/scale_factor), int(max(y_coords)/scale_factor)
                            
                            total_width = mx_end - mx_start
                            box_height = my_end - my_start

                            y_sample = min(test_crop.shape[0]-1, my_start + max(1, box_height // 4))
                            x_sample = min(test_crop.shape[1]-1, mx_start + 2)
                            bg_color = [int(c) for c in test_crop[y_sample, x_sample]]

                            if total_width > box_height:
                                available_mask_width = int(total_width * 0.64)
                                new_x_end = mx_start + available_mask_width
                                cv2.rectangle(test_crop, (mx_start, my_start), (new_x_end, my_end), bg_color, -1)

                                mask_text = "xxxxxxxx"
                                font = cv2.FONT_HERSHEY_DUPLEX
                                current_scale = box_height / 30.0
                                while True:
                                    (tw, th), _ = cv2.getTextSize(mask_text, font, current_scale, 1)
                                    if tw <= available_mask_width * 0.95 or current_scale < 0.1:
                                        break
                                    current_scale -= 0.05

                                y_center = my_start + (box_height // 2) + (th // 2) - int(box_height * 0.05)
                                cv2.putText(test_crop, mask_text, (mx_start, y_center), font, current_scale, (0, 0, 0), 1, cv2.LINE_AA)
                            else:
                                available_mask_height = int(box_height * 0.64)
                                new_y_end = my_start + available_mask_height
                                cv2.rectangle(test_crop, (mx_start, my_start), (mx_end, new_y_end), bg_color, -1)

                            found_and_masked = True
                            break 
                    
                    if found_and_masked:
                        break 
                
                # Un-spin
                if found_and_masked:
                    if crop_angle == cv2.ROTATE_90_CLOCKWISE:
                        test_crop = cv2.rotate(test_crop, cv2.ROTATE_90_COUNTERCLOCKWISE)
                    elif crop_angle == cv2.ROTATE_180:
                        test_crop = cv2.rotate(test_crop, cv2.ROTATE_180)
                    elif crop_angle == cv2.ROTATE_90_COUNTERCLOCKWISE:
                        test_crop = cv2.rotate(test_crop, cv2.ROTATE_90_CLOCKWISE)
                    
                    working_img[y1:y2, x1:x2] = test_crop
                    
                    if master_angle == cv2.ROTATE_90_CLOCKWISE:
                        working_img = cv2.rotate(working_img, cv2.ROTATE_90_COUNTERCLOCKWISE)
                    elif master_angle == cv2.ROTATE_180:
                        working_img = cv2.rotate(working_img, cv2.ROTATE_180)
                    elif master_angle == cv2.ROTATE_90_COUNTERCLOCKWISE:
                        working_img = cv2.rotate(working_img, cv2.ROTATE_90_CLOCKWISE)
                        
                    return working_img, True

    # --- FINAL ROBUST FALLBACK ---
    print("⚠️ YOLO missed detection completely.")
    for master_angle in [None, cv2.ROTATE_90_CLOCKWISE, cv2.ROTATE_180, cv2.ROTATE_90_COUNTERCLOCKWISE]:
        working_img = original_img.copy()
        if master_angle is not None:
            working_img = cv2.rotate(working_img, master_angle)

        for is_preprocessed, img_variant in [(False, working_img), (True, preprocess_for_ocr(working_img))]:
            ocr_results = reader.readtext(img_variant, adjust_contrast=True, text_threshold=0.6)
            found_and_masked = False

            for (bbox, text, prob) in ocr_results:
                clean_text = text.replace(" ", "")
                if re.search(r"\d{4}\s*[-]?\s*\d{4}\s*[-]?\s*\d{4}", text) or (len(clean_text) == 12 and clean_text.isdigit()):
                    
                    x_coords = [int(pt[0]) for pt in bbox]
                    y_coords = [int(pt[1]) for pt in bbox]
                    
                    # Downscale coordinates if we used the 200% Zoomed image
                    scale_factor = 2.0 if is_preprocessed else 1.0
                    mx_start, mx_end = int(min(x_coords)/scale_factor), int(max(x_coords)/scale_factor)
                    my_start, my_end = int(min(y_coords)/scale_factor), int(max(y_coords)/scale_factor)
                    
                    total_width = mx_end - mx_start
                    box_height = my_end - my_start

                    y_sample = min(working_img.shape[0]-1, my_start + max(1, box_height // 4))
                    x_sample = min(working_img.shape[1]-1, mx_start + 2)
                    bg_color = [int(c) for c in working_img[y_sample, x_sample]]
                    
                    if total_width > box_height:
                        available_mask_width = int(total_width * 0.64)
                        new_x_end = mx_start + available_mask_width
                        cv2.rectangle(working_img, (mx_start, my_start), (new_x_end, my_end), bg_color, -1)
                        
                        mask_text = "xxxxxxxx"
                        font = cv2.FONT_HERSHEY_DUPLEX
                        current_scale = box_height / 30.0
                        while True:
                            (tw, th), _ = cv2.getTextSize(mask_text, font, current_scale, 1)
                            if tw <= available_mask_width * 0.95 or current_scale < 0.1: 
                                break
                            current_scale -= 0.05
                            
                        y_center = my_start + (box_height // 2) + (th // 2) - int(box_height * 0.05)
                        cv2.putText(working_img, mask_text, (mx_start, y_center), font, current_scale, (0, 0, 0), 1, cv2.LINE_AA)
                    else:
                        available_mask_height = int(box_height * 0.64)
                        new_y_end = my_start + available_mask_height
                        cv2.rectangle(working_img, (mx_start, my_start), (mx_end, new_y_end), bg_color, -1)

                    found_and_masked = True
                    break
                    
            if found_and_masked:
                if master_angle == cv2.ROTATE_90_CLOCKWISE:
                    working_img = cv2.rotate(working_img, cv2.ROTATE_90_COUNTERCLOCKWISE)
                elif master_angle == cv2.ROTATE_180:
                    working_img = cv2.rotate(working_img, cv2.ROTATE_180)
                elif master_angle == cv2.ROTATE_90_COUNTERCLOCKWISE:
                    working_img = cv2.rotate(working_img, cv2.ROTATE_90_CLOCKWISE)
                return working_img, True

    return original_img, False

@app.route('/mask', methods=['POST'])
def mask_image():
    file = request.files['image']
    img = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_COLOR)
    p_img, found = ultimate_aadhaar_engine(img)
    _, buf = cv2.imencode('.jpg', p_img)
    return jsonify({"status": "success" if found else "no_aadhaar_found", "image": base64.b64encode(buf).decode('utf-8')})

# --- HTML TEMPLATE EXACTLY THE SAME... ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Aadhaar Shield | Pastel Secure</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&display=swap" rel="stylesheet">
    <style>
        :root {
            --pastel-blue: #b2e2f2;
            --pastel-pink: #ffb7b2;
            --pastel-purple: #e2cfea;
            --pastel-bg: #fdfafe;
            --text-dark: #2d3436;
            --glass: rgba(255, 255, 255, 0.7);
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'Outfit', sans-serif; background: linear-gradient(135deg, var(--pastel-bg), #fff5f7); color: var(--text-dark); min-height: 100vh; display: flex; flex-direction: column; align-items: center; padding: 40px 20px; }
        .container { max-width: 1000px; width: 100%; }
        header { text-align: center; margin-bottom: 50px; }
        header h1 { font-size: 3.5rem; font-weight: 600; background: linear-gradient(to right, #6c5ce7, #ff7675); -webkit-background-clip: text; -webkit-fill-color: transparent; margin-bottom: 10px; }
        header p { color: #636e72; font-size: 1.1rem; }
        .main-card { background: var(--glass); backdrop-filter: blur(15px); border-radius: 30px; padding: 50px; border: 1px solid rgba(255, 255, 255, 0.4); box-shadow: 0 15px 35px rgba(0,0,0,0.05); transition: transform 0.3s ease; }
        .upload-area { border: 3px dashed var(--pastel-blue); border-radius: 20px; padding: 60px 20px; text-align: center; cursor: pointer; transition: all 0.3s ease; background: rgba(178, 226, 242, 0.05); }
        .upload-area:hover { border-color: #74b9ff; background: rgba(178, 226, 242, 0.15); transform: translateY(-2px); }
        .upload-area .icon { font-size: 60px; margin-bottom: 15px; display: block; }
        .upload-area h3 { font-weight: 600; color: #0984e3; margin-bottom: 10px; }
        .btn { background: linear-gradient(135deg, #a29bfe, #81ecec); color: white; border: none; padding: 15px 40px; border-radius: 50px; font-weight: 600; font-size: 1rem; cursor: pointer; box-shadow: 0 8px 20px rgba(162, 155, 254, 0.3); transition: all 0.3s ease; margin-top: 25px; }
        .btn:hover { transform: scale(1.05); box-shadow: 0 10px 25px rgba(162, 155, 254, 0.4); }
        .result-section { display: none; margin-top: 50px; animation: fadeIn 0.8s ease; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 30px; }
        .preview-box { background: white; border-radius: 20px; padding: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.03); }
        .preview-box h4 { margin-bottom: 15px; color: #b2bec3; font-weight: 400; text-transform: uppercase; font-size: 0.8rem; letter-spacing: 1px; text-align: center; }
        img { width: 100%; border-radius: 12px; }
        .loader { display: none; width: 50px; height: 50px; border: 5px solid var(--pastel-blue); border-top: 5px solid #a29bfe; border-radius: 50%; animation: spin 1s linear infinite; margin: 30px auto; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .footer { margin-top: 50px; color: #b2bec3; font-size: 0.9rem; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Aadhaar Shield</h1>
            <p>Smart, Secure, and Seamless Information Protection</p>
        </header>

        <div class="main-card">
            <div class="upload-area" id="dropArea" onclick="document.getElementById('fileInput').click()">
                <span class="icon">🌸</span>
                <h3>Upload Your Aadhaar Card</h3>
                <p>Drag and drop or click to browse</p>
                <input type="file" id="fileInput" style="display:none" accept="image/*">
                <button class="btn">Select Image</button>
            </div>

            <div class="loader" id="loader"></div>

            <div class="result-section" id="resultArea">
                <div class="grid">
                    <div class="preview-box">
                        <h4>Original Document</h4>
                        <img id="origImg">
                    </div>
                    <div class="preview-box">
                        <h4>Shielded Result</h4>
                        <img id="maskedImg">
                        <button class="btn" id="dlBtn" style="width:100%; margin-top: 15px;">✨ Download Shielded Card</button>
                    </div>
                </div>
            </div>
        </div>

        <div class="footer">
            Built with ❤️ for Privacy
        </div>
    </div>

    <script>
        const fileInput = document.getElementById('fileInput');
        const loader = document.getElementById('loader');
        const resultArea = document.getElementById('resultArea');

        fileInput.onchange = async (e) => {
            const file = e.target.files[0];
            if (!file) return;

            const reader = new FileReader();
            reader.onload = (ev) => document.getElementById('origImg').src = ev.target.result;
            reader.readAsDataURL(file);

            loader.style.display = 'block';
            resultArea.style.display = 'none';

            const fd = new FormData();
            fd.append('image', file);

            try {
                const res = await fetch('/mask', { method: 'POST', body: fd });
                const data = await res.json();

                if (data.image) {
                    const maskedData = 'data:image/jpeg;base64,' + data.image;
                    document.getElementById('maskedImg').src = maskedData;
                    resultArea.style.display = 'block';

                    document.getElementById('dlBtn').onclick = () => {
                        const a = document.createElement('a');
                        a.href = maskedData;
                        a.download = 'aadhaar_shielded.jpg';
                        a.click();
                    };
                } else {
                    alert('Could not find Aadhaar number in this image.');
                }
            } catch (error) {
                alert('Connection Error. Please check if server is running.');
            } finally {
                loader.style.display = 'none';
            }
        };
    </script>
</body>
</html>
"""

@app.route('/')
def home(): return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860)