import customtkinter as ctk
from tkinter import filedialog
import os

class SidebarPanel(ctk.CTkFrame):
    def __init__(self, master, start_callback, **kwargs):
        super().__init__(master, **kwargs)
        self.start_callback = start_callback
        
        # Seçilen veri kaynağını tutacak değişkenler
        self.source_path = None
        self.source_type = None

        # --- BAŞLIK ---
        self.title_label = ctk.CTkLabel(self, text="Kontrol Paneli", font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.pack(padx=20, pady=(20, 10))

        # --- VERİ KAYNAĞI SEÇİMİ ---
        self.source_label_title = ctk.CTkLabel(self, text="Veri Kaynağı:", font=ctk.CTkFont(weight="bold"))
        self.source_label_title.pack(padx=20, pady=(10, 0), anchor="w")

        # Butonlar yan yana dursun diye küçük bir frame
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.pack(padx=20, pady=5, fill="x")

        self.img_btn = ctk.CTkButton(self.btn_frame, text="Resim", width=60, command=self.select_image)
        self.img_btn.pack(side="left", padx=(0, 5), expand=True, fill="x")

        self.vid_btn = ctk.CTkButton(self.btn_frame, text="Video", width=60, command=self.select_video)
        self.vid_btn.pack(side="left", padx=(0, 5), expand=True, fill="x")

        self.cam_btn = ctk.CTkButton(self.btn_frame, text="Kamera", width=60, command=self.select_webcam)
        self.cam_btn.pack(side="left", expand=True, fill="x")

        # Video Döngü (Loop) Anahtarı
        self.loop_var = ctk.BooleanVar(value=True) # Varsayılan olarak açık gelsin
        self.loop_switch = ctk.CTkSwitch(self, text="Videoyu Sürekli Oynat", variable=self.loop_var)
        self.loop_switch.pack(padx=20, pady=(10, 0), anchor="w")

        # Seçilen dosyanın ismini gösterecek etiket
        self.selected_file_label = ctk.CTkLabel(self, text="Seçilen: Yok", text_color="gray", font=ctk.CTkFont(size=11))
        self.selected_file_label.pack(padx=20, pady=(0, 15), anchor="w")

        # --- MODEL SEÇİMİ ---
        self.model1_label = ctk.CTkLabel(self, text="Model 1:", font=ctk.CTkFont(weight="bold"))
        self.model1_label.pack(padx=20, pady=(10, 0), anchor="w")
        self.model1_combo = ctk.CTkComboBox(self, values=["YOLOv8", "Faster R-CNN", "Mask R-CNN", "RT-DETR"], state="readonly")
        self.model1_combo.pack(padx=20, pady=(5, 10), fill="x")

        self.model2_label = ctk.CTkLabel(self, text="Model 2:", font=ctk.CTkFont(weight="bold"))
        self.model2_label.pack(padx=20, pady=(10, 0), anchor="w")
        self.model2_combo = ctk.CTkComboBox(self, values=["YOLOv8", "Faster R-CNN", "Mask R-CNN", "RT-DETR"], state="readonly")
        self.model2_combo.pack(padx=20, pady=(5, 10), fill="x")

        # --- YENİ EKLENEN: ANALİZ MODU SEÇENEĞİ ---
        self.mode_label = ctk.CTkLabel(self, text="Analiz Modu:", font=ctk.CTkFont(weight="bold"))
        self.mode_label.pack(padx=20, pady=(10, 0), anchor="w")
        
        self.mode_var = ctk.StringVar(value="Çiftli Model")
        self.mode_option = ctk.CTkOptionMenu(
            self, 
            values=["Tekli Model", "Çiftli Model"],
            variable=self.mode_var,
            state="readonly"
        )
        self.mode_option.pack(padx=20, pady=(5, 20), fill="x")

        # --- ÇALIŞTIR BUTONU ---
        self.start_btn = ctk.CTkButton(self, text="Analizi Başlat", height=40, command=self.on_start_click)
        self.start_btn.pack(padx=20, pady=20, fill="x")

    def select_image(self):
        file_path = filedialog.askopenfilename(
            title="Bir Resim Seçin",
            filetypes=[("Resim Dosyaları", "*.jpg *.jpeg *.png *.bmp")]
        )
        if file_path:
            self.source_path = file_path
            self.source_type = 'image'
            filename = os.path.basename(file_path)
            self.selected_file_label.configure(text=f"Seçilen: {filename}")

    def select_video(self):
        file_path = filedialog.askopenfilename(
            title="Bir Video Seçin",
            filetypes=[("Video Dosyaları", "*.mp4 *.avi *.mkv *.mov")]
        )
        if file_path:
            self.source_path = file_path
            self.source_type = 'video'
            filename = os.path.basename(file_path)
            self.selected_file_label.configure(text=f"Seçilen: {filename}")

    def select_webcam(self):
        self.source_path = 0
        self.source_type = 'webcam'
        self.selected_file_label.configure(text="Seçilen: Web Kamerası")

    def on_start_click(self):
        if self.source_path is None:
            self.selected_file_label.configure(text="Lütfen bir kaynak seçin!", text_color="red")
            return

        self.selected_file_label.configure(text_color="gray")

        m1 = self.model1_combo.get()
        m2 = self.model2_combo.get()
        
        self.start_callback(m1, m2, self.source_path, self.source_type)