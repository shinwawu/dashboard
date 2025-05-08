import os
import threading
import time
import tkinter as tk
from tkinter import ttk

#Funcao para ler as estatisticas do CPU e retorna tempos
#Aqui vai ser o Model
def LeituraCPU():
    with open("/proc/stat", "r") as f:
        linha = f.readline()
    cpupartes = list(map(int, linha.split()[1:]))
    tempototal = sum(cpupartes)
    tempoparado = cpupartes[3]
    
    return tempototal, tempoparado

#Interface
#Aqui vai ser o View
class InterfaceDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Dashboard/Gerenciador de Tarefas")
        self.root.geometry("900x550")

        self.label_cpu = tk.Label(root, text="Uso da CPU: --%", font=("Arial", 14))
        self.label_cpu.pack(pady=10)

        self.progress_cpu = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
        self.progress_cpu.pack(pady=10)

    def atualizar_cpu(self, uso):
        self.label_cpu.config(text=f"Uso da CPU: {uso:.2f}%")
        self.progress_cpu["value"] = uso

#Controle das funcoes e do dashboard
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

            time.sleep(5)

#inicializacao do Gerenciador de Tarefas/Dashboard
#Main inicializadora
if __name__ == "__main__":
    root = tk.Tk()
    view = InterfaceDashboard(root)
    controller = ControleDashboard(view)
    root.mainloop()
