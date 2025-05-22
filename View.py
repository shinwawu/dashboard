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
        frame_principal = tk.Frame(self.aba_geral)
        frame_principal.pack(fill="both", expand=True, padx=10, pady=10)

        # Gráficos e informações lado a lado usando grid
        frame_grafico = tk.Frame(frame_principal)
        frame_grafico.grid(row=0, column=0, sticky="n")

        frame_info = tk.Frame(frame_principal)
        frame_info.grid(row=0, column=1, sticky="n")

        #Gráfico da CPU
        tk.Label(frame_grafico, text="Uso da CPU", font=("Arial", 12, "bold")).pack()
        self.GraficoCPU = tk.Canvas(frame_grafico, width=400, height=200, bg="dark gray")
        self.GraficoCPU.pack(pady=(0, 10))
        self.CPUuso_lista = [0] * 100 


        # Frame horizontal para o gráfico de memória e barra de memória total
        frame_memoria = tk.Frame(frame_grafico)
        frame_memoria.pack()

        # Gráfico da Memória
        tk.Label(frame_memoria, text="Uso da Memória (%)", font=("Arial", 12, "bold")).grid(row=0, column=0, sticky="n")
        self.GraficoMemoria = tk.Canvas(frame_memoria, width=400, height=200, bg="dark gray")
        self.GraficoMemoria.grid(row=1, column=0)

        # Gráfico de barra da Memória usada
        tk.Label(frame_memoria, text="Memória Usada", font=("Arial", 12, "bold")).grid(row=0, column=1, sticky="n")
        self.GraficoBarraMemoria = tk.Canvas(frame_memoria, width=200, height=200, bg="dark gray")
        self.GraficoBarraMemoria.grid(row=1, column=1, padx=10)
        self.MEMuso_lista = [0] * 100

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
        self.memo_uso.config(text=f"Uso de Memoria: {info.mem_used_percent:.2f}%")
        self.swap_uso.config(text=f"Uso de Swap: {info.swap_used_percent:.2f}%")
        self.processos_num.config(text=f"Total de Processos: {info.total_processes}")
        self.threads_num.config(text=f"Total de Threads: {info.total_threads}")

        altura = 200
        largura = 400
        intervalo_atualizacao = 5

        margem_x = 30
        margem_y = 10

        # === GRÁFICO DA CPU ===
        self.GraficoCPU.delete("all")
        for i in range(0, 101, 20):
            y = altura - (i / 100 * altura) + margem_y
            self.GraficoCPU.create_line(margem_x, y, largura, y, fill="lightgray", dash=(2, 2))
            self.GraficoCPU.create_text(margem_x - 5, y, text=f"{i}%", anchor="e", fill="white", font=("Arial", 8))
        for i in range(0, 101, 10):
            x = margem_x + i * ((largura - margem_x) / 100)
            tempo_seg = (100 - i) * intervalo_atualizacao
            self.GraficoCPU.create_line(x, margem_y, x, altura + margem_y, fill="lightgray", dash=(2, 2))
            if tempo_seg % 25 == 0:
                self.GraficoCPU.create_text(x, altura + margem_y + 10, text=f"{tempo_seg}s", anchor="n", fill="white", font=("Arial", 8))
        for i in range(1, len(self.CPUuso_lista)):
            x1 = margem_x + (i - 1) * ((largura - margem_x) / len(self.CPUuso_lista))
            y1 = altura - (self.CPUuso_lista[i - 1] / 100 * altura) + margem_y
            x2 = margem_x + i * ((largura - margem_x) / len(self.CPUuso_lista))
            y2 = altura - (self.CPUuso_lista[i] / 100 * altura) + margem_y
            self.GraficoCPU.create_line(x1, y1, x2, y2, fill="light blue", width=2)

        # === GRÁFICO DA MEMÓRIA ===
        self.GraficoMemoria.delete("all")
        for i in range(0, 101, 20):
            y = altura - (i / 100 * altura) + margem_y
            self.GraficoMemoria.create_line(margem_x, y, largura, y, fill="lightgray", dash=(2, 2))
            self.GraficoMemoria.create_text(margem_x - 5, y, text=f"{i}%", anchor="e", fill="white", font=("Arial", 8))
        for i in range(0, 101, 10):
            x = margem_x + i * ((largura - margem_x) / 100)
            tempo_seg = (100 - i) * intervalo_atualizacao
            self.GraficoMemoria.create_line(x, margem_y, x, altura + margem_y, fill="lightgray", dash=(2, 2))
            if tempo_seg % 25 == 0:
                self.GraficoCPU.create_text(x, altura + margem_y + 10, text=f"{tempo_seg}s", anchor="n", fill="white", font=("Arial", 8))
        for i in range(1, len(self.MEMuso_lista)):
            x1 = margem_x + (i - 1) * ((largura - margem_x) / len(self.MEMuso_lista))
            y1 = altura - (self.MEMuso_lista[i - 1] / 100 * altura) + margem_y
            x2 = margem_x + i * ((largura - margem_x) / len(self.MEMuso_lista))
            y2 = altura - (self.MEMuso_lista[i] / 100 * altura) + margem_y
            self.GraficoMemoria.create_line(x1, y1, x2, y2, fill="light green", width=2)

        # grafico memoria usada
       
       
        self.GraficoBarraMemoria.delete("all")
        mem_usada_kb = info.mem_used_kb
        mem_total_kb = info.mem_total_kb

        mem_usada_mb = mem_usada_kb / 1024
        mem_total_mb = mem_total_kb / 1024

        # Altura total do canvas
        altura_barra = 170

        canvas_largura = 200
        largura_barra = 70
        x_centro = (canvas_largura - largura_barra) / 2  # Centraliza a barra no Canvas
        # Altura proporcional usada
        if mem_total_mb > 0:
            altura_usada = (mem_usada_mb / mem_total_mb) * altura_barra
        else:
            altura_usada = 0  # ou altura_barra para indicar uso total como fallback

        y0 = altura_barra - altura_usada


        # Desenha barra preenchida
        # Escolhe cor baseada no percentual
        mem_percent = info.mem_used_percent
        if mem_percent >= 90:
            cor = "red"
        elif mem_percent >= 70:
            cor = "orange"
        else:
            cor = "light blue"

        self.GraficoBarraMemoria.create_rectangle(x_centro, y0,x_centro + largura_barra, altura_barra,fill=cor)


        # Rótulo de texto
        texto_mem = f"{mem_usada_mb:.1f} MB / {mem_total_mb:.1f} MB"
        self.GraficoBarraMemoria.create_text(canvas_largura / 2, 5, text=texto_mem,fill="white",font=("Arial", 8),anchor="n")

        
            
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
