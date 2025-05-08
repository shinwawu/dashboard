import os
import threading
import time
import tkinter as tk
from tkinter import ttk

# ======== MODEL ========
def LeituraCPU():
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
        self.root.geometry("900x550")

        self.label_cpu = tk.Label(root, text="Uso da CPU: --%", font=("Arial", 14))
        self.label_cpu.pack(pady=10)

        self.progress_cpu = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
        self.progress_cpu.pack(pady=10)

        # Canvas para gráfico manual
        self.canvas = tk.Canvas(root, width=800, height=200, bg="black")
        self.canvas.pack(pady=10)
        self.cpu_uso_lista = [0] * 100  # 100 pontos no gráfico

    def atualizar_cpu(self, uso):
        self.label_cpu.config(text=f"Uso da CPU: {uso:.2f}%")
        self.progress_cpu["value"] = uso

        # Atualiza os dados
        self.cpu_uso_lista.append(uso)
        self.cpu_uso_lista.pop(0)

        # Redesenha o gráfico
        self.canvas.delete("all")
        h = 200
        w = 800
        for i in range(1, len(self.cpu_uso_lista)):
            x1 = (i - 1) * (w / len(self.cpu_uso_lista))
            y1 = h - (self.cpu_uso_lista[i - 1] / 100 * h)
            x2 = i * (w / len(self.cpu_uso_lista))
            y2 = h - (self.cpu_uso_lista[i] / 100 * h)
            self.canvas.create_line(x1, y1, x2, y2, fill="lime", width=2)

# ======== CONTROLLER ========
class ControleDashboard:
    def __init__(self, view):
        self.view = view
        self.CPUtotal_tempoanterior, self.CPUparado_tempoanterior = LeituraCPU()
        self.thread = threading.Thread(target=self.atualizar_periodicamente)
        self.thread.daemon = True
        self.thread.start()

    def atualizar_periodicamente(self):
        while True:
            tempototal, tempoparado = LeituraCPU()
            diferenca_tempo = tempototal - self.CPUtotal_tempoanterior
            diferenca_parado = tempoparado - self.CPUparado_tempoanterior

            uso_cpu = 100 * (1 - diferenca_parado / diferenca_tempo) if diferenca_tempo > 0 else 0
            self.CPUtotal_tempoanterior, self.CPUparado_tempoanterior = tempototal, tempoparado

            self.view.root.after(0, self.view.atualizar_cpu, uso_cpu)
            time.sleep(1)

# ======== MAIN ========
if __name__ == "__main__":
    root = tk.Tk()
    view = InterfaceDashboard(root)
    controller = ControleDashboard(view)
    root.mainloop()
