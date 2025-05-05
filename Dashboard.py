import tkinter as tk
import subprocess

def uso_cpu_top():
    resultado = subprocess.run(["top", "-bn1"], stdout=subprocess.PIPE, text=True)
    for linha in resultado.stdout.split("\n"):
        if "Cpu(s)" in linha:
            partes = linha.split()
            uso = float(partes[1].replace(",", "."))
            return uso
    return None

class Dashboard:
    def __init__(self):
        self.window = tk.Tk()
        self.window.geometry("400x200")
        self.window.title("Dashboard de CPU")

        self.label_cpu = tk.Label(self.window, text="Uso da CPU: --%", font=("Arial", 24))
        self.label_cpu.pack(pady=50)

        self.atualizar_cpu()  # Começa o loop de atualização

        self.window.mainloop()

    def atualizar_cpu(self):
        uso = uso_cpu_top()
        if uso is not None:
            self.label_cpu.config(text=f"Uso da CPU: {uso:.2f}%")
        else:
            self.label_cpu.config(text="Erro ao obter CPU")
        self.window.after(1000, self.atualizar_cpu)  # Atualiza a cada 1000ms (1 segundo)

if __name__ == "__main__":
    Dashboard()
