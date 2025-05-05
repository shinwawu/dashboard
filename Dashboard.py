import os
import threading
import time
import tkinter as tk
from tkinter import ttk

# ======== MODEL ========
def ler_uso_cpu():
    with open("/proc/stat", "r") as f:
        linha = f.readline()
    cpupartes = list(map(int, linha.split()[1:]))
    tempototal = sum(cpupartes)
    tempoparado = cpupartes[3]
    return tempototal, tempoparado

# ======== VIEW ========
class InterfaceDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Dashboard/Gerenciador de Tarefas")
        self.root.geometry("400x150")

        self.label_cpu = tk.Label(root, text="Uso da CPU: --%", font=("Arial", 14))
        self.label_cpu.pack(pady=10)

        self.progress_cpu = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
        self.progress_cpu.pack(pady=10)

    def atualizar_cpu(self, uso):
        self.label_cpu.config(text=f"Uso da CPU: {uso:.2f}%")
        self.progress_cpu["value"] = uso

# ======== CONTROLLER ========
class ControleDashboard:
    def __init__(self, view):
        self.view = view
        self.cpu_total_antes, self.cpu_parado_antes = ler_uso_cpu()
        self.thread = threading.Thread(target=self.atualizar_periodicamente)
        self.thread.daemon = True
        self.thread.start()

    def atualizar_periodicamente(self):
        while True:
            tempototal, tempoparado = ler_uso_cpu()
            diferenca_tempo = tempototal - self.cpu_total_antes
            diferenca_parado = tempoparado - self.cpu_parado_antes
            uso_cpu = 100 * (1 - diferenca_parado / diferenca_tempo) if diferenca_tempo > 0 else 0
            self.cpu_total_antes, self.cpu_parado_antes = tempototal, tempoparado

            self.view.root.after(0, self.view.atualizar_cpu, uso_cpu)

            time.sleep(5)

# ======== MAIN ========
if __name__ == "__main__":
    root = tk.Tk()
    view = InterfaceDashboard(root)
    controller = ControleDashboard(view)
    root.mainloop()
