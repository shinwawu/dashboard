import os
import threading
import time
import tkinter as tk
from tkinter import ttk

# ======== MODEL ========
def ler_uso_cpu():
    with open("/proc/stat", "r") as f:
        linha = f.readline()
    partes = list(map(int, linha.split()[1:]))
    total = sum(partes)
    idle = partes[3]
    return total, idle

# ======== VIEW ========
class DashboardView:
    def __init__(self, root):
        self.root = root
        self.root.title("Linux Dashboard - Uso da CPU")
        self.root.geometry("400x150")

        self.label_cpu = tk.Label(root, text="Uso da CPU: --%", font=("Arial", 14))
        self.label_cpu.pack(pady=10)

        self.progress_cpu = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
        self.progress_cpu.pack(pady=10)

    def atualizar_cpu(self, uso):
        self.label_cpu.config(text=f"Uso da CPU: {uso:.2f}%")
        self.progress_cpu["value"] = uso

# ======== CONTROLLER ========
class DashboardController:
    def __init__(self, view):
        self.view = view
        self.cpu_total_antes, self.cpu_idle_antes = ler_uso_cpu()
        self.thread = threading.Thread(target=self.atualizar_periodicamente)
        self.thread.daemon = True
        self.thread.start()

    def atualizar_periodicamente(self):
        while True:
            total, idle = ler_uso_cpu()
            total_diff = total - self.cpu_total_antes
            idle_diff = idle - self.cpu_idle_antes
            uso_cpu = 100 * (1 - idle_diff / total_diff) if total_diff > 0 else 0
            self.cpu_total_antes, self.cpu_idle_antes = total, idle

            # Atualiza a interface na thread principal
            self.view.root.after(0, self.view.atualizar_cpu, uso_cpu)

            time.sleep(5)

# ======== MAIN ========
if __name__ == "__main__":
    root = tk.Tk()
    view = DashboardView(root)
    controller = DashboardController(view)
    root.mainloop()
