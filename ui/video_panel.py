import customtkinter as ctk
from PIL import Image

class VideoPanel(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.grid_columnconfigure(0, weight=0, minsize=240) 
        self.grid_columnconfigure(1, weight=1)              
        self.grid_rowconfigure((0, 1), weight=1)

        # --- MODEL 1 (ÜST PANEL) ---
        # Sol İstatistik Kutusu
        self.info1_label = ctk.CTkLabel(
            self, 
            text="Model 1 Verisi\nBekleniyor...", 
            justify="left", 
            anchor="w",
            fg_color="gray12", 
            corner_radius=8,
            padx=15,
            pady=15,
            font=("Courier New", 13, "bold")
        )
        self.info1_label.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="nsew")

        # Sağ Görüntü Kutusu
        self.cam1_label = ctk.CTkLabel(self, text="[ Model 1 Görüntüsü Bekleniyor ]", fg_color="gray15", corner_radius=10)
        self.cam1_label.grid(row=0, column=1, padx=(5, 10), pady=10, sticky="nsew")


        # --- MODEL 2 (ALT PANEL) ---
        # Sol İstatistik Kutusu
        self.info2_label = ctk.CTkLabel(
            self, 
            text="Model 2 Verisi\nBekleniyor...", 
            justify="left", 
            anchor="w",
            fg_color="gray12", 
            corner_radius=8,
            padx=15,
            pady=15,
            font=("Courier New", 13, "bold")
        )
        self.info2_label.grid(row=1, column=0, padx=(10, 5), pady=10, sticky="nsew")

        # Sağ Görüntü Kutusu
        self.cam2_label = ctk.CTkLabel(self, text="[ Model 2 Görüntüsü Bekleniyor ]", fg_color="gray15", corner_radius=10)
        self.cam2_label.grid(row=1, column=1, padx=(5, 10), pady=10, sticky="nsew")

    def update_frames(self, frame1_pil, frame2_pil, info1_text="", info2_text=""):
        """
        Görüntüleri ve sol paneldeki istatistik metinlerini eşzamanlı günceller.
        """
        if frame1_pil:
            ctk_img1 = ctk.CTkImage(light_image=frame1_pil, dark_image=frame1_pil, size=(640, 280))
            self.cam1_label.configure(image=ctk_img1, text="")
        if info1_text:
            self.info1_label.configure(text=info1_text)
            
        if frame2_pil:
            ctk_img2 = ctk.CTkImage(light_image=frame2_pil, dark_image=frame2_pil, size=(640, 280))
            self.cam2_label.configure(image=ctk_img2, text="")
        if info2_text:
            self.info2_label.configure(text=info2_text)