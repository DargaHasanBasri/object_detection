# Ana çerçeveyi ve diğer bileşenleri birleştirir

import time
import cv2
import customtkinter as ctk
from PIL import Image
from ui.sidebar_panel import SidebarPanel
from ui.video_panel import VideoPanel

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class ObjectDetectionApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Doğa ve Tarım: Nesne Tespiti Analiz Sistemi")
        self.geometry("1100x700")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Sol Panel (Sidebar)
        self.sidebar = SidebarPanel(self, start_callback=self.start_analysis, width=250, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        # Orta Panel (VideoPaneli modülü)
        self.video_panel = VideoPanel(self, corner_radius=10)
        self.video_panel.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        # OpenCV VideoCapture nesnesi için durum değişkenleri
        self.cap = None
        self.is_running = False
        self.frame_delay = 15 # Varsayılan bekleme süresi (milisaniye)

        # Pencere kapatıldığında kamerayı serbest bırakmak için
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def start_analysis(self, model1, model2, source_path, source_type):
        # Kaynak tipini (video mu resim mi) döngü kontrolü için sisteme kaydediyoruz
        self.current_source_type = source_type

        # Eğer hali hazırda çalışan bir kamera/video varsa önce onu kapat
        if self.cap is not None:
            self.cap.release()
        
        self.is_running = True
        
        # Seçilen kaynağa göre (Kamera ise 0, Video ise dosya yolu) OpenCV'yi başlat
        self.cap = cv2.VideoCapture(source_path)
        
        # Kameranın başarıyla açıldığından emin ol
        if not self.cap.isOpened():
            print("HATA: Görüntü kaynağı açılamadı!")
            return

        # Videonun orijinal FPS'ini bul ve bir karenin kaç milisaniye ekranda kalması gerektiğini hesapla
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        if not fps or fps == 0:
            fps = 30 # Kamera veya okunamayan videolarda varsayılan FPS
        self.frame_delay = int(1000 / fps)

        print(f"Analiz Başladı: {source_type} akışı okunuyor... (Hedef FPS: {fps})")
        
        # Frame (kare) okuma döngüsünü başlat
        self.process_video_stream()

    def process_video_stream(self):
        # Döngü durdurulduysa veya kamera kapandıysa çık
        if not self.is_running or self.cap is None:
            return

        # İşlem süresini ölçmek için başlangıç zamanını kaydet
        start_time = time.perf_counter()

        ret, frame = self.cap.read()
        
        if ret:
            # OPTİMİZASYON 1: Görüntüyü dönüştürmeden önce OpenCV ile küçült (Çok daha hızlıdır)
            # Arayüzdeki kutuların boyutu yaklaşık 400x300 olduğu için o boyuta çekiyoruz
            frame_resized = cv2.resize(frame, (400, 300))
            
            # 1. OpenCV BGR formatında okur, bunu RGB'ye çevirmeliyiz (Arayüzde renklerin doğru görünmesi için)
            frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
            
            # 2. Numpy dizisini (OpenCV formatı) PIL Image formatına çevir
            pil_image = Image.fromarray(frame_rgb)
            
            # 3. İleride burada modellerin çizim yaptığı (bounding box) frame'ler olacak. 
            # Şimdilik sistemin çalıştığını görmek için aynı görüntüyü iki panele de gönderiyoruz.
            self.video_panel.update_frames(pil_image, pil_image)
            
        else:
            if hasattr(self, 'current_source_type') and self.current_source_type == 'video' and self.sidebar.loop_var.get():
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0) # Videoyu 0. kareye (en başa) al
                self.after(10, self.process_video_stream) # Döngüyü tekrar başlat
                return

            # Döngü kapalıysa veya kamera bağlantısı koptuysa tamamen durdur
            print("Akış sona erdi.")
            self.is_running = False
            self.cap.release()
            return
            
        # OPTİMİZASYON 2: Görüntü işlerken geçen süreyi hedef bekleme süresinden çıkarıyoruz.
        # Böylece ağır işlemler videonun akış hızını yavaşlatmıyor.
        elapsed_time = int((time.perf_counter() - start_time) * 1000)
        wait_time = max(1, self.frame_delay - elapsed_time)
        
        # UI'ı dondurmamak için hesaplanan bekleme süresi kadar sonra bu fonksiyonu tekrar çağır
        self.after(wait_time, self.process_video_stream)

    def on_closing(self):
        # Uygulama kapanırken arkada kameranın açık kalmaması için donanımı serbest bırak
        self.is_running = False
        if self.cap is not None:
            self.cap.release()
        self.destroy()