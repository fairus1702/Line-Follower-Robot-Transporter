import tkinter as tk
from tkinter import messagebox, ttk
import socket

class MonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistem Monitor")
        self.root.geometry("1150x500")
        self.root.configure(bg="#F0F4F8")

        self.judul = ["Motor", "Servo", "Servo2"]  # Tambahkan Servo2
        self.entries = []
        self.tcp_conn = None
        self.connected = False

        # Header
        tk.Label(self.root, text="SISTEM MONITOR", font=("Segoe UI", 16, "bold"),
                 fg="#0aa1ff", bg="#F0F4F8").pack(pady=(10, 2))

        self.create_wifi_input()

        # Main layout
        main_frame = tk.Frame(self.root, bg="#F0F4F8")
        main_frame.pack(fill="both", expand=True, padx=15, pady=5)

        self.left_frame = tk.Frame(main_frame, bg="#F0F4F8")
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        ttk.Separator(main_frame, orient='vertical').grid(row=0, column=1, sticky="ns", padx=5)

        self.right_frame = tk.Frame(main_frame, bg="#F0F4F8")
        self.right_frame.grid(row=0, column=2, sticky="nsew", padx=(10, 0))

        self.create_left_side()
        self.create_right_side()

        self.root.after(100, self.read_serial)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_wifi_input(self):
        ip_frame = tk.Frame(self.root, bg="#F0F4F8")
        ip_frame.pack(pady=(0, 5), anchor="center")

        tk.Label(ip_frame, text="IP ESP8266:", font=("Segoe UI", 11), bg="#F0F4F8").grid(row=0, column=0, padx=(0, 5))
        self.ip_entry = tk.Entry(ip_frame, font=("Segoe UI", 11), width=18)
        self.ip_entry.grid(row=0, column=1, padx=(0, 5))
        tk.Button(ip_frame, text="Connect", font=("Segoe UI", 10, "bold"), bg="#0a75ff", fg="white",
                  command=self.connect_wifi).grid(row=0, column=2)

    def connect_wifi(self):
        ip = self.ip_entry.get()
        try:
            self.tcp_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.tcp_conn.settimeout(3)
            self.tcp_conn.connect((ip, 80))
            self.tcp_conn.settimeout(None)
            self.connected = True
            messagebox.showinfo("Sukses", f"Terhubung ke ESP di {ip}")
        except Exception as e:
            messagebox.showerror("Gagal", f"Koneksi WiFi gagal: {e}")
            self.tcp_conn = None
            self.connected = False

    def on_closing(self):
        if self.tcp_conn:
            self.tcp_conn.close()
        self.root.destroy()

    def send_data(self, msg):
        try:
            if self.connected and self.tcp_conn:
                self.tcp_conn.sendall(msg.encode())
                print("Terkirim:", msg.strip())
        except Exception as e:
            messagebox.showerror("Error", f"Gagal kirim data: {e}")

    def update_sensor_value(self, index, value):
        canvas, bar = self.line_bars[index]
        color = "#6134c9" if value == "1" else "#dcdcdc"
        canvas.itemconfig(bar, fill=color)

    def read_serial(self):
        try:
            if self.connected and self.tcp_conn:
                self.tcp_conn.settimeout(0.1)
                line = self.tcp_conn.recv(1024).decode(errors='ignore').strip()
                if line:
                    print("Received:", line)
                    values = line.split(",")
                    if len(values) == len(self.line_bars):
                        for i, val in enumerate(values):
                            self.update_sensor_value(i, '1' if val.strip() == '1' else '0')
        except:
            pass
        self.root.after(100, self.read_serial)

    def create_left_side(self):
        nav_frame = tk.Frame(self.left_frame, bg="#FFFFFF", relief="ridge", bd=2)
        nav_frame.pack(pady=10, fill="both", expand=True)

        canvas_width, canvas_height = 350, 160
        self.x_pos, self.y_pos, self.step = canvas_width // 2, canvas_height // 2, 10

        self.canvas = tk.Canvas(nav_frame, width=canvas_width, height=canvas_height, bg="#eef6ff")
        self.canvas.pack(pady=10)
        self.tracker = self.canvas.create_oval(self.x_pos-7, self.y_pos-7,
                                               self.x_pos+7, self.y_pos+7, fill="#007fff")

        btn_frame = tk.Frame(nav_frame, bg="#F0F4F8")
        btn_frame.pack(pady=8)
        btn_opts = {"width": 4, "height": 2, "bg": "#0a75ff", "fg": "white", "font": ("Segoe UI", 12, "bold")}

        tk.Button(btn_frame, text="↑", command=self.move_up, **btn_opts).grid(row=0, column=1, padx=8)
        tk.Button(btn_frame, text="←", command=self.move_left, **btn_opts).grid(row=1, column=0, padx=8)
        tk.Button(btn_frame, text="↓", command=self.move_down, **btn_opts).grid(row=1, column=1, padx=8)
        tk.Button(btn_frame, text="→", command=self.move_right, **btn_opts).grid(row=1, column=2, padx=8)

        tk.Button(btn_frame, text="STOP", command=self.stop_motor,
                  bg="#d9534f", fg="white", font=("Segoe UI", 12, "bold"),
                  width=10, height=2).grid(row=2, column=0, columnspan=3, pady=10)

    def create_right_side(self):
        input_frame = tk.Frame(self.right_frame, bg="#F0F4F8")
        input_frame.pack(pady=(0, 10), anchor="ne")

        for i, label_text in enumerate(self.judul):
            label = tk.Label(input_frame, text=f"{i+1}. {label_text}", font=("Segoe UI", 13, "bold"),
                             fg="#0a75ff", bg="#F0F4F8")
            label.grid(row=i, column=0, sticky="w", pady=6, padx=5)
            entry = tk.Entry(input_frame, font=("Segoe UI", 13), width=18, bd=2, relief="groove")
            entry.grid(row=i, column=1, pady=6, padx=5)
            self.entries.append(entry)
            btn = tk.Button(input_frame, text="OK", font=("Segoe UI", 11, "bold"),
                            bg="#0a75ff", fg="white", width=4,
                            command=lambda e=entry, l=label_text: self.submit(e, l))
            btn.grid(row=i, column=2, padx=5, pady=6)

        # Line Sensor Status
        tk.Label(self.right_frame, text="Line Sensor Monitor",
                 font=("Segoe UI", 14, "bold"), fg="#0a75ff", bg="#F0F4F8").pack(pady=(10, 5))

        self.line_bars = []
        bar_frame = tk.Frame(self.right_frame, bg="#F0F4F8")
        bar_frame.pack(pady=5, padx=10, fill='both', expand=True)

        bar_frame.columnconfigure(0, weight=1, minsize=90)
        bar_frame.columnconfigure(1, weight=3)

        for i in range(5):
            label = tk.Label(bar_frame, text=f"Sensor {i+1}", font=("Segoe UI", 12), bg="#F0F4F8", anchor='w')
            label.grid(row=i, column=0, sticky="w", padx=(5, 10), pady=6)

            canvas = tk.Canvas(bar_frame, width=250, height=25, bg="#dcdcdc", highlightthickness=0)
            canvas.grid(row=i, column=1, sticky="ew", padx=(0, 5), pady=6)

            bar = canvas.create_rectangle(2, 2, 248, 23, fill="#dcdcdc", outline="#999999", width=1)
            self.line_bars.append((canvas, bar))

    def move_tracker(self, dx, dy):
        if 0 < self.x_pos + dx < 350 and 0 < self.y_pos + dy < 160:
            self.canvas.move(self.tracker, dx, dy)
            self.x_pos += dx
            self.y_pos += dy

    def send_movement(self, cmd):
        speed = self.entries[0].get()
        if speed.isdigit() and 0 <= int(speed) <= 255:
            self.send_data(f"{cmd}:{speed}\n")

    def move_up(self):
        self.move_tracker(0, -self.step)
        self.send_movement("M")

    def move_down(self):
        self.move_tracker(0, self.step)
        self.send_movement("B")

    def move_left(self):
        self.move_tracker(-self.step, 0)
        self.send_movement("L")

    def move_right(self):
        self.move_tracker(self.step, 0)
        self.send_movement("R")

    def stop_motor(self):
        self.send_data("M:0\n")

    def submit(self, entry, label):
        val = entry.get()
        if label == "Motor" and val.isdigit() and 0 <= int(val) <= 255:
            prefix = "M"
        elif label == "Servo" and val.isdigit() and 0 <= int(val) <= 180:
            prefix = "S"
        elif label == "Servo2" and val.isdigit() and 0 <= int(val) <= 180:
            prefix = "T"
        else:
            messagebox.showwarning("Error", f"Input {label} tidak valid.")
            return
        self.send_data(f"{prefix}:{val}\n")
        messagebox.showinfo("Sukses", f"{label} diatur ke {val}")

if __name__ == "__main__":
    root = tk.Tk()
    app = MonitorApp(root)
    root.mainloop()
