with open('engine.py', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Add buffer fields to CameraWorker.__init__
old_init = '''        self.last_frame = None
        self.error = None
        self.connected = False'''

new_init = '''        self.last_frame = None
        self.error = None
        self.connected = False
        self.detection_buffer = []  # buffer of (frame, detections) for best frame selection
        self.BUFFER_SIZE = 5        # collect 5 frames before picking best'''

# Add buffer logic in _loop - after "if in_zone_det and not self.present:"
old_present = '''            if in_zone_det and not self.present:
                self.present = True
                self.alert_count = 0

            if in_zone_det and self.present:
                if now - self.last_alert > self.COOLDOWN and self.alert_count < self.MAX_ALERTS:
                    self.last_alert = now
                    self.alert_count += 1
                    cls_names = list(set(d["class"] for d in in_zone_det))'''

new_present = '''            if in_zone_det and not self.present:
                self.present = True
                self.alert_count = 0
                self.detection_buffer = []

            # Collect frames into buffer to find best shot
            if in_zone_det and self.present:
                self.detection_buffer.append((frame.copy(), in_zone_det))
                if len(self.detection_buffer) > self.BUFFER_SIZE:
                    self.detection_buffer.pop(0)

            if in_zone_det and self.present:
                if now - self.last_alert > self.COOLDOWN and self.alert_count < self.MAX_ALERTS:
                    self.last_alert = now
                    self.alert_count += 1
                    # Pick best frame: largest total bbox area = object closest/most visible
                    best_frame = frame
                    best_dets = in_zone_det
                    if self.detection_buffer:
                        best_score = 0
                        for buf_frame, buf_dets in self.detection_buffer:
                            score = sum(d["w"] * d["h"] for d in buf_dets)
                            if score > best_score:
                                best_score = score
                                best_frame = buf_frame
                                best_dets = buf_dets
                        self.detection_buffer = []
                    in_zone_det = best_dets
                    frame = best_frame
                    cls_names = list(set(d["class"] for d in in_zone_det))'''

if old_init in content and old_present in content:
    content = content.replace(old_init, new_init)
    content = content.replace(old_present, new_present)
    with open('engine.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Done')
else:
    print('Pattern not found')
    if old_init not in content:
        print('  - init pattern missing')
    if old_present not in content:
        print('  - present pattern missing')
