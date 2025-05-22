import tkinter as tk
from tkinter import ttk, messagebox
from controller import SystemMonitorController


class InterfaceDashboard:
    def __init__(self, master):
        self.master = master
        self.master.title("Dashboard/Gerenciador de Tarefas")
        self.master.geometry("1100x650")

        self.controller = SystemMonitorController(update_interval_sec=2)
        self.controller.start()

        self.tabs = ttk.Notebook(master)
        self.tab_global = ttk.Frame(self.tabs)
        self.tab_processos = ttk.Frame(self.tabs)
        self.tabs.add(self.tab_global, text="Visão Global")
        self.tabs.add(self.tab_processos, text="Processos")
        self.tabs.pack(expand=1, fill="both")

        self.setup_global_tab()
        self.setup_processos_tab()
        self.refresh_view()

    def setup_global_tab(self):
        self.lbl_cpu = tk.Label(self.tab_global, text="Uso da CPU: --%", font=("Arial", 14))
        self.lbl_cpu.pack(pady=5)
        self.lbl_idle = tk.Label(self.tab_global, text="Tempo ocioso: --%", font=("Arial", 12))
        self.lbl_idle.pack()

        self.lbl_mem = tk.Label(self.tab_global, text="Uso de Memória: --%", font=("Arial", 12))
        self.lbl_mem.pack()
        self.lbl_swap = tk.Label(self.tab_global, text="Uso de Swap: --%", font=("Arial", 12))
        self.lbl_swap.pack()

        self.lbl_proc = tk.Label(self.tab_global, text="Total de Processos: --", font=("Arial", 12))
        self.lbl_proc.pack()
        self.lbl_threads = tk.Label(self.tab_global, text="Total de Threads: --", font=("Arial", 12))
        self.lbl_threads.pack()

    def setup_processos_tab(self):
        self.tree = ttk.Treeview(self.tab_processos, columns=("PID", "User", "CPU", "Mem", "Cmd"), show='headings')
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150 if col != "Cmd" else 300, anchor='center')
        self.tree.pack(expand=True, fill="both")

        self.btn_detalhes = tk.Button(self.tab_processos, text="Ver Detalhes do Processo", command=self.ver_detalhes)
        self.btn_detalhes.pack(pady=10)

    def refresh_view(self):
        info = self.controller.get_system_global_info()
        processos = self.controller.get_all_processes()

        self.lbl_cpu.config(text=f"Uso da CPU: {info.cpu_usage_percent:.2f}%")
        self.lbl_idle.config(text=f"Tempo ocioso: {info.cpu_idle_percent:.2f}%")
        self.lbl_mem.config(text=f"Uso de Memória: {info.mem_used_percent:.2f}%")
        self.lbl_swap.config(text=f"Uso de Swap: {info.swap_used_percent:.2f}%")
        self.lbl_proc.config(text=f"Total de Processos: {info.total_processes}")
        self.lbl_threads.config(text=f"Total de Threads: {info.total_threads}")

        for i in self.tree.get_children():
            self.tree.delete(i)
        for proc in sorted(processos, key=lambda p: p.cpu_percent, reverse=True):
            self.tree.insert("", "end", values=(
                proc.pid, proc.user, f"{proc.cpu_percent:.2f}%", f"{proc.mem_percent:.2f}%", proc.cmdline[:80]
            ))

        self.master.after(2000, self.refresh_view)

    def ver_detalhes(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Seleção", "Selecione um processo na lista.")
            return

        pid = int(self.tree.item(selected[0], "values")[0])
        proc = self.controller.get_process_by_pid(pid)
        threads = self.controller.load_and_get_threads_for_process(pid)

        detalhes_win = tk.Toplevel(self.master)
        detalhes_win.title(f"Detalhes do Processo PID {pid}")
        detalhes_win.geometry("600x400")

        tk.Label(detalhes_win, text=f"Usuário: {proc.user}").pack()
        tk.Label(detalhes_win, text=f"CPU %: {proc.cpu_percent:.2f} | Mem %: {proc.mem_percent:.2f}").pack()
        tk.Label(detalhes_win, text=f"Início: {proc.start_time_str}").pack()
        tk.Label(detalhes_win, text=f"Comando: {proc.cmdline}").pack()

        tk.Label(detalhes_win, text=f"Threads:").pack(pady=5)
        tree_thr = ttk.Treeview(detalhes_win, columns=("TID", "Nome", "Estado"), show="headings")
        for col in ("TID", "Nome", "Estado"):
            tree_thr.heading(col, text=col)
            tree_thr.column(col, width=150, anchor='center')
        for thr in threads:
            tree_thr.insert("", "end", values=(thr.tid, thr.name, thr.state))
        tree_thr.pack(expand=True, fill="both")


if __name__ == "__main__":
    root = tk.Tk()
    app = InterfaceDashboard(root)
    root.mainloop()
