import torch
from torchvision.models.detection import maskrcnn_resnet50_fpn, MaskRCNN_ResNet50_FPN_Weights
import torchvision.transforms.functional as F
import cv2
import numpy as np

class MaskRCNN_Model:
    def __init__(self, confidence_threshold=0.5):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"[BİLGİ] Mask R-CNN Yükleniyor... Cihaz: {self.device}")
        
        weights = MaskRCNN_ResNet50_FPN_Weights.DEFAULT
        self.model = maskrcnn_resnet50_fpn(weights=weights)
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
                    mask = predictions['masks'][i, 0].cpu().numpy() > 0.5
                    
                    results.append({
                        "box": box,
                        "class_name": "Elma",
                        "score": score,
                        "mask": mask
                    })
        return results
        
    def draw_boxes(self, frame, results):
        drawn_frame = frame.copy()
        mask_overlay = np.zeros_like(frame, dtype=np.uint8)
        
        for res in results:
            x1, y1, x2, y2 = res["box"]
            label = f"{res['class_name']}: {res['score']:.2f}"
            mask = res["mask"]
            
            mask_overlay[mask] = [0, 0, 255]
            cv2.rectangle(drawn_frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
            (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            cv2.rectangle(drawn_frame, (x1, y1 - 20), (x1 + w, y1), (0, 0, 255), -1)
            cv2.putText(drawn_frame, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
        cv2.addWeighted(mask_overlay, 0.4, drawn_frame, 1.0, 0, drawn_frame)
        return drawn_frame