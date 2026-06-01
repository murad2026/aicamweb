import cloudinary
import cloudinary.uploader
import cv2
import tempfile
import os

cloudinary.config(
    cloud_name="dqhypnnjs",
    api_key="382958327679424",
    api_secret="-ipKS6dadmApdrh0UfXeS5U07w4",
    secure=True
)

def upload_frame(frame, camera_name):
    try:
        _, buf = cv2.imencode('.jpg', frame)
        tmp = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
        tmp.write(buf.tobytes())
        tmp.close()
        result = cloudinary.uploader.upload(
            tmp.name,
            folder="aianycamera",
            public_id=f"{camera_name}_{int(__import__('time').time())}_{__import__('random').randint(1000,9999)}",
            overwrite=True
        )
        os.unlink(tmp.name)
        return result["secure_url"]
    except Exception as e:
        print(f"❌ Cloudinary error: {e}")
        return None

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
        tmp = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
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
