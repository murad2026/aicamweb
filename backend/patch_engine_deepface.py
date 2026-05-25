with open('engine.py', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

old_embedding = '''# ─── Embedding ────────────────────────────────────────────────────────────────

def compute_embedding(crop_bgr):
    """Compute a compact visual embedding from a crop using histogram + HOG."""
    try:
        img = cv2.resize(crop_bgr, (64, 128))
        # Color histogram (HSV)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        hist_h = cv2.calcHist([hsv], [0], None, [32], [0, 180]).flatten()
        hist_s = cv2.calcHist([hsv], [1], None, [32], [0, 256]).flatten()
        hist_v = cv2.calcHist([hsv], [2], None, [32], [0, 256]).flatten()
        # HOG-like gradient histogram
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gx = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
        gy = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
        mag = cv2.magnitude(gx, gy)
        ang = cv2.phase(gx, gy, angleInDegrees=True)
        hist_grad, _ = np.histogram(ang.flatten(), bins=32, range=(0, 360), weights=mag.flatten())
        # Combine and normalize
        vec = np.concatenate([hist_h, hist_s, hist_v, hist_grad]).astype(np.float32)
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()
    except Exception as e:
        print(f"Embedding error: {e}")
        return None

def cosine_similarity(a, b):
    a = np.array(a, dtype=np.float32)
    b = np.array(b, dtype=np.float32)
    dot = np.dot(a, b)
    na = np.linalg.norm(a)
    nb = np.linalg.norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return float(dot / (na * nb))

SIMILARITY_THRESHOLD = 0.90  # tune this if needed'''

new_embedding = '''# ─── Embedding (DeepFace) ─────────────────────────────────────────────────────

_deepface_loaded = False

def get_deepface():
    global _deepface_loaded
    if not _deepface_loaded:
        try:
            from deepface import DeepFace as _df
            _deepface_loaded = True
            return _df
        except Exception as e:
            print(f"DeepFace load error: {e}")
            return None
    from deepface import DeepFace as _df
    return _df

def compute_embedding(crop_bgr):
    """Compute face/person embedding using DeepFace (Facenet512 model)."""
    try:
        import tempfile, os
        # Save crop to temp file
        tmp = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
        _, buf = cv2.imencode('.jpg', crop_bgr)
        tmp.write(buf.tobytes())
        tmp.close()
        df = get_deepface()
        if df is None:
            return _fallback_embedding(crop_bgr)
        result = df.represent(
            img_path=tmp.name,
            model_name="Facenet512",
            enforce_detection=False,
            detector_backend="skip"
        )
        os.unlink(tmp.name)
        if result and len(result) > 0:
            emb = result[0]["embedding"]
            vec = np.array(emb, dtype=np.float32)
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm
            return vec.tolist()
    except Exception as e:
        print(f"DeepFace embedding error: {e}")
    return _fallback_embedding(crop_bgr)

def _fallback_embedding(crop_bgr):
    """Fallback: color histogram if DeepFace fails."""
    try:
        img = cv2.resize(crop_bgr, (64, 128))
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        h = cv2.calcHist([hsv], [0], None, [64], [0, 180]).flatten()
        s = cv2.calcHist([hsv], [1], None, [64], [0, 256]).flatten()
        vec = np.concatenate([h, s]).astype(np.float32)
        norm = np.linalg.norm(vec)
        if norm > 0: vec = vec / norm
        return vec.tolist()
    except:
        return None

def cosine_similarity(a, b):
    a = np.array(a, dtype=np.float32)
    b = np.array(b, dtype=np.float32)
    dot = np.dot(a, b)
    na = np.linalg.norm(a)
    nb = np.linalg.norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return float(dot / (na * nb))

SIMILARITY_THRESHOLD = 0.92  # higher threshold for DeepFace embeddings'''

if old_embedding in content:
    content = content.replace(old_embedding, new_embedding)
    with open('engine.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Done')
else:
    print('Pattern not found - checking...')
    if 'compute_embedding' in content:
        print('compute_embedding exists but pattern mismatch')
    else:
        print('compute_embedding not found at all')
