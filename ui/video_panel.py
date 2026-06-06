# Kameraların/Görüntülerin yan yana gösterileceği orta panel

import customtkinter as ctk
from PIL import Image, ImageTk

class VideoPanel(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # İki model çıktısını yan yana koymak için grid yapısı (1 satır, 2 sütun)
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Model 1 (Sol Ekran)
        self.cam1_label = ctk.CTkLabel(self, text="[ Model 1 Görüntüsü Bekleniyor ]", fg_color="gray15", corner_radius=10)
        self.cam1_label.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Model 2 (Sağ Ekran)
        self.cam2_label = ctk.CTkLabel(self, text="[ Model 2 Görüntüsü Bekleniyor ]", fg_color="gray15", corner_radius=10)
        self.cam2_label.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

    def update_frames(self, frame1_pil, frame2_pil):
        """
        OpenCV'den gelen ve PIL Image formatına çevrilen kareleri (frame) arayüzde günceller.
        """
        if frame1_pil:
            # CustomTkinter'ın desteklediği CTkImage formatına çeviriyoruz
            # Boyutları arayüze göre dinamik ayarlamak için panelin güncel genişlik/yüksekliğini alabiliriz
            ctk_img1 = ctk.CTkImage(light_image=frame1_pil, dark_image=frame1_pil, size=(400, 300))
            self.cam1_label.configure(image=ctk_img1, text="") # Metni temizle, resmi koy
            
        if frame2_pil:
            ctk_img2 = ctk.CTkImage(light_image=frame2_pil, dark_image=frame2_pil, size=(400, 300))
            self.cam2_label.configure(image=ctk_img2, text="")