from ultralytics import YOLO
import cv2

class YOLOv8_Model:
    def __init__(self, confidence_threshold=0.5):
        print("[BİLGİ] YOLOv8 Yükleniyor... Model: yolov8n.pt")
        self.model = YOLO("yolov8n.pt")
        self.threshold = confidence_threshold

    def predict(self, frame):
        results = self.model(frame, verbose=False, conf=self.threshold)[0]
        detections = []
        
        for box in results.boxes:
            conf = box.conf[0].item()
            cls_id = int(box.cls[0].item())
            class_name = self.model.names[cls_id]
            
            # --- SADECE ELMA FİLTRESİ ---
            if class_name.lower() == "apple":
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                detections.append({
                    "box": [x1, y1, x2, y2],
                    "class_name": "Elma",
                    "score": conf
                })
        return detections
        
    def draw_boxes(self, frame, results):
        drawn_frame = frame.copy()
        for res in results:
            x1, y1, x2, y2 = res["box"]
            label = f"{res['class_name']}: {res['score']:.2f}"
            cv2.rectangle(drawn_frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
            (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            cv2.rectangle(drawn_frame, (x1, y1 - 20), (x1 + w, y1), (255, 0, 0), -1)
            cv2.putText(drawn_frame, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        return drawn_frame