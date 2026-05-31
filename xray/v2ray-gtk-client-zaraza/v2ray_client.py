#!/usr/bin/env python3
"""
Xray Config Manager - минималистичное приложение
"""

import os
import sys
import subprocess
import threading
from datetime import datetime

import tkinter as tk
import customtkinter as ctk
import pystray
from PIL import Image, ImageDraw

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class XrayManagerApp:
    def __init__(self):
        self.config_dir = os.path.expanduser("~/.config/xray/json/")
        self.main_config = os.path.expanduser("~/.config/xray/config.json")
        self.xray_process = None
        self.current_config = None
        
        os.makedirs(self.config_dir, exist_ok=True)
        
        self.root = ctk.CTk()
        self.root.title("Xray Manager")
        self.root.geometry("300x400")
        self.root.minsize(300, 300)
        
        # Центрируем окно
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_close_window)
        
        self.setup_ui()
        self.update_config_list()
        self.setup_tray()
        
        # Автоматически запускаем Xray и сворачиваем окно в трей
        self.root.after(100, self.auto_start_and_hide)
        
    def setup_ui(self):
        """Минималистичный интерфейс"""
        # Основной фрейм без отступов
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Выбор конфигурации
        config_label = ctk.CTkLabel(
            main_frame,
            text="Config:",
            font=ctk.CTkFont(size=12)
        )
        config_label.pack(anchor=tk.W, padx=10, pady=(10, 0))
        
        self.config_var = ctk.StringVar()
        self.config_combo = ctk.CTkOptionMenu(
            main_frame,
            variable=self.config_var,
            values=[],
            height=32
        )
        self.config_combo.pack(padx=10, pady=(5, 0), fill=tk.X)
        self.config_combo.configure(command=self.on_config_selected)
        
        # Кнопки управления
        btn_frame = ctk.CTkFrame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.start_btn = ctk.CTkButton(
            btn_frame,
            text="▶ Start",
            command=self.start_xray,
            height=35
        )
        self.start_btn.pack(side=tk.LEFT, padx=(10, 5), fill=tk.X, expand=True)
        
        self.stop_btn = ctk.CTkButton(
            btn_frame,
            text="⏹ Stop",
            command=self.stop_xray,
            height=35,
            state="disabled"
        )
        self.stop_btn.pack(side=tk.LEFT, padx=(5, 10), fill=tk.X, expand=True)
        
        # Очистка логов
        clear_btn = ctk.CTkButton(
            main_frame,
            text="Clear",
            command=self.clear_logs,
            height=28,
            width=60
        )
        clear_btn.pack(anchor=tk.E, padx=10, pady=(5, 0))
        
        # Логи Xray (только stdout)
        self.log_text = ctk.CTkTextbox(
            main_frame,
            font=ctk.CTkFont(family="monospace", size=11)
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
    def auto_start_and_hide(self):
        """Автоматический запуск Xray и сворачивание в трей"""
        # Выбираем первый доступный конфиг если ничего не выбрано
        if not self.current_config and self.config_combo.cget('values'):
            first_config = self.config_combo.cget('values')[0]
            self.config_combo.set(first_config)
            self.on_config_selected(first_config)
        
        # Запускаем Xray
        if self.current_config:
            self.start_xray()
        
        # Скрываем окно в трей
        self.root.withdraw()
        
    def update_config_list(self):
        configs = []
        
        if os.path.exists(self.config_dir):
            for filename in os.listdir(self.config_dir):
                if filename.endswith('.json'):
                    configs.append(filename)
        
        configs.sort()
        self.config_combo.configure(values=configs)
        
        if self.current_config and self.current_config in configs:
            self.config_combo.set(self.current_config)
        elif configs:
            self.config_combo.set(configs[0])
            self.on_config_selected(configs[0])
            
    def on_config_selected(self, config_name=None):
        selected = self.config_var.get()
        if selected:
            self.current_config = selected
            self.create_symlink(selected)
            
    def create_symlink(self, config_name):
        source = os.path.join(self.config_dir, config_name)
        
        if os.path.islink(self.main_config):
            os.unlink(self.main_config)
        elif os.path.exists(self.main_config):
            os.remove(self.main_config)
            
        try:
            os.symlink(source, self.main_config)
        except Exception:
            pass
            
    def start_xray(self):
        if self.xray_process and self.xray_process.poll() is None:
            return
            
        if not self.current_config:
            return
            
        if not os.path.exists(self.main_config):
            return
            
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        
        thread = threading.Thread(target=self._run_xray, daemon=True)
        thread.start()
        
    def _run_xray(self):
        try:
            cmd = ["xray", "run", "-c", self.main_config]
            
            self.xray_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            while self.xray_process and self.xray_process.poll() is None:
                line = self.xray_process.stdout.readline()
                if line:
                    self.log(line.strip())
                    
            self.on_xray_stopped()
            
        except FileNotFoundError:
            self.log("Error: xray not found in PATH")
            self.on_xray_stopped()
        except Exception as e:
            self.log(f"Error: {e}")
            self.on_xray_stopped()
            
    def stop_xray(self):
        if self.xray_process and self.xray_process.poll() is None:
            try:
                self.xray_process.terminate()
                try:
                    self.xray_process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    self.xray_process.kill()
                    self.xray_process.wait()
            except Exception:
                pass
            
    def on_xray_stopped(self):
        self.root.after(0, lambda: self.start_btn.configure(state="normal"))
        self.root.after(0, lambda: self.stop_btn.configure(state="disabled"))
        self.xray_process = None
        
    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.root.after(0, lambda: self.log_text.insert(tk.END, log_entry))
        self.root.after(0, lambda: self.log_text.see(tk.END))
        
    def clear_logs(self):
        self.log_text.delete("1.0", tk.END)
        
    def setup_tray(self):
        """Настройка системного трея с иконкой из файла"""
        # Пытаемся загрузить иконку из файла
        icon_path = "tray_icon.png"
        
        if os.path.exists(icon_path):
            # Загружаем иконку из файла
            image = Image.open(icon_path)
            # Приводим к нужному размеру (обычно 64x64 для трея)
            image = image.resize((64, 64), Image.Resampling.LANCZOS)
        else:
            # Создаем иконку по умолчанию, если файл не найден
            print(f"Warning: {icon_path} not found, using default icon")
            image = Image.new('RGB', (64, 64), color=(64, 64, 64))
            draw = ImageDraw.Draw(image)
            draw.ellipse([8, 8, 56, 56], fill=(30, 30, 30))
            draw.text([22, 20], "X", fill=(100, 100, 100))
        
        menu = pystray.Menu(
            pystray.MenuItem("Show", lambda: self.show_window()),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Start", lambda: self.tray_start()),
            pystray.MenuItem("Stop", lambda: self.tray_stop()),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Exit", lambda: self.quit_app())
        )
        
        self.tray_icon = pystray.Icon("xray_manager", image, "Xray", menu)
        tray_thread = threading.Thread(target=self.tray_icon.run, daemon=True)
        tray_thread.start()
        
    def show_window(self):
        """Показывает главное окно"""
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
        
    def tray_start(self):
        self.root.after(0, self.start_xray)
        
    def tray_stop(self):
        self.root.after(0, self.stop_xray)
        
    def on_close_window(self):
        """При закрытии окна сворачиваем в трей"""
        self.root.withdraw()
        
    def quit_app(self):
        """Выход из приложения"""
        if self.xray_process and self.xray_process.poll() is None:
            self.stop_xray()
            
        self.tray_icon.stop()
        self.root.destroy()
        sys.exit(0)
        
    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    try:
        import customtkinter as ctk
        import pystray
        from PIL import Image, ImageDraw
    except ImportError as e:
        print(f"Missing dependency: {e}")
        sys.exit(1)
        
    app = XrayManagerApp()
    app.run()
