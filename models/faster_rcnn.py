import torch
from torchvision.models.detection import fasterrcnn_resnet50_fpn, FasterRCNN_ResNet50_FPN_Weights
import torchvision.transforms.functional as F
import cv2

class FasterRCNN_Model:
    def __init__(self, confidence_threshold=0.5):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"[BİLGİ] Faster R-CNN Yükleniyor... Cihaz: {self.device}")
        
        weights = FasterRCNN_ResNet50_FPN_Weights.DEFAULT
        self.model = fasterrcnn_resnet50_fpn(weights=weights)
        self.model.to(self.device)
        self.model.eval()
        
        self.threshold = confidence_threshold
        self.categories = weights.meta["categories"]

    def predict(self, frame):
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        tensor_img = F.to_tensor(rgb_image).to(self.device)
        
        with torch.no_grad():
            predictions = self.model([tensor_img])[0]
            
        results = []
        for i in range(len(predictions['boxes'])):
            score = predictions['scores'][i].item()
            if score > self.threshold:
                class_id = predictions['labels'][i].item()
                class_name = self.categories[class_id]
                
                # --- SADECE ELMA FİLTRESİ ---
                if class_name.lower() == "apple":
                    box = predictions['boxes'][i].cpu().numpy().astype(int)
                    results.append({
                        "box": box,
                        "class_name": "Elma",
                        "score": score
                    })
        return results
        
    def draw_boxes(self, frame, results):
        drawn_frame = frame.copy()
        for res in results:
            x1, y1, x2, y2 = res["box"]
            label = f"{res['class_name']}: {res['score']:.2f}"
            cv2.rectangle(drawn_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            cv2.rectangle(drawn_frame, (x1, y1 - 20), (x1 + w, y1), (0, 255, 0), -1)
            cv2.putText(drawn_frame, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        return drawn_frame