import os
import threading
import time
import tkinter as tk
from tkinter import ttk

#parte Model do modelo MVC
def LeituraCPU():
    with open("/proc/stat", "r") as f:
        linha = f.readline()
    cpupartes = list(map(int, linha.split()[1:]))
    tempototal = sum(cpupartes)
    tempoparado = cpupartes[3]
    return tempototal, tempoparado

# parte View do modelo MVC
class InterfaceDashboard:
    def __init__(self, Dashboard):
        self.Dashboard = Dashboard
        self.Dashboard.title("Dashboard/Gerenciador de Tarefas")
        self.Dashboard.geometry("900x550")

        self.CPULegenda = tk.Label(Dashboard, text="Uso da CPU: --%", font=("Arial", 14))
        self.CPULegenda.pack(pady=10)

        #Grafico da CPU
        self.GraficoCPU = tk.Canvas(Dashboard, width=800, height=200, bg="black")
        self.GraficoCPU.pack(pady=10)
        self.CPUuso_lista = [0] * 100 

    def CPU_atualizacao(self, uso):
        self.CPULegenda.config(text=f"Uso da CPU: {uso:.2f}%")

        #Atualizacao dos graficos
        self.CPUuso_lista.append(uso)
        self.CPUuso_lista.pop(0)

        #Redesenha o grafico apos a atualizacao
        self.GraficoCPU.delete("all")
        altura = 200
        largura = 800
        for i in range(1, len(self.CPUuso_lista)):
            x1 = (i - 1) * (largura / len(self.CPUuso_lista))
            y1 = altura - (self.CPUuso_lista[i - 1] / 100 * altura)
            x2 = i * (largura / len(self.CPUuso_lista))
            y2 = altura - (self.CPUuso_lista[i] / 100 * altura)
            self.GraficoCPU.create_line(x1, y1, x2, y2, fill="blue", width=2)

#parte Control do modelo MVC
class ControleDashboard:
    def __init__(self, Interface):
        self.Interface = Interface
        self.CPUtotal_tempoanterior, self.CPUparado_tempoanterior = LeituraCPU()
        self.thread = threading.Thread(target=self.atualizacao_continua)
        self.thread.daemon = True
        self.thread.start()

    def atualizacao_continua(self):
        while True:
            tempototal, tempoparado = LeituraCPU()
            diferenca_tempo = tempototal - self.CPUtotal_tempoanterior
            diferenca_parado = tempoparado - self.CPUparado_tempoanterior

            CPU_uso = 100 * (1 - diferenca_parado / diferenca_tempo) if diferenca_tempo > 0 else 0
            self.CPUtotal_tempoanterior, self.CPUparado_tempoanterior = tempototal, tempoparado

            self.Interface.Dashboard.after(0, self.Interface.CPU_atualizacao, CPU_uso)
            time.sleep(5)

# Aqui esta a inicializacao do programa
if __name__ == "__main__":
    Dashboard = tk.Tk()
    Interface = InterfaceDashboard(Dashboard)
    Controle = ControleDashboard(Interface)
    Dashboard.mainloop()
