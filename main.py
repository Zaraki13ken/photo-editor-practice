import cv2
import numpy as np
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk, filedialog, messagebox


class App():
    def __init__(self, root):
        self.root = root
        self.root.title("Летняя практика")
        root.iconbitmap(default="static/favicon.ico")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)

        self.cv_original = None
        self.cv_current = None
        self.image_tk = None

        self.create_widgets()

    def create_widgets(self):
        """Создание элементов интерфейса"""
        rightbar = ttk.Frame(borderwidth=1, relief="solid", width=250)
        rightbar.pack(side="right", fill="y", padx=5, pady=5)

        button1 = ttk.Button(
            rightbar,
            command=self.load_image,
            text="Открыть файл (PNG/JPG)"
            )
        button1.pack(anchor="n", pady=10, padx=15, fill='x')
        button2 = ttk.Button(
            rightbar,
            command=self.camera_shot,
            text="Снимок с веб-камеры"
            )
        button2.pack(anchor="n", pady=[0, 10], padx=15, fill='x')
        button3 = ttk.Button(
            rightbar,
            command=self.save_as,
            text="Сохранить как.."
            )
        button3.pack(anchor="n", pady=[0, 10], padx=15, fill='x')

        ttk.Separator(rightbar, orient='horizontal').pack(fill='x', pady=5)

        tk.Label(
            rightbar,
            text="Цветовые каналы",
            font=("Calibri", 10, "bold")).pack()
        tk.Button(
            rightbar,
            text="Оригинальный цвет",
            command=self.show_original,
            width=25).pack(pady=2, padx=5)
        tk.Button(
            rightbar,
            text="Синий канал (B)",
            command=lambda: self.show_channel(0),
            width=25,
            fg="blue").pack(pady=2, padx=5)
        tk.Button(
            rightbar,
            text="Зеленый канал (G)",
            command=lambda: self.show_channel(1),
            width=25,
            fg="green").pack(pady=2, padx=5)
        tk.Button(
            rightbar,
            text="Красный канал (R)",
            command=lambda: self.show_channel(2),
            width=25,
            fg="red").pack(pady=2, padx=5)

        ttk.Separator(
            rightbar,
            orient='horizontal').pack(fill='x', pady=5)

        ttk.Button(
            rightbar,
            text="Эффект: Негатив",
            command=self.apply_negative,
            width=25).pack(pady=5)

        ttk.Separator(rightbar, orient='horizontal').pack(fill='x', pady=5)

        tk.Label(
            rightbar,
            text="Размер границ (пикс):"
            ).pack(anchor=tk.W, pady=[0, 2], padx=5)

        self.border_entry = tk.Entry(rightbar, width=10)
        self.border_entry.insert(0, "15")
        self.border_entry.pack(anchor=tk.W, padx=5, pady=2)
        ttk.Button(
            rightbar,
            text="Добавить границы",
            command=self.apply_border).pack(anchor="w", padx=5, pady=2)

        ttk.Separator(rightbar, orient='horizontal').pack(fill='x', pady=5)

        tk.Label(
            rightbar,
            text="Зелёная линия",
            font=("Calibri", 10, "bold")).pack(padx=5, pady=[0, 2])

        inside_frame = ttk.Frame(rightbar)
        inside_frame.pack(anchor=tk.W, padx=5)
        self.ent_x1 = tk.Entry(inside_frame, width=4)
        self.ent_x1.insert(0, "10")
        self.ent_y1 = tk.Entry(inside_frame, width=4)
        self.ent_y1.insert(0, "10")
        self.ent_x2 = tk.Entry(inside_frame, width=4)
        self.ent_x2.insert(0, "200")
        self.ent_y2 = tk.Entry(inside_frame, width=4)
        self.ent_y2.insert(0, "200")
        self.ent_thick = tk.Entry(inside_frame, width=3)
        self.ent_thick.insert(0, "5")

        tk.Label(
            inside_frame,
            text="Координаты нач. точки"
            ).grid(row=0, column=0, columnspan=4, sticky="w")

        tk.Label(inside_frame, text="X1:").grid(row=1, column=0, sticky="w")
        self.ent_x1.grid(row=1, column=1, sticky="w")
        tk.Label(inside_frame, text="Y1:").grid(row=1, column=2, sticky="w")
        self.ent_y1.grid(row=1, column=3, sticky="w")

        tk.Label(
            inside_frame,
            text="Координаты кон. точки"
            ).grid(row=2, column=0, columnspan=4, sticky="w")

        tk.Label(inside_frame, text="X2:").grid(row=3, column=0, sticky="w")
        self.ent_x2.grid(row=3, column=1, sticky="w")
        tk.Label(inside_frame, text="Y2:").grid(row=3, column=2, sticky="w")
        self.ent_y2.grid(row=3, column=3, sticky="w")

        tk.Label(
            inside_frame,
            text="Толщина линии:").grid(row=4, column=0, sticky="w")

        self.ent_thick.grid(row=5, column=1, sticky="w")

        tk.Button(
            rightbar,
            text="Нарисовать зеленую линию",
            command=self.apply_line, width=25).pack(pady=5)

        ttk.Separator(
            rightbar,
            orient='horizontal').pack(anchor="s", fill='x', pady=5)

        tk.Label(
            rightbar,
            text="Status bar",
            font=("Calibri", 10, "bold")).pack()

        self.status_label = tk.Label(
            rightbar,
            text="Приложение готово",
            fg="green",
            bg="#f0f0f0",
            wraplength=180
            )
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

        self.display_panel = tk.Label(
            self.root,
            text="Изображение не загружено",
            bg="#ffffff",
            bd=1,
            relief=tk.SOLID
            )
        self.display_panel.pack(
            side=tk.LEFT,
            fill=tk.BOTH,
            expand=True,
            padx=5,
            pady=5
            )

    def log_status(self, text, is_error=False):
        """Вывод отклика приложения в статус-бар"""
        color = "red" if is_error else "blue"
        self.status_label.config(text=text, fg=color)

    def display_image(self, cv_img):
        """Конвертация OpenCV-матрицы в формат для отображения в Tkinter"""
        if cv_img is None:
            return

        img_rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)

        img_pil.thumbnail((700, 500))

        self.image_tk = ImageTk.PhotoImage(image=img_pil)
        self.display_panel.config(image=self.image_tk, text="")

    def load_image(self):
        """Загрузка изображения с диска"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png;*.jpg"), ("All Files", "*.*")]
        )
        if not file_path:
            return

        try:
            file_bytes = np.fromfile(file_path, dtype=np.uint8)
            img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

            if img is None:
                raise Exception(
                    "Файл поврежден или имеет неподдерживаемый формат."
                    )

            self.cv_original = img.copy()
            self.cv_current = img.copy()
            self.display_image(self.cv_current)
            self.log_status(f"Успешно загружено: {file_path.split('/')[-1]}")
        except Exception as e:
            self.log_status("Ошибка загрузки файла!", is_error=True)
            messagebox.showerror(
                "Ошибка", f"Не удалось открыть изображение:\n{str(e)}"
                )

    def camera_shot(self):
        """Захват кадра с веб-камеры"""
        self.log_status("Попытка подключения к камере...")
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            self.log_status("Камера недоступна!", is_error=True)
            messagebox.showerror("Ошибка камеры",
                                 "Не удалось подключиться к веб-камере.")
            return

        ret, frame = cap.read()
        cap.release()

        if ret:
            self.cv_original = frame.copy()
            self.cv_current = frame.copy()
            self.display_image(self.cv_current)
            self.log_status("Снимок с камеры успешно получен!")
        else:
            self.log_status("Не удалось считать кадр", is_error=True)
            messagebox.showerror(
                "Ошибка",
                "Камера подключена, но не смогла передать изображение."
                )

    def save_as(self):
        """Сохранение изображения на диск"""
        if self.cv_original is None:
            self.log_status("Изображение не загружено!", is_error=True)
            return
        try:
            img_cv = self.cv_current.copy()
            img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
            img_pil = Image.fromarray(img_rgb)

            file_path = filedialog.asksaveasfilename(
                defaultextension=".jpg",
                filetypes=[
                    ("Image Files", "*.png;*.jpg"),
                    ("Все файлы", "*.*")
                    ],
                initialfile="image.jpg"
            )

            if not file_path:
                return

            img_pil.save(file_path)
            self.log_status(
                f"Файл {file_path.split('/')[-1]} успешно сохранён"
                )
        except Exception:
            self.log_status("Ошибка сохранения файла", is_error=True)

    def show_original(self):
        """Отображение картинки с изначальным цветом"""
        if self.cv_original is None:
            self.log_status("Изображение не загружено!", is_error=True)
            return
        self.cv_current = self.cv_original.copy()
        self.display_image(self.cv_current)
        self.log_status("Восстановлен оригинальный цвет")

    def show_channel(self, channel_index):
        """Отображение конкретного цветового канала (0=B, 1=G, 2=R)"""
        if self.cv_original is None:
            self.log_status("Изображение не загружено!", is_error=True)
            return

        b, g, r = cv2.split(self.cv_current)
        blank = np.zeros_like(b)

        if channel_index == 0:
            self.cv_current = cv2.merge([b, blank, blank])
            self.log_status("Показан Синий (B) канал")
        elif channel_index == 1:
            self.cv_current = cv2.merge([blank, g, blank])
            self.log_status("Показан Зеленый (G) channel")
        elif channel_index == 2:
            self.cv_current = cv2.merge([blank, blank, r])
            self.log_status("Показан Красный (R) канал")

        self.display_image(self.cv_current)

    def apply_negative(self):
        """Инверсия (Негатив)"""
        if self.cv_current is None:
            self.log_status("Нет изображения для обработки!", is_error=True)
            return

        self.cv_current = cv2.bitwise_not(self.cv_current)
        self.display_image(self.cv_current)
        self.log_status("Применен эффект 'Негатив'")

    def apply_border(self):
        """Добавление границ"""
        if self.cv_current is None:
            self.log_status("Нет изображения для обработки!", is_error=True)
            return

        try:
            size = int(self.border_entry.get())
            if size < 0:
                raise ValueError("Размер не может быть отрицательным.")
            if size > 500:
                raise ValueError("Размер границы слишком велик.")

            self.cv_current = cv2.copyMakeBorder(
                self.cv_current, size, size, size, size,
                cv2.BORDER_CONSTANT, value=[0, 0, 0]
            )
            self.display_image(self.cv_current)
            self.log_status(f"Добавлены границы толщиной {size} пикс.")
        except ValueError as e:
            self.log_status("Неверный размер границ!", is_error=True)
            messagebox.showwarning(
                "Внимание",
                f"Введите целое положительное число (0-500).\nОшибка: {e}"
                )

    def apply_line(self):
        """Рисование зеленой линии"""
        if self.cv_current is None:
            self.log_status("Нет изображения для обработки!", is_error=True)
            return

        try:
            x1 = int(self.ent_x1.get())
            y1 = int(self.ent_y1.get())
            x2 = int(self.ent_x2.get())
            y2 = int(self.ent_y2.get())
            thick = int(self.ent_thick.get())

            if thick <= 0:
                raise ValueError("Толщина должна быть больше 0.")

            cv2.line(self.cv_current, (x1, y1), (x2, y2), (0, 255, 0), thick)
            self.display_image(self.cv_current)
            self.log_status(f"Нарисована линия ({x1},{y1}) -> ({x2},{y2})")

        except ValueError as e:
            self.log_status("Ошибка ввода параметров линии!", is_error=True)
            messagebox.showwarning(
                "Внимание",
                ("Все параметры линии должны"
                 f"быть целыми числами.\nОшибка: {e}")
                )


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)

    root.mainloop()
