---
title: Masking Doc
emoji: 🌍
colorFrom: purple
colorTo: indigo
sdk: docker
pinned: false
---

# Document Masking with OCR and AI
## Overview
This project uses advanced OCR and AI detection to automatically identify and mask sensitive information in documents, specifically focusing on Aadhaar card numbers. The system combines EasyOCR for text detection, YOLO for object detection, and OpenCV for intelligent image processing to create a seamless masking effect. The process involves detecting document patterns, identifying sensitive information like Aadhaar numbers, and applying context-aware masking that preserves the document's natural appearance while protecting privacy.

## Requirements
To run this project, you'll need a machine with sufficient processing power and memory for AI model processing.

### Software
- Python 3.9 or higher
- Flask web framework
- OpenCV library
- EasyOCR library
- NumPy library
- Ultralytics YOLO
- Pillow library

You can install the required Python packages by running the following command:

```bash
pip install -r requirements.txt
```

Or install individually:
```bash
pip install flask flask-cors ultralytics easyocr opencv-python-headless numpy Pillow
```

### Hardware Requirements
- Minimum 4GB RAM (8GB recommended)
- GPU support optional but recommended for faster processing
- Sufficient storage for AI model files (~10MB)

## Installation

### 1. Download the Code
Download or clone the project files to your local machine, including:
- `app.py` - Main Flask application
- `document_masking.ipynb` - Jupyter notebook with development code
- `Dockerfile` - Container configuration
- `requirements.txt` - Python dependencies
- `yolo26n.pt` - Pre-trained YOLO model

### 2. Install Dependencies
Open a terminal or command prompt, navigate to the project directory, and run:

```bash
pip install -r requirements.txt
```

### 3. Model Setup
Ensure the YOLO model file (`yolo26n.pt`) is in the same directory as the application. The system will automatically load this model for document detection.

## Usage

### Web Application
Run the Flask application from your terminal:

```bash
python app.py
```

The application will start on `http://localhost:5000` by default. Open this URL in your web browser to access the document masking interface.

### Using the Interface
1. **Upload Image**: Click the upload area or drag-and-drop an image containing documents
2. **Automatic Processing**: The system will automatically detect and mask sensitive information
3. **Download Result**: Download the masked image with sensitive information obscured

### Jupyter Notebook
For development and testing, you can run the Jupyter notebook:

```bash
jupyter notebook document_masking.ipynb
```

This contains the development code and examples for testing the masking functionality.

## Features

### Intelligent Detection
- **OCR Text Recognition**: Uses EasyOCR to detect and read text in documents
- **Pattern Matching**: Identifies Aadhaar number patterns using regex (`\d{4}\s\d{4}\s\d{4}`)
- **YOLO Object Detection**: Detects document boundaries and regions of interest

### Smart Masking
- **Context-Aware Masking**: Samples background colors for seamless integration
- **Partial Masking**: Masks only the first 8 digits, preserving the last 4 for verification
- **Dynamic Font Scaling**: Automatically adjusts text size to fit masked areas
- **Professional Appearance**: Maintains document readability while protecting privacy

### Multi-Format Support
- Supports various image formats (JPEG, PNG, etc.)
- Handles different document orientations
- Processes multiple documents in a single image

## Troubleshooting

### Import Errors
If you see ImportError, make sure all dependencies are installed correctly:
```bash
pip install -r requirements.txt
```

### Model Loading Issues
- Ensure `yolo26n.pt` is in the correct directory
- Check if the model file is corrupted (re-download if necessary)
- Verify sufficient RAM is available for model loading

### OCR Performance
- EasyOCR may be slow without GPU acceleration
- For better performance, consider using GPU-enabled version
- Adjust confidence thresholds if detection is too sensitive/lenient

### Memory Issues
- Large images may cause memory errors
- Resize images before processing if needed
- Close other applications to free up RAM

### Docker Issues
If using Docker, ensure you have sufficient resources allocated:
```bash
docker build -t doc-masking .
docker run -p 5000:5000 doc-masking
```

## API Reference

### Endpoints
- `POST /mask` - Upload and process an image for masking
- `GET /` - Web interface
- `GET /health` - Health check endpoint

### Request Format
```json
{
  "image": "base64_encoded_image_data"
}
```

### Response Format
```json
{
  "masked_image": "base64_encoded_result",
  "detections": ["Aadhaar number detected and masked"],
  "processing_time": "2.3s"
}
```

## Configuration

### Environment Variables
- `FLASK_ENV`: Set to `development` for debug mode
- `MODEL_PATH`: Custom path to YOLO model file
- `OCR_GPU`: Enable/disable GPU for OCR (true/false)

### Customization
- Modify regex patterns in `app.py` for different document types
- Adjust masking percentage (default: 64% of detected text width)
- Change masking text and styling preferences

## License
This project is licensed under the MIT License.

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## Privacy and Security
- This tool is designed for privacy protection and educational purposes
- Processed images are not stored permanently unless explicitly saved
- Ensure compliance with local regulations when processing sensitive documents
