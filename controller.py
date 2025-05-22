# scr/controller.py
"""
Controlador principal do sistema de monitoramento que gerencia a coleta de dados
e fornece uma interface para a camada de visualização.

Este módulo implementa o padrão MVC (Model-View-Controller) como a camada de controle,
gerenciando a atualização periódica dos dados e calculando métricas derivadas.
"""

import threading
import time
from typing import Dict, List, Optional

# Importações dos modelos e funções de coleta de dados
from model.data_model import SystemGlobalInfo, ProcessInfo, ThreadInfo
import system_monitor  # Módulo para coleta direta de dados do sistema


class SystemMonitorController:
    """
    Controlador responsável pela coleta e processamento dos dados do sistema.

    Gerencia uma thread separada para atualização periódica dos dados e disponibiliza
    métodos para a camada de visualização acessar informações processadas do sistema.
    """

    def __init__(self, update_interval_sec: float = 2.0) -> None:
        """
        Inicializa o controlador com configurações e estruturas de dados básicas.

        Args:
            update_interval_sec (float, optional): Intervalo em segundos entre atualizações.
                                                  Padrão é 2.0 segundos.
        """
        # Intervalo de atualização dos dados
        self.update_interval_sec: float = update_interval_sec

        # Instâncias para armazenar dados do sistema (protegidas por lock)
        self._system_global_info: SystemGlobalInfo = SystemGlobalInfo()
        self._processes_info_list: List[ProcessInfo] = []
        self._data_lock: threading.Lock = (
            threading.Lock()
        )  # Para acesso thread-safe aos dados

        # Dados da leitura anterior para cálculos de delta (uso de CPU)
        self._prev_global_cpu_times: List[int] = []  # Tempos de CPU globais anteriores
        self._prev_per_core_cpu_times: List[
            List[int]
        ] = []  # Tempos de CPU por core anteriores
        # Dicionário para armazenar tempos de CPU anteriores por processo
        self._prev_processes_cpu_times: Dict[
            int, Dict[str, int]
        ] = {}  # {pid: {"utime": x, "stime": y}}

        # Controle da thread de atualização
        self._update_thread: Optional[threading.Thread] = None
        self._running: threading.Event = (
            threading.Event()
        )  # Sinaliza para parar a thread

    def _update_data(self) -> None:
        """
        Coleta, processa e atualiza os dados do sistema e dos processos.

        Este método é executado periodicamente pela thread de atualização e executa:
        1. Coleta de informações globais do sistema (CPU, memória, etc.)
        2. Cálculo de percentuais de uso de CPU global e por core
        3. Coleta de informações sobre todos os processos
        4. Cálculo de métricas derivadas para cada processo (CPU%, mem%, etc.)
        5. Atualização thread-safe dos dados compartilhados
        """
        # --- 1. Coletar dados globais atuais do sistema ---
        # Cria uma nova instância para trabalho isolado (não afeta os dados compartilhados até o final)
        current_global_info_snapshot: SystemGlobalInfo = SystemGlobalInfo()
        # Popula a instância com dados brutos do sistema
        system_monitor.populate_system_global_data(current_global_info_snapshot)

        # --- 2. Calcular percentuais de uso de CPU ---
        # Calcula o percentual de uso global da CPU usando os dados anteriores como base
        current_global_info_snapshot.calculate_and_set_cpu_percent(
            prev_cpu_times=self._prev_global_cpu_times,
        )
        # Calcula o percentual de uso para cada núcleo de CPU
        current_global_info_snapshot.calculate_and_set_per_core_cpu_usages(
            prev_per_core_cpu_times=self._prev_per_core_cpu_times,
        )

        # --- 3. Coletar informações de todos os processos ---
        current_processes_list: List[ProcessInfo] = (
            system_monitor.get_all_processes_info_list()
        )

        # --- 4. Calcular métricas derivadas para cada processo ---
        # Dicionário para armazenar os tempos de CPU atuais para a próxima iteração
        new_prev_processes_cpu_times: Dict[int, Dict[str, int]] = {}

        # Calcula o delta total de jiffies do sistema entre esta leitura e a anterior
        # Este delta é necessário para calcular o percentual de CPU de cada processo
        delta_total_system_jiffies: int = (
            lambda curr, prev: sum(curr) - sum(prev) if prev and curr else 0
        )(
            current_global_info_snapshot.last_cpu_times_jiffies_all,
            self._prev_global_cpu_times,
        )

        # Contador de threads para atualizar a estatística global
        total_threads_count: int = 0

        # Calcula o tempo de boot do sistema (usado para determinar hora de início dos processos)
        system_boot_time_epoch: float = (
            time.time() - current_global_info_snapshot.uptime_seconds
        )

        # Itera sobre cada processo para calcular suas métricas
        for proc_info in current_processes_list:
            # Acumula o número total de threads de todos os processos
            total_threads_count += proc_info.num_threads

            # Armazena os tempos atuais deste processo para a próxima iteração
            new_prev_processes_cpu_times[proc_info.pid] = {
                "utime": proc_info.utime,  # Tempo em modo usuário
                "stime": proc_info.stime,  # Tempo em modo kernel
            }

            # Calcula o percentual de CPU do processo
            if proc_info.pid in self._prev_processes_cpu_times:
                # Se temos dados anteriores deste processo, calculamos o percentual
                prev_times_for_this_proc = self._prev_processes_cpu_times[proc_info.pid]
                proc_info.calculate_and_set_cpu_percent(
                    prev_utime=prev_times_for_this_proc["utime"],
                    prev_stime=prev_times_for_this_proc["stime"],
                    delta_total_system_jiffies=delta_total_system_jiffies,
                    system_hz=current_global_info_snapshot.system_hz,
                    num_cores=current_global_info_snapshot.num_cores,
                )
            else:
                # Se é a primeira vez que vemos este processo, não podemos calcular o delta
                proc_info.cpu_percent = 0.0

            # Calcula o percentual de memória do processo
            proc_info.calculate_and_set_mem_percent(
                system_total_mem_kb=current_global_info_snapshot.mem_total_kb
            )

            # Calcula e formata o horário de início do processo
            proc_info.calculate_and_set_start_time_str(
                system_boot_time_epoch=system_boot_time_epoch,
                system_hz=current_global_info_snapshot.system_hz,
            )

        # --- 5. Atualizar estatísticas globais do sistema ---
        # Atualiza contadores de processos e threads
        current_global_info_snapshot.total_processes = len(current_processes_list)
        current_global_info_snapshot.total_threads = total_threads_count
        # Conta processos no estado "running" (R)
        current_global_info_snapshot.running_processes = sum(
            1 for p in current_processes_list if p.state == "R"
        )

        # Armazena os dados atuais para serem usados como "anteriores" na próxima iteração
        self._prev_global_cpu_times = (
            current_global_info_snapshot.last_cpu_times_jiffies_all
        )
        self._prev_per_core_cpu_times = (
            current_global_info_snapshot.last_cpu_times_jiffies_cores
        )
        self._prev_processes_cpu_times = new_prev_processes_cpu_times

        # --- 6. Atualizar os dados compartilhados (protegidos por lock) ---
        # O lock garante que a View não acesse dados parcialmente atualizados
        with self._data_lock:
            # Copia todos os dados da instância temporária para a instância compartilhada
            self._system_global_info.copy_data_from(current_global_info_snapshot)
            # Atualiza a lista de processos
            self._processes_info_list = current_processes_list

    def _run_update_loop(self) -> None:
        """
        Loop principal da thread de atualização de dados.

        Este método é executado em uma thread separada e gerencia o ciclo de vida das atualizações.
        Realiza a primeira coleta inicial e depois entra em um loop contínuo de coleta,
        respeitando o intervalo de atualização configurado.
        """
        # Primeira coleta para inicializar os dados de comparação
        print("Controller: Primeira coleta de dados...")
        # Executa a primeira coleta para popular os dados de referência (_prev_*)
        self._update_data()
        print("Controller: Primeira coleta concluída.")

        # Loop principal de atualização que continua até que o sinal de parada seja dado
        while not self._running.is_set():
            # Marca o início da atualização para controle de tempo
            start_time: float = time.monotonic()

            try:
                # Coleta e processa os dados do sistema e dos processos
                self._update_data()
            except Exception as e:
                # Tratamento de erros para evitar que a thread morra por exceções não tratadas
                print(f"Erro no loop de atualização do controller: {e}")
                import traceback

                traceback.print_exc()
                # Poderia implementar uma estratégia de retry ou log mais robusto aqui

            # Controle de tempo para garantir o intervalo configurado
            elapsed_time: float = time.monotonic() - start_time
            wait_time: float = self.update_interval_sec - elapsed_time

            # Espera o tempo restante do intervalo, mas permite interrupção
            if wait_time > 0:
                # Usa o evento para esperar, o que permite interromper a espera se necessário
                self._running.wait(timeout=wait_time)

    def start(self) -> None:
        """
        Inicia a thread de monitoramento do sistema.

        Cria e inicia uma nova thread para executar o loop de atualização, se ainda não houver
        uma thread em execução. A thread é configurada como daemon para terminar quando o
        programa principal terminar.
        """
        # Verifica se já existe uma thread em execução
        if self._update_thread is not None and self._update_thread.is_alive():
            print("Controller: Thread de atualização já está em execução.")
            return

        # Inicia uma nova thread
        print("Controller: Iniciando thread de atualização...")
        # Limpa o evento de parada para que o loop possa executar
        self._running.clear()
        # Cria uma nova thread com o método _run_update_loop como alvo
        self._update_thread = threading.Thread(
            target=self._run_update_loop,
            daemon=True,  # Thread daemon termina quando o programa principal termina
        )
        # Inicia a thread
        self._update_thread.start()
        print("Controller: Thread de atualização iniciada.")

    def stop(self) -> None:
        """
        Para a thread de monitoramento do sistema.

        Sinaliza para a thread de atualização parar e aguarda sua conclusão
        por um tempo limite. Limpa a referência à thread após a conclusão.
        """
        print("Controller: Parando thread de atualização...")
        # Sinaliza para a thread parar o loop de atualização
        self._running.set()

        # Se a thread existir e estiver em execução, aguarda a conclusão
        if self._update_thread is not None and self._update_thread.is_alive():
            # Espera a thread terminar com timeout para evitar bloqueio indefinido
            self._update_thread.join(timeout=self.update_interval_sec + 1)

            # Verifica se a thread realmente terminou
            if self._update_thread.is_alive():
                print("Aviso: Thread de atualização não terminou no tempo esperado.")

        print("Controller: Thread de atualização parada.")
        # Limpa a referência à thread
        self._update_thread = None

    # --- Métodos para a View ---

    def get_system_global_info(self) -> SystemGlobalInfo:
        """Retorna uma cópia dos dados globais do sistema."""
        with self._data_lock:
            # Retornar uma cópia para evitar modificações externas e problemas de thread-safety
            # Se SystemGlobalInfo for grande, considerar se uma cópia profunda é necessária
            # ou se o acesso direto (com lock) é aceitável pela View,
            # mas cópia é mais seguro.
            # Para simplificar, retornamos o objeto, mas a View deve tratar como read-only.
            # Idealmente, a View pediria dados específicos, não o objeto inteiro.
            import copy  # Usar copy.copy() ou copy.deepcopy() se necessário

            return copy.deepcopy(self._system_global_info)

    def get_all_processes(self) -> List[ProcessInfo]:
        """Retorna uma cópia da lista de informações de processos."""
        with self._data_lock:
            import copy

            return copy.deepcopy(
                self._processes_info_list
            )  # Cópia profunda da lista e seus itens

    def get_process_by_pid(self, pid: int) -> Optional[ProcessInfo]:
        """Retorna informações de um processo específico por PID."""
        with self._data_lock:
            import copy

            for proc_info in self._processes_info_list:
                if proc_info.pid == pid:
                    return copy.deepcopy(proc_info)
            return None

    def load_and_get_threads_for_process(self, pid: int) -> List[ThreadInfo]:
        """
        Carrega e retorna os detalhes das threads para um processo específico.
        Esta função é destinada a ser chamada pela View quando detalhes de um processo são solicitados.
        """
        # Coleta os detalhes das threads FORA do lock principal para evitar segurá-lo
        # durante operações de I/O potencialmente demoradas.

        collected_threads = system_monitor.get_thread_details_for_process(pid)
        # Agora, precisamos ATUALIZAR o ProcessInfo na lista principal com os dados coletados.
        # Isso requer adquirir o lock novamente.
        with self._data_lock:
            # Encontra o processo na lista
            for i, proc_in_list in enumerate(self._processes_info_list):
                if proc_in_list.pid == pid:
                    # Atualiza o objeto ProcessInfo diretamente na lista
                    self._processes_info_list[i].threads = collected_threads
                    # Atualiza o num_threads se a contagem for diferente
                    if (
                        self._processes_info_list[i].num_threads
                        != len(collected_threads)
                        and collected_threads
                    ):
                        # print(f"Ajustando num_threads para PID {pid} de {self._processes_info_list[i].num_threads} para {len(collected_threads)}")
                        self._processes_info_list[i].num_threads = len(
                            collected_threads
                        )

                    import copy

                    return copy.deepcopy(
                        self._processes_info_list[i].threads
                    )  # Retorna a cópia dos dados atualizados
        return []  # Se o processo desapareceu da lista entre as verificações


# --- Exemplo de Uso (para teste) ---
if __name__ == "__main__":
    print("Iniciando SystemMonitorController para teste...")
    controller = SystemMonitorController(update_interval_sec=2)
    controller.start()

    try:
        while True:
            time.sleep(
                controller.update_interval_sec + 0.5
            )  # Espera um pouco mais que o intervalo

            system_info = controller.get_system_global_info()
            all_procs = controller.get_all_processes()

            print("\n--- Informações Globais do Sistema ---")
            print(
                f"Uso CPU: {system_info.cpu_usage_percent:.2f}% | Ocioso: {system_info.cpu_idle_percent:.2f}%"
            )
            if system_info.individual_cpu_usages:
                for core_idx, usage in enumerate(system_info.individual_cpu_usages):
                    print(f"  Core {core_idx}: {usage:.2f}%")
            print(f"Memória Total: {system_info.mem_total_kb / 1024:.2f} MB")
            print(
                f"Memória Usada: {system_info.mem_used_kb / 1024:.2f} MB ({system_info.mem_used_percent:.2f}%)"
            )
            print(f"Total de Processos: {system_info.total_processes}")
            print(f"Total de Threads: {system_info.total_threads}")
            print(
                f"Uptime: {system_info.uptime_seconds // 3600}h {(system_info.uptime_seconds % 3600) // 60}m"
            )
            print(f"Load Avg: {system_info.load_avg}")

            if all_procs:
                print("\n--- Top 5 Processos por CPU ---")
                # Ordena uma cópia da lista para não modificar a original enquanto iteramos
                sorted_procs = sorted(
                    all_procs, key=lambda p: p.cpu_percent, reverse=True
                )
                a = False
                for proc in sorted_procs[:5]:
                    if not a:
                        a = True
                        proc.threads = controller.load_and_get_threads_for_process(
                            proc.pid
                        )
                    print(
                        f"  PID: {proc.pid:<5} Usuário: {proc.user:<10} CPU%: {proc.cpu_percent:>6.2f}% "
                        f"Mem%: {proc.mem_percent:>5.2f}% MemRSS: {proc.vm_rss_kb / 1024:>6.2f}MB "
                        f"Início: {proc.start_time_str[:30]:<30} Cmd: {proc.cmdline[:30]}"
                    )
                    for thr in proc.threads[:5]:
                        print(
                            f"  TID: {thr.tid:<5} Nome: {thr.name:<10} State: {thr.state}"
                        )
            else:
                print("Nenhum processo encontrado.")

            print("-" * 40)

    except KeyboardInterrupt:
        print("\nInterrompido pelo usuário.")
    finally:
        print("Parando o controller...")
        controller.stop()
        print("Controller parado. Fim do teste.")
