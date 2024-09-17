from flask import Flask, request, jsonify, render_template
import os
import pydicom

app = Flask(__name__)

# Ensure the uploads directory exists
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def get_dicom_compression_info(dicom_file):
    try:
        # Load the DICOM file
        dicom_data = pydicom.dcmread(dicom_file)
        transfer_syntax = dicom_data.file_meta.TransferSyntaxUID

        # Check for common compression schemes
        if transfer_syntax == "1.2.840.10008.1.2":  # Implicit VR Little Endian
            compression_info = "No Compression (Implicit VR Little Endian)"
        elif transfer_syntax == "1.2.840.10008.1.2.1":  # Explicit VR Little Endian
            compression_info = "No Compression (Explicit VR Little Endian)"
        elif transfer_syntax == "1.2.840.10008.1.2.4.50":  # JPEG Baseline (Process 1)
            compression_info = "JPEG Compression (Baseline)"
        elif transfer_syntax == "1.2.840.10008.1.2.4.90":  # JPEG 2000 Lossless
            compression_info = "JPEG 2000 Compression (Lossless)"
        elif transfer_syntax == "1.2.840.10008.1.2.4.91":  # JPEG 2000 Lossy
            compression_info = "JPEG 2000 Compression (Lossy)"
        else:
            compression_info = "Unknown or Uncommon Compression"

        # Return compression information
        return {
            "transfer_syntax": transfer_syntax,
            "compression_info": compression_info,
            "rows": dicom_data.Rows,
            "columns": dicom_data.Columns,
            "bits_allocated": dicom_data.BitsAllocated
        }
    except Exception as e:
        return {"error": str(e)}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file:
        # Save the file to the server
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        # Get compression details
        compression_info = get_dicom_compression_info(filepath)

        # Return the compression info as a JSON response
        return jsonify(compression_info)

if __name__ == '__main__':
    app.run(debug=True)
    
