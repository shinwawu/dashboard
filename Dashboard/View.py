# Como estamos utilizando modelo MVC, estaremos encapsulando para melhor visualizacao
# aqui vai ser a parte View, onde vai estar presente a interface

import tkinter as tk

class InterfaceDashboard:
    def __init__(self, Dashboard):
        self.Dashboard = Dashboard
        self.Dashboard.title("Dashboard/Gerenciador de Tarefas")
        self.Dashboard.geometry("900x550")

        self.CPULegenda = tk.Label(Dashboard, text="Uso da CPU: --%", font=("Arial", 14))
        self.CPULegenda.pack(pady=10)

        self.CPUtempoparado = tk.Label(Dashboard, text="Tempo ocioso: --%", font=("Arial", 12))
        self.CPUtempoparado.pack(pady=5)

        
        self.GraficoCPU = tk.Canvas(Dashboard, width=800, height=200, bg="gray")
        self.GraficoCPU.pack(pady=10)
        self.CPUuso_lista = [0] * 100

    def CPU_atualizacao(self, uso, ocioso):
        self.CPULegenda.config(text=f"Uso da CPU: {uso:.2f}%")
        self.CPUtempoparado.config(text=f"Uso da CPU: {uso:.2f}%")
        
        self.CPUuso_lista.append(uso)
        self.CPUuso_lista.pop(0)
        self.GraficoCPU.delete("all")
        altura = 200
        largura = 800
        for i in range(1, len(self.CPUuso_lista)):
            x1 = (i - 1) * (largura / len(self.CPUuso_lista))
            y1 = altura - (self.CPUuso_lista[i - 1] / 100 * altura)
            x2 = i * (largura / len(self.CPUuso_lista))
            y2 = altura - (self.CPUuso_lista[i] / 100 * altura)
            self.GraficoCPU.create_line(x1, y1, x2, y2, fill="blue", width=4)

