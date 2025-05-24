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
        #frame principal da aba geral
        frame_principal = tk.Frame(self.aba_geral, bg="gray15")
        frame_principal.pack(fill="both", expand=True, padx=10, pady=10)

        #frame de gráficos em grade
        frame_grafico = tk.Frame(frame_principal, bg="gray15")
        frame_grafico.grid(row=0, column=0, sticky="nw")

        frame_info = tk.Frame(frame_principal, bg="gray15")
        frame_info.grid(row=0, column=1, sticky="ne")

        #criando o gráfico da CPU
        self.label_titulo_cpu = tk.Label(frame_grafico, text="Uso da CPU: --%", font=("Arial", 12, "bold"), bg="gray15", fg="white")
        self.label_titulo_cpu.grid(row=0, column=0)
        self.GraficoCPU = tk.Canvas(frame_grafico, width=400, height=250, bg="dark gray")
        self.GraficoCPU.grid(row=1, column=0, padx=5, pady=5)
        self.CPUuso_lista = [0] * 100

        #criando o gráfico de processos
        self.label_titulo_processos = tk.Label(frame_grafico, text="Total de Processos: --", font=("Arial", 12, "bold"), bg="gray15", fg="white")
        self.label_titulo_processos.grid(row=0, column=1)
        self.GraficoProcessos = tk.Canvas(frame_grafico, width=400, height=250, bg="dark gray")
        self.GraficoProcessos.grid(row=1, column=1, padx=5, pady=5)
        self.processos_lista = [0] * 100

        #criando o gráfico de memoria
        self.label_titulo_memoria = tk.Label(frame_grafico, text="Uso da Memória: --%", font=("Arial", 12, "bold"), bg="gray15", fg="white")
        self.label_titulo_memoria.grid(row=2, column=0)
        self.GraficoMemoria = tk.Canvas(frame_grafico, width=400, height=250, bg="dark gray")
        self.GraficoMemoria.grid(row=3, column=0, padx=5, pady=5)
        self.MEMuso_lista = [0] * 100
        self.label_swap_info = tk.Label(frame_grafico,text="Swap Usado: -- MB",font=("Arial", 10),bg="gray15",fg="white")
        self.label_swap_info.grid(row=4, column=0)

        #criando os graficos de threads
        self.label_titulo_threads = tk.Label(frame_grafico, text="Total de Threads: --", font=("Arial", 12, "bold"), bg="gray15", fg="white")
        self.label_titulo_threads.grid(row=2, column=1)
        self.GraficoThreads = tk.Canvas(frame_grafico, width=400, height=250, bg="dark gray")
        self.GraficoThreads.grid(row=3, column=1, padx=5, pady=5)
        self.threads_lista = [0] * 100
        
        #tabela de estatisticas
        frame_estat = tk.Frame(frame_grafico, bg="gray15")
        frame_estat.grid(row=0, column=3, rowspan=4, sticky="ns", padx=10)

        tk.Label(frame_estat, text="Estatísticas", font=("Arial", 12, "bold"), bg="gray15", fg="white").pack(pady=(0, 10))

        self.estat_tabela = ttk.Treeview(frame_estat,columns=("Grafico", "Min", "Max", "Media", "Atual"),show="headings",height=11)
        for col in ("Grafico", "Min", "Max", "Media", "Atual"):
            self.estat_tabela .heading(col, text=col)
            self.estat_tabela .column(col, anchor="center", width=80)
        self.estat_tabela .pack()

        #criando o gráfico de memoria usada
        self.label_titulo_mem_barra = tk.Label(frame_grafico,text="Memória Usada",font=("Arial", 12, "bold"),bg="gray15",fg="white")
        self.label_titulo_mem_barra.grid(row=0, column=2)
        self.GraficoBarraMemoria = tk.Canvas(frame_grafico, width=200, height=250, bg="dark gray")
        self.GraficoBarraMemoria.grid(row=1, column=2, rowspan=3, padx=5, pady=5, sticky="n")






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
        #Pega informacoes geral do processador e dos processos
        info = self.controller.get_system_global_info()
        processos = self.controller.get_all_processes()

        #Demonstra informacoes em texto para usuario
        self.label_titulo_cpu.config(
    text=f"Uso da CPU: {info.cpu_usage_percent:.2f}% | Ocioso: {info.cpu_idle_percent:.2f}%"
)

        #aqui estamos atualizando a lista de cada grafico
        self.CPUuso_lista.append(info.cpu_usage_percent)
        self.CPUuso_lista.pop(0)
        self.MEMuso_lista.append(info.mem_used_percent)
        self.label_titulo_memoria.config(text=f"Uso da Memória: {info.mem_used_percent:.2f}% | Livre: {100 - info.mem_used_percent:.2f}%")
        self.MEMuso_lista.pop(0)
        self.label_swap_info.config(text=f"Swap Usado: {info.swap_used_kb / 1024:.2f} MB")
        self.processos_lista.append(info.total_processes)
        self.processos_lista.pop(0)
        self.threads_lista.append(info.total_threads)
        self.threads_lista.pop(0)
        self.label_titulo_processos.config(text=f"Total de Processos: {info.total_processes}")
        self.label_titulo_threads.config(text=f"Total de Threads: {info.total_threads}")


        altura = 230
        largura = 400
        intervalo_atualizacao = 5

        margem_x = 35
        margem_y = 8

        #Gráfico da CPU
        self.GraficoCPU.delete("all")
        for i in range(0, 101, 20):  #Eixo Y, cria a legenda 
            y = altura - (i / 100 * altura) + margem_y
            self.GraficoCPU.create_line(margem_x, y, largura, y, fill="lightgray", dash=(2, 2))
            self.GraficoCPU.create_text(margem_x - 5, y, text=f"{i}%", anchor="e", fill="white", font=("Arial", 8))
        for i in range(0, len(self.CPUuso_lista), 10): #Eixo X, cria a legenda 
            x = margem_x + i * ((largura - margem_x) / len(self.CPUuso_lista))
            tempo_seg = (len(self.CPUuso_lista) - i) * intervalo_atualizacao
            self.GraficoCPU.create_line(x, margem_y, x, altura + margem_y, fill="lightgray", dash=(2, 2))
            self.GraficoCPU.create_text(x, altura + margem_y + 2, text=f"-{tempo_seg}s", anchor="n", fill="white", font=("Arial", 8))

        for i in range(1, len(self.CPUuso_lista)): #Cria as linhas do grafico
            x1 = margem_x + (i - 1) * ((largura - margem_x) / len(self.CPUuso_lista))
            y1 = altura - (self.CPUuso_lista[i - 1] / 100 * altura) + margem_y
            x2 = margem_x + i * ((largura - margem_x) / len(self.CPUuso_lista))
            y2 = altura - (self.CPUuso_lista[i] / 100 * altura) + margem_y
            self.GraficoCPU.create_line(x1, y1, x2, y2, fill="light blue", width=2)

        #Grafico de Memoria
        self.GraficoMemoria.delete("all")
        for i in range(0, 101, 20):  #Eixo Y, cria a legenda 
            y = altura - (i / 100 * altura) + margem_y
            self.GraficoMemoria.create_line(margem_x, y, largura, y, fill="lightgray", dash=(2, 2))
            self.GraficoMemoria.create_text(margem_x - 5, y, text=f"{i}%", anchor="e", fill="white", font=("Arial", 8))
        for i in range(0, len(self.MEMuso_lista), 10): #Eixo X, cria a legenda 
            x = margem_x + i * ((largura - margem_x) / len(self.MEMuso_lista))
            tempo_seg = (len(self.MEMuso_lista) - i) * intervalo_atualizacao
            self.GraficoMemoria.create_line(x, margem_y, x, altura + margem_y, fill="lightgray", dash=(2, 2))
            self.GraficoMemoria.create_text(x, altura + margem_y + 2, text=f"-{tempo_seg}s", anchor="n", fill="white", font=("Arial", 8))


        for i in range(1, len(self.MEMuso_lista)): #Cria as linhas do grafico
            x1 = margem_x + (i - 1) * ((largura - margem_x) / len(self.MEMuso_lista))
            y1 = altura - (self.MEMuso_lista[i - 1] / 100 * altura) + margem_y
            x2 = margem_x + i * ((largura - margem_x) / len(self.MEMuso_lista))
            y2 = altura - (self.MEMuso_lista[i] / 100 * altura) + margem_y
            self.GraficoMemoria.create_line(x1, y1, x2, y2, fill="light green", width=2)
        
        #grafico de processos
        self.GraficoProcessos.delete("all")
        max_proc = max(self.processos_lista) or 1

        for i in range(0, max_proc + 1, max(1, max_proc // 10)):
            y = altura - (i / max_proc * altura) + margem_y
            self.GraficoProcessos.create_line(margem_x, y, largura, y, fill="lightgray", dash=(2, 2))
            self.GraficoProcessos.create_text(margem_x - 5, y, text=str(i), anchor="e", fill="white", font=("Arial", 8))
        # Eixo X do gráfico de processos
        for i in range(0, len(self.processos_lista), 10):
            x = margem_x + i * ((largura - margem_x) / len(self.processos_lista))
            tempo_seg = (len(self.processos_lista) - i) * intervalo_atualizacao
            self.GraficoProcessos.create_line(x, margem_y, x, altura + margem_y, fill="lightgray", dash=(2, 2))
            self.GraficoProcessos.create_text(x, altura + margem_y + 2, text=f"-{tempo_seg}s", anchor="n", fill="white", font=("Arial", 8))


        for i in range(1, len(self.processos_lista)):
            x1 = margem_x + (i - 1) * ((largura - margem_x) / len(self.processos_lista))
            y1 = altura - (self.processos_lista[i - 1] / max_proc * altura) + margem_y
            x2 = margem_x + i * ((largura - margem_x) / len(self.processos_lista))
            y2 = altura - (self.processos_lista[i] / max_proc * altura) + margem_y
            self.GraficoProcessos.create_line(x1, y1, x2, y2, fill="cyan", width=2)


        # === GRÁFICO DE THREADS ===
        self.GraficoThreads.delete("all")
        max_thr = max(self.threads_lista) or 1

        for i in range(0, max_thr + 1, max(1, max_thr // 10)):
            y = altura - (i / max_thr * altura) + margem_y
            self.GraficoThreads.create_line(margem_x, y, largura, y, fill="lightgray", dash=(2, 2))
            self.GraficoThreads.create_text(margem_x - 5, y, text=str(i), anchor="e", fill="white", font=("Arial", 8))
        # Eixo X do gráfico de threads
        for i in range(0, len(self.threads_lista), 10):
            x = margem_x + i * ((largura - margem_x) / len(self.threads_lista))
            tempo_seg = (len(self.threads_lista) - i) * intervalo_atualizacao
            self.GraficoThreads.create_line(x, margem_y, x, altura + margem_y, fill="lightgray", dash=(2, 2))
            self.GraficoThreads.create_text(x, altura + margem_y + 2, text=f"-{tempo_seg}s", anchor="n", fill="white", font=("Arial", 8))


        for i in range(1, len(self.threads_lista)):
            x1 = margem_x + (i - 1) * ((largura - margem_x) / len(self.threads_lista))
            y1 = altura - (self.threads_lista[i - 1] / max_thr * altura) + margem_y
            x2 = margem_x + i * ((largura - margem_x) / len(self.threads_lista))
            y2 = altura - (self.threads_lista[i] / max_thr * altura) + margem_y
            self.GraficoThreads.create_line(x1, y1, x2, y2, fill="magenta", width=2)


        # grafico memoria usada
       
       
        self.GraficoBarraMemoria.delete("all")
        mem_usada_kb = info.mem_used_kb  #pega as informacoes da memoria
        mem_total_kb = info.mem_total_kb

        mem_usada_mb = mem_usada_kb / 1024  #converte para MB
        mem_total_mb = mem_total_kb / 1024
        self.label_titulo_mem_barra.config(text=f"Memória Usada: {mem_usada_mb:.1f} MB / {mem_total_mb:.1f} MB")
        # Dimensões do canvas
        canvas_altura = 250
        canvas_largura = 200
        largura_barra = 70

        #calcula altura da barra
        if mem_total_mb > 0:
            altura_usada = (mem_usada_mb / mem_total_mb) * canvas_altura
        else:
            altura_usada = 0

        #coordenadas do grafico horizontal
        x_meio = canvas_largura / 2
        x0 = x_meio - largura_barra / 2
        x1 = x_meio + largura_barra / 2

        #coordenadas do grafico vertical
        y1 = canvas_altura  
        y0 = y1 - altura_usada  

        #cor da barra
        mem_percent = info.mem_used_percent
        if mem_percent >= 90:
            cor = "red"
        elif mem_percent >= 70:
            cor = "orange"
        else:
            cor = "light blue"

        #desenha a barra
        self.GraficoBarraMemoria.create_rectangle(x0, y0, x1, y1, fill=cor)

        #informa quantos MB estao sendo utilizados
        texto_mem = f"{mem_usada_mb:.1f} MB / {mem_total_mb:.1f} MB"
        self.GraficoBarraMemoria.create_text(canvas_largura / 2, y0 - 10, text=texto_mem, fill="white", font=("Arial", 8), anchor="s")


        
        #atualiza a listadeprocessos
        for i in self.listaprocessos.get_children():
            self.listaprocessos.delete(i)
        for proc in sorted(processos, key=lambda p: p.cpu_percent, reverse=True):
            self.listaprocessos.insert("", "end", values=(
                proc.pid, proc.user, f"{proc.cpu_percent:.2f}%", f"{proc.mem_percent:.2f}%", proc.cmdline[:80]
            ))
            
        #tabela de estatisticas
        self.estat_tabela.delete(*self.estat_tabela.get_children())

        def calc_estat(nome, lista):
            # Remove apenas os zeros iniciais
            i = 0
            while i < len(lista) and lista[i] == 0:
                i += 1
            valores_validos = lista[i:]
            if not valores_validos:
                return (nome, "-", "-", "-", "-")
            return(nome,f"{min(valores_validos):.2f}",f"{max(valores_validos):.2f}",f"{sum(valores_validos)/len(valores_validos):.2f}",f"{lista[-1]:.2f}")


        for nome, lista in [
            ("CPU (%)", self.CPUuso_lista),
            ("Mem (%)", self.MEMuso_lista),
            ("Procs", self.processos_lista),
            ("Threads", self.threads_lista),
        ]:
            self.estat_tabela.insert("", "end", values=calc_estat(nome, lista))

        #atualiza a cada 5s a interface
        self.Dashboard.after(5000, self.atualizacao_interface)

    def ver_detalhes(self):
        selected = self.listaprocessos.selection()
        if not selected:
            messagebox.showwarning("Seleção", "Selecione um processo na lista.")
            return

        pid = int(self.listaprocessos.item(selected[0], "values")[0])
        proc = self.controller.get_process_by_pid(pid)
        threads = self.controller.load_and_get_threads_for_process(pid)

        # Cria nova janela para os detalhes
        janela_detalhes = tk.Toplevel(self.Dashboard)
        janela_detalhes.title(f"Detalhes do Processo PID {pid}")
        janela_detalhes.geometry("750x600")
        janela_detalhes.configure(bg="gray15")

        #Frame com informações principais
        frame_info = tk.Frame(janela_detalhes, bg="gray15")
        frame_info.pack(padx=10, pady=10, anchor="w", fill="x")

        tk.Label(frame_info, text=f"Usuário: {proc.user}", bg="gray15", fg="white").pack(anchor="w")
        tk.Label(frame_info, text=f"CPU %: {proc.cpu_percent:.2f} | Mem %: {proc.mem_percent:.2f}", bg="gray15", fg="white").pack(anchor="w")
        tk.Label(frame_info, text=f"Início: {proc.start_time_str}", bg="gray15", fg="white").pack(anchor="w")
        tk.Label(frame_info, text=f"Comando: {proc.cmdline}", bg="gray15", fg="white", wraplength=700, justify="left").pack(anchor="w")

        # Frame com informações de memória detalhadas
        frame_memoria = tk.LabelFrame(janela_detalhes,text="Uso de Memória (em KB)",bg="gray15",fg="white",font=("Arial", 10, "bold"))
        frame_memoria.pack(fill="x", padx=10, pady=10)

        campos_mem = [("Memória Virtual Total (VmSize)", proc.vm_size_kb),("Memória Física (VmRSS)", proc.vm_rss_kb),("Pico de Memória Virtual (VmPeak)", proc.vm_peak_kb),("Memória do Código (VmExe)", proc.vm_exe_kb),("Heap / Dados (VmData)", proc.vm_data_kb),("Pilha (VmStk)", proc.vm_stk_kb),("Bibliotecas Compartilhadas (VmLib)", proc.vm_lib_kb),("Memória em Swap (VmSwap)", proc.vm_swap_kb),("Tamanho Tabelas de Página (VmPTE)", proc.vm_pte_kb),]

        for nome, valor in campos_mem:
            tk.Label(frame_memoria, text=f"{nome}: {valor} KB", bg="gray15", fg="white").pack(anchor="w")

        # Frame com lista de threads
        tk.Label(janela_detalhes,text="Threads:",bg="gray15",fg="white",font=("Arial", 10, "bold")).pack(pady=(10, 0), anchor="w", padx=10)

        listathreads = ttk.Treeview(janela_detalhes,columns=("TID", "Nome", "Estado"),show="headings")

        for col in ("TID", "Nome", "Estado"):
            listathreads.heading(col, text=col)
            listathreads.column(col, width=200 if col == "Nome" else 100, anchor='center')

        for thr in threads:
            listathreads.insert("", "end", values=(thr.tid, thr.name, thr.state))

        listathreads.pack(expand=True, fill="both", padx=10, pady=(0, 10))



#inicializacao da main
if __name__ == "__main__":
    root = tk.Tk()
    root.configure(bg="gray15")
    app = InterfaceDashboard(root)
    root.mainloop()

