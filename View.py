import tkinter as tk
from tkinter import ttk, messagebox
from controller import SystemMonitorController
#Utilizando a biblioteca tkinter para interface
#Utilizando Monitor de Sistema (SystemMonitor) o qual le e processa informacoes

class InterfaceDashboard:
    def __init__(self, Dashboard):
        self.Dashboard = Dashboard
        #Aqui abre janela
        self.Dashboard.title("Dashboard/Gerenciador de Tarefas")
        self.Dashboard.geometry("1100x650")
        #Controller com intervalo de 5 segundos
        self.controller = SystemMonitorController(update_interval_sec=5)
        self.controller.start()

        #Aqui ele cria aba, uma para geral e outra para lista de processos
        self.abas = ttk.Notebook(self.Dashboard)
        self.aba_geral = ttk.Frame(self.abas)
        self.aba_processos = ttk.Frame(self.abas)
        self.abas.add(self.aba_geral, text="Visao Geral")
        self.abas.add(self.aba_processos, text="Processos")
        self.abas.pack(expand=1, fill="both")

        self.interface_aba_geral()  
        self.interface_processos_aba()
        self.atualizacao_interface()

    def interface_aba_geral(self):
        # Frame principal da aba
        frame_principal = tk.Frame(self.aba_geral)
        frame_principal.pack(fill="both", expand=True, padx=10, pady=10)

        # Frame para os gráficos à esquerda
        frame_grafico = tk.Frame(frame_principal)
        frame_grafico.pack(side="left", fill="y", padx=10)

        # Gráfico da CPU
        tk.Label(frame_grafico, text="Uso da CPU : ", font=("Arial", 12, "bold")).pack()
        self.GraficoCPU = tk.Canvas(frame_grafico, width=400, height=200, bg="dark gray")
        self.GraficoCPU.pack(pady=(0, 10))
        self.CPUuso_lista = [0] * 100 

        # Gráfico da Memória
        tk.Label(frame_grafico, text="Uso da Memória : ", font=("Arial", 12, "bold")).pack()
        self.GraficoMemoria = tk.Canvas(frame_grafico, width=400, height=200, bg="dark gray")
        self.GraficoMemoria.pack()
        self.MEMuso_lista = [0] * 100

        # Frame para as informações à direita
        frame_info = tk.Frame(frame_principal)
        frame_info.pack(side="left", fill="both", expand=True)

        self.cpu_uso = tk.Label(frame_info, text="Uso da CPU: --%", font=("Arial", 14))
        self.cpu_uso.pack(pady=5)
        self.cpu_parado = tk.Label(frame_info, text="Tempo ocioso: --%", font=("Arial", 12))
        self.cpu_parado.pack()

        self.memo_uso = tk.Label(frame_info, text="Uso de Memoria: --%", font=("Arial", 12))
        self.memo_uso.pack()
        self.swap_uso = tk.Label(frame_info, text="Uso de Swap: --%", font=("Arial", 12))
        self.swap_uso.pack()

        self.processos_num = tk.Label(frame_info, text="Total de Processos: --", font=("Arial", 12))
        self.processos_num.pack()
        self.threads_num = tk.Label(frame_info, text="Total de Threads: --", font=("Arial", 12))
        self.threads_num.pack()



    def interface_processos_aba(self):
        #funcao para montar lista de processos e mostrar na aba de processos e informar umas informacoes basicas
        self.listaprocessos = ttk.Treeview(self.aba_processos, columns=("PID", "User", "CPU", "Mem", "Cmd"), show='headings')
        for col in self.listaprocessos["columns"]:
            self.listaprocessos.heading(col, text=col)
            self.listaprocessos.column(col, width=150 if col != "Cmd" else 300, anchor='center')
        self.listaprocessos.pack(expand=True, fill="both")

        #botao para ver detalhe
        self.btn_detalhes = tk.Button(self.aba_processos, text="Ver Detalhes do Processo", command=self.ver_detalhes)
        self.btn_detalhes.pack(pady=10)

    def atualizacao_interface(self):
        info = self.controller.get_system_global_info()
        processos = self.controller.get_all_processes()

        self.cpu_uso.config(text=f"Uso da CPU: {info.cpu_usage_percent:.2f}%")
        self.cpu_parado.config(text=f"Tempo ocioso: {info.cpu_idle_percent:.2f}%")
        self.CPUuso_lista.append(info.cpu_usage_percent)
        self.CPUuso_lista.pop(0)
        self.MEMuso_lista.append(info.mem_used_percent)
        self.MEMuso_lista.pop(0)
        self.GraficoCPU.delete("all")
        self.memo_uso.config(text=f"Uso de Memoria: {info.mem_used_percent:.2f}%")
        self.swap_uso.config(text=f"Uso de Swap: {info.swap_used_percent:.2f}%")
        self.processos_num.config(text=f"Total de Processos: {info.total_processes}")
        self.threads_num.config(text=f"Total de Threads: {info.total_threads}")
        print("CPU:", info.cpu_usage_percent)
        print("Mem:", info.mem_used_percent)

        altura = 200
        largura = 400
        intervalo_atualizacao = 5  # segundos

        # -------------------- GRÁFICO CPU --------------------
        self.GraficoCPU.delete("all")

        # Eixo Y (0% a 100%)
        for i in range(0, 101, 20):
            y = altura - (i / 100 * altura)
            self.GraficoCPU.create_line(0, y, largura, y, fill="lightgray", dash=(2, 2))
            self.GraficoCPU.create_text(5, y, text=f"{i}%", anchor="w", fill="white", font=("Arial", 8))

        # Eixo X (tempo: 0s a 500s)
        for i in range(0, 101, 10):  # 10 pontos = 50s
            x = i * (largura / 100)
            tempo_seg = (100 - i) * intervalo_atualizacao
            self.GraficoCPU.create_line(x, 0, x, altura, fill="lightgray", dash=(2, 2))
            if tempo_seg % 25 == 0:  # marcação a cada 25s
                self.GraficoCPU.create_text(x, altura - 2, text=f"{tempo_seg}s", anchor="n", fill="white", font=("Arial", 8))

        # Linhas do gráfico
        for i in range(1, len(self.CPUuso_lista)):
            x1 = (i - 1) * (largura / len(self.CPUuso_lista))
            y1 = altura - (self.CPUuso_lista[i - 1] / 100 * altura)
            x2 = i * (largura / len(self.CPUuso_lista))
            y2 = altura - (self.CPUuso_lista[i] / 100 * altura)
            self.GraficoCPU.create_line(x1, y1, x2, y2, fill="blue", width=2)

        # -------------------- GRÁFICO MEMÓRIA --------------------
        self.GraficoMemoria.delete("all")

        # Eixo Y (0% a 100%)
        for i in range(0, 101, 20):
            y = altura - (i / 100 * altura)
            self.GraficoMemoria.create_line(0, y, largura, y, fill="lightgray", dash=(2, 2))
            self.GraficoMemoria.create_text(5, y, text=f"{i}%", anchor="w", fill="white", font=("Arial", 8))

        # Eixo X (tempo: 0s a 500s)
        for i in range(0, 101, 10):
            x = i * (largura / 100)
            tempo_seg = (100 - i) * intervalo_atualizacao
            self.GraficoMemoria.create_line(x, 0, x, altura, fill="lightgray", dash=(2, 2))
            if tempo_seg % 25 == 0:
                self.GraficoMemoria.create_text(x, altura - 2, text=f"{tempo_seg}s", anchor="n", fill="white", font=("Arial", 8))

        # Linhas do gráfico
        for i in range(1, len(self.MEMuso_lista)):
            x1 = (i - 1) * (largura / len(self.MEMuso_lista))
            y1 = altura - (self.MEMuso_lista[i - 1] / 100 * altura)
            x2 = i * (largura / len(self.MEMuso_lista))
            y2 = altura - (self.MEMuso_lista[i] / 100 * altura)
            self.GraficoMemoria.create_line(x1, y1, x2, y2, fill="green", width=2)

            
        for i in self.listaprocessos.get_children():
            self.listaprocessos.delete(i)
        for proc in sorted(processos, key=lambda p: p.cpu_percent, reverse=True):
            self.listaprocessos.insert("", "end", values=(
                proc.pid, proc.user, f"{proc.cpu_percent:.2f}%", f"{proc.mem_percent:.2f}%", proc.cmdline[:80]
            ))

        self.Dashboard.after(5000, self.atualizacao_interface)

    def ver_detalhes(self):
        selected = self.listaprocessos.selection()
        if not selected:
            messagebox.showwarning("Selecao", "Selecione um processo na lista.")
            return

        pid = int(self.listaprocessos.item(selected[0], "values")[0])
        proc = self.controller.get_process_by_pid(pid)
        threads = self.controller.load_and_get_threads_for_process(pid)

        janela_detalhes = tk.Toplevel(self.Dashboard)
        janela_detalhes.title(f"Detalhes do Processo PID {pid}")
        janela_detalhes.geometry("600x400")

        tk.Label(janela_detalhes, text=f"Usuario: {proc.user}").pack()
        tk.Label(janela_detalhes, text=f"CPU %: {proc.cpu_percent:.2f} | Mem %: {proc.mem_percent:.2f}").pack()
        tk.Label(janela_detalhes, text=f"Inicio: {proc.start_time_str}").pack()
        tk.Label(janela_detalhes, text=f"Comando: {proc.cmdline}").pack()

        tk.Label(janela_detalhes, text=f"Threads:").pack(pady=5)
        listathreads = ttk.Treeview(janela_detalhes, columns=("TID", "Nome", "Estado"), show="headings")
        for col in ("TID", "Nome", "Estado"):
            listathreads.heading(col, text=col)
            listathreads.column(col, width=150, anchor='center')
        for thr in threads:
            listathreads.insert("", "end", values=(thr.tid, thr.name, thr.state))
        listathreads.pack(expand=True, fill="both")


if __name__ == "__main__":
    root = tk.Tk()
    app = InterfaceDashboard(root)
    root.mainloop()
