with open('photo_service.py', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

new_func = '''
def upload_subject_crop(frame, camera_name):
    """Upload subject crop with AI enhancement and upscaling."""
    try:
        import cv2, tempfile, os, time
        # Upscale crop 2x before uploading for better quality
        h, w = frame.shape[:2]
        if w < 200 or h < 200:
            scale = max(200 / w, 200 / h, 2.0)
            frame = cv2.resize(frame, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_CUBIC)
        # Sharpen
        import numpy as np
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        frame = cv2.filter2D(frame, -1, kernel)
        _, buf = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
        tmp = tempfile.NamedTemporaryFile(suffix=\'.jpg\', delete=False)
        tmp.write(buf.tobytes())
        tmp.close()
        result = cloudinary.uploader.upload(
            tmp.name,
            folder="aianycamera/subjects",
            public_id=f"subject_{camera_name}_{int(time.time())}",
            overwrite=True,
            transformation=[
                {"width": 400, "height": 400, "crop": "fit"},
                {"effect": "improve:outdoor:50"},
                {"quality": "auto:best"}
            ]
        )
        os.unlink(tmp.name)
        return result["secure_url"]
    except Exception as e:
        print(f"Cloudinary subject error: {e}")
        # Fallback to regular upload
        return upload_frame(frame, camera_name)
'''

if 'upload_subject_crop' not in content:
    content += new_func
    with open('photo_service.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Done')
else:
    print('Already added')
