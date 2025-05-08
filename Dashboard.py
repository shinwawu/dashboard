import os
import threading
import time
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

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

        # Gráfico com matplotlib
        self.fig = Figure(figsize=(8, 3), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("Gráfico de Uso da CPU")
        self.ax.set_xlabel("Tempo")
        self.ax.set_ylabel("% Uso")
        self.cpu_uso_lista = [0] * 30
        self.line, = self.ax.plot(self.cpu_uso_lista, color='blue')

        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(pady=10)

    def atualizar_cpu(self, uso):
        self.label_cpu.config(text=f"Uso da CPU: {uso:.2f}%")
        self.progress_cpu["value"] = uso

        # Atualiza o gráfico
        self.cpu_uso_lista.append(uso)
        self.cpu_uso_lista.pop(0)
        self.line.set_ydata(self.cpu_uso_lista)
        self.ax.set_ylim(0, 100)
        self.canvas.draw()

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
