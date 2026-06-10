import time
import cv2
import customtkinter as ctk
from PIL import Image
import gc       
import torch    
import numpy as np
from ui.sidebar_panel import SidebarPanel
from ui.video_panel import VideoPanel

from models.faster_rcnn import FasterRCNN_Model
from models.mask_rcnn import MaskRCNN_Model
from models.yolov8_model import YOLOv8_Model
from models.rt_detr_model import RTDETR_Model

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class ObjectDetectionApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Doğa ve Tarım: Nesne Tespiti Analiz Sistemi")
        self.geometry("1180x720") 
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.sidebar = SidebarPanel(self, start_callback=self.start_analysis, width=250, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        self.video_panel = VideoPanel(self, corner_radius=10)
        self.video_panel.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        self.cap = None
        self.is_running = False
        self.frame_delay = 15
        self.stream_after_id = None 
        
        self.active_model1 = None
        self.active_model2 = None
        
        # --- MODEL İSİMLERİ VE FPS TAKİP DEĞİŞKENLERİ ---
        self.model1_name = ""
        self.model2_name = ""
        self.fps_start_time = None
        self.fps_counter = 0
        self.current_fps = 0.0

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def start_analysis(self, model1, model2, source_path, source_type):
        self.is_running = False
        
        if self.stream_after_id is not None:
            self.after_cancel(self.stream_after_id)
            self.stream_after_id = None

        if self.cap is not None:
            self.cap.release()
            self.cap = None
            time.sleep(0.3)  

        self.active_model1 = None
        self.active_model2 = None
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        self.current_source_type = source_type 
        self.model1_name = model1
        self.model2_name = model2
        
        # FPS sayacını sıfırla
        self.fps_start_time = None
        self.fps_counter = 0
        self.current_fps = 0.0
        
        print("Modeller belleğe yükleniyor, lütfen bekleyin...")
        
        # MODEL 1 SEÇİMİ
        if model1 == "Faster R-CNN":
            self.active_model1 = FasterRCNN_Model()
        elif model1 == "Mask R-CNN":
            self.active_model1 = MaskRCNN_Model()
        elif model1 == "YOLOv8":
            self.active_model1 = YOLOv8_Model()
        elif model1 == "RT-DETR":
            self.active_model1 = RTDETR_Model()
            
        # MODEL 2 SEÇİMİ
        if model2 == "Faster R-CNN":
            self.active_model2 = FasterRCNN_Model()
        elif model2 == "Mask R-CNN":
            self.active_model2 = MaskRCNN_Model()
        elif model2 == "YOLOv8":
            self.active_model2 = YOLOv8_Model()
        elif model2 == "RT-DETR":
            self.active_model2 = RTDETR_Model()

        if source_type == "Kamera":
            self.cap = cv2.VideoCapture(0)
        else:
            self.cap = cv2.VideoCapture(source_path)
        
        if not self.cap.isOpened():
            print("HATA: Görüntü kaynağı açılamadı!")
            return

        fps = self.cap.get(cv2.CAP_PROP_FPS)
        if not fps or fps == 0:
            fps = 30
        self.frame_delay = int(1000 / fps)

        self.is_running = True
        self.process_video_stream()

    def calculate_stats_text(self, model_name, results, inference_time):
        count = len(results)
        if count > 0:
            scores = [r['score'] * 100 for r in results]
            avg_conf = np.mean(scores)
            max_conf = np.max(scores)
            min_conf = np.min(scores)
        else:
            avg_conf, max_conf, min_conf = 0.0, 0.0, 0.0

        is_stream = "resim" not in self.current_source_type.lower()
        fps_str = f"{self.current_fps:.1f}" if is_stream else "N/A"

        # Süre bilgisini formatlıyoruz
        time_str = f"{inference_time:.1f} ms" if inference_time > 0 else "0.0 ms"

        text = (
            f"🤖 MODEL: {model_name}\n"
            f"====================\n"
            f"🍏 Adet     : {count}\n"
            f"📊 Ortalama : %{avg_conf:.1f}\n"
            f"🔝 En Yuksek: %{max_conf:.1f}\n"
            f"📉 En Dusuk : %{min_conf:.1f}\n"
            f"⏱️ Sure     : {time_str}\n" 
            f"⚡ Hiz (FPS): {fps_str}"
        )
        return text

    def process_video_stream(self):
        if not self.is_running or self.cap is None:
            return

        start_time = time.perf_counter()
        
        # --- CANLI DİNAMİK FPS HESAPLAMA ---
        if "resim" not in self.current_source_type.lower():
            if self.fps_start_time is None:
                self.fps_start_time = time.perf_counter()
                self.fps_counter = 0
            else:
                self.fps_counter += 1
                elapsed = time.perf_counter() - self.fps_start_time
                if elapsed >= 1.0:
                    self.current_fps = self.fps_counter / elapsed
                    self.fps_counter = 0
                    self.fps_start_time = time.perf_counter()

        ret, frame = self.cap.read()
        
        if ret:
            if hasattr(self, 'current_source_type') and self.current_source_type == 'webcam':
                frame = cv2.flip(frame, 1)
            frame_resized = cv2.resize(frame, (640, 280))
            
            # --- MODEL 1 ANALİZ ---
            frame1_out = frame_resized.copy()
            results1 = []
            m1_time = 0.0
            if self.active_model1 is not None:
                t0 = time.perf_counter()
                results1 = self.active_model1.predict(frame_resized)
                m1_time = (time.perf_counter() - t0) * 1000
                frame1_out = self.active_model1.draw_boxes(frame1_out, results1)
            info1_text = self.calculate_stats_text(self.model1_name, results1, m1_time)

            # --- MODEL 2 ANALİZ ---
            frame2_out = frame_resized.copy()
            results2 = []
            m2_time = 0.0
            info2_text = "🤖 MODEL 2: Devre Disi\n====================\nTekli analiz modu\naktif."
            
            if self.sidebar.mode_var.get() == "Çiftli Model" and self.active_model2 is not None:
                t0 = time.perf_counter()
                results2 = self.active_model2.predict(frame_resized)
                m2_time = (time.perf_counter() - t0) * 1000
                frame2_out = self.active_model2.draw_boxes(frame2_out, results2)
                info2_text = self.calculate_stats_text(self.model2_name, results2, m2_time)

            pil_image1 = Image.fromarray(cv2.cvtColor(frame1_out, cv2.COLOR_BGR2RGB))
            pil_image2 = Image.fromarray(cv2.cvtColor(frame2_out, cv2.COLOR_BGR2RGB))
            
            self.video_panel.update_frames(pil_image1, pil_image2, info1_text, info2_text)
            
        else:
            if hasattr(self, 'current_source_type') and self.current_source_type == 'video' and self.sidebar.loop_var.get():
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                self.stream_after_id = self.after(10, self.process_video_stream)
                return

            print("Akış sona erdi.")
            self.is_running = False
            self.cap.release()
            return
            
        elapsed_time = int((time.perf_counter() - start_time) * 1000)
        wait_time = max(1, self.frame_delay - elapsed_time)
        self.stream_after_id = self.after(wait_time, self.process_video_stream)

    def on_closing(self):
        self.is_running = False
        if self.stream_after_id is not None:
            self.after_cancel(self.stream_after_id)
        if self.cap is not None:
            self.cap.release()
        self.destroy()

if __name__ == "__main__":
    app = ObjectDetectionApp()
    app.mainloop()