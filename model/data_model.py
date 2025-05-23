import time


class ThreadInfo:
    """Classe para armazenar informações sobre uma thread específica de um processo."""

    def __init__(self, tid: int, process_pid: int) -> None:
        """Inicializa um objeto ThreadInfo com identificadores básicos.

        Args:
            tid (int): ID da thread.
            process_pid (int): ID do processo ao qual a thread pertence.
        """
        self.tid: int = tid  # ID da thread (Thread ID)
        self.pid: int = process_pid  # PID do processo pai
        self.state: str = (
            "N/A"  # Estado da thread (R=running, S=sleeping, D=disk sleep, etc.)
        )
        self.name: str = ""  # Nome da thread (obtido de /proc/[pid]/task/[tid]/comm)

    def __repr__(self) -> str:
        """Retorna uma representação em string do objeto ThreadInfo.

        Returns:
            str: Representação formatada da thread.
        """
        return f"<ThreadInfo TID:{self.tid} Name:'{self.name}' State:'{self.state}'>"


class ProcessInfo:
    """Classe para armazenar e processar informações detalhadas sobre um processo do sistema."""

    def __init__(self, pid: int) -> None:
        """Inicializa um objeto ProcessInfo com valores padrão.

        Args:
            pid (int): ID do processo.
        """
        self.pid: int = int(pid)  # Garantir que pid seja int
        self.comm: str = ""  # Nome do comando (extraído de /proc/[pid]/stat)
        self.cmdline: str = ""  # Linha de comando completa (de /proc/[pid]/cmdline)
        self.state: str = (
            ""  # Estado do processo (R=running, S=sleeping, D=disk sleep, etc.)
        )
        self.ppid: int = 0  # PID do processo pai
        self.user: str = ""  # Nome do usuário dono do processo
        self.uid: int = -1  # ID do usuário dono do processo
        self.utime: int = 0  # Tempo em modo usuário (em jiffies)
        self.stime: int = 0  # Tempo em modo kernel (em jiffies)
        self.priority: int = 0  # Prioridade do processo
        self.nice: int = 0  # Valor nice do processo (-20 a 19)
        self.num_threads: int = 0  # Número de threads no processo
        self.starttime_jiffies: int = (
            0  # Tempo de início do processo (jiffies desde boot)
        )
        self.threads: list[ThreadInfo] = []  # Lista de threads deste processo

        # Métricas calculadas dinamicamente
        self.cpu_percent: float = 0.0  # Percentual de uso de CPU
        self.mem_percent: float = 0.0  # Percentual de uso de memória

        # Detalhes de Memória (em KB)
        self.vm_peak_kb: int = 0  # Pico de memória virtual utilizada
        self.vm_size_kb: int = 0  # Tamanho atual da memória virtual
        self.vm_lck_kb: int = 0  # Memória bloqueada (não pode ser swapped)
        self.vm_pin_kb: int = 0  # Memória pinada
        self.vm_hwm_kb: int = 0  # Pico de RSS (high water mark)
        self.vm_rss_kb: int = 0  # Resident Set Size (memória física utilizada)
        self.rss_anon_kb: int = 0  # Parte anônima do RSS
        self.rss_file_kb: int = 0  # Parte mapeada em arquivo do RSS
        self.rss_shmem_kb: int = 0  # Parte compartilhada do RSS
        self.vm_data_kb: int = 0  # Tamanho do segmento de dados
        self.vm_stk_kb: int = 0  # Tamanho da pilha
        self.vm_exe_kb: int = 0  # Tamanho do segmento de código
        self.vm_lib_kb: int = 0  # Tamanho das bibliotecas compartilhadas
        self.vm_pte_kb: int = 0  # Tamanho das tabelas de página
        self.vm_swap_kb: int = 0  # Memória do processo em swap

        self.start_time_str: str = "N/A"  # Tempo de início formatado como string

    def __repr__(self) -> str:
        """Retorna uma representação em string do objeto ProcessInfo.

        Returns:
            str: Representação resumida do processo.
        """
        return f"<ProcessInfo PID:{self.pid} Comm:'{self.comm}' User:'{self.user}' CPU%:{self.cpu_percent:.2f}>"

    def calculate_and_set_mem_percent(self, system_total_mem_kb: int) -> None:
        """Calcula e salva o percentual de memória usado pelo processo.
        O percentual é calculado em relação à memória total do sistema.

        Args:
            system_total_mem_kb (int): Memória total do sistema em KB.
        """
        # Verifica se os valores são válidos antes de calcular
        if system_total_mem_kb > 0 and self.vm_rss_kb is not None:
            # Cálculo do percentual: (memória usada / memória total) * 100
            self.mem_percent = (
                float(self.vm_rss_kb) / float(system_total_mem_kb)
            ) * 100.0
        else:
            # Define 0% se não for possível calcular
            self.mem_percent = 0.0

    def calculate_and_set_cpu_percent(
        self,
        prev_utime: int,
        prev_stime: int,
        delta_total_system_jiffies: int,
        system_hz: int,
        num_cores: int,
    ) -> None:
        """Calcula e salva o percentual de CPU usado pelo processo.
        O percentual é calculado em relação ao tempo total de CPU do sistema,
        normalizado pelo número de cores disponíveis para refletir o uso por core.

        Args:
            prev_utime (int): Tempo anterior em modo usuário (em jiffies).
            prev_stime (int): Tempo anterior em modo kernel (em jiffies).
            delta_total_system_jiffies (int): Delta total de jiffies do sistema entre medições.
            system_hz (int): Frequência do sistema em jiffies por segundo.
            num_cores (int): Número de núcleos de CPU disponíveis.

        Returns:
            None: O resultado é armazenado no atributo cpu_percent.
        """
        # Verificação inicial: evita divisões por zero ou cálculos com valores inválidos
        if delta_total_system_jiffies <= 0 or system_hz <= 0:
            self.cpu_percent = 0.0
            return

        # Obtém os valores atuais de tempo de CPU do processo
        current_utime: int = self.utime
        current_stime: int = self.stime

        # Calcula o delta de jiffies do processo entre duas medições
        delta_proc_jiffies: int = (current_utime - prev_utime) + (
            current_stime - prev_stime
        )

        # Verifica valores negativos que podem ocorrer se o processo for reiniciado
        # ou se houver alguma inconsistência na leitura dos contadores
        if delta_proc_jiffies < 0:
            self.cpu_percent = 0.0
            return

        # EXPLICAÇÃO DETALHADA DO CÁLCULO DE %CPU:
        # -------------------------------------------
        # O uso de CPU é calculado com base no delta de tempo que um processo usou a CPU em relação
        # ao tempo total disponível no sistema durante o intervalo de medição.
        #
        # Em um sistema com múltiplos cores, há duas formas de interpretar o uso de CPU:
        #
        # 1. Como porcentagem do tempo total de CPU disponível no sistema:
        #    - Se um processo usa 1 core inteiro em um sistema com 4 cores, ele estaria usando 25%
        #    - Cálculo: (delta_proc_jiffies / delta_total_system_jiffies) * 100
        #
        # 2. Como porcentagem relativa a um único core (padrão usado pelo 'top' e similar):
        #    - Se um processo usa 1 core inteiro, mostra 100% (independente do número de cores no sistema)
        #    - Se um processo usa 2 cores inteiros em um sistema de 4 cores, mostra 200%
        #    - Cálculo: ((delta_proc_jiffies / delta_total_system_jiffies) * 100) * num_cores
        #
        # Este código adota a segunda abordagem para ser compatível com ferramentas como 'top'.
        #
        # O delta_total_system_jiffies representa a soma dos jiffies de todos os cores no período.
        # Para calcular o percentual relativo a um único core, normalizamos dividindo por num_cores.
        #
        # Assim:
        #   %CPU = (delta_proc_jiffies / (delta_total_system_jiffies / num_cores)) * 100
        #   %CPU = (delta_proc_jiffies * num_cores / delta_total_system_jiffies) * 100
        #
        # Este valor pode variar de 0% a (100 * num_cores)%

        # Cálculo do percentual de CPU utilizado pelo processo
        if delta_total_system_jiffies > 0:
            # Normaliza o uso por núcleo para que 100% signifique uso completo de um núcleo
            proc_cpu_usage_percent: float = (
                delta_proc_jiffies * num_cores * 100.0
            ) / delta_total_system_jiffies
        else:
            proc_cpu_usage_percent = 0.0

        # Garante que o valor esteja entre 0% e (100% * número de cores)
        # Ex: Em um sistema com 4 cores, limita a 400%
        self.cpu_percent = max(0.0, min(proc_cpu_usage_percent, 100.0 * num_cores))

    def calculate_and_set_start_time_str(
        self, system_boot_time_epoch: float, system_hz: int
    ):
        """Calcula e salva a string de tempo de início do processo.
        O tempo de início é calculado a partir do tempo de boot do sistema e do valor de jiffies
        do processo.

        Args:
            system_boot_time_epoch (float): Tempo de boot do sistema em segundos desde a época Unix.
            system_hz (int): Frequência do sistema em jiffies por segundo.
        """
        if (
            self.starttime_jiffies is None
            or system_hz <= 0
            or system_boot_time_epoch < 0
        ):
            self.start_time_str = "N/A (Sys Data)"
            return
        try:
            starttime_seconds_since_boot = float(self.starttime_jiffies) / float(
                system_hz
            )

            # Pequena correção para starttime_seconds_since_boot se for negativo ou maior que o uptime
            # (pode acontecer para processos kernel ou devido a arredondamentos/timing)
            if starttime_seconds_since_boot < 0:
                starttime_seconds_since_boot = 0.0
            # Não é estritamente necessário limitar a system_uptime_seconds,
            # mas pode evitar tempos de início "no futuro" se houver grande imprecisão.
            # if starttime_seconds_since_boot > system_uptime_seconds:
            #    starttime_seconds_since_boot = system_uptime_seconds

            process_start_time_epoch = (
                system_boot_time_epoch + starttime_seconds_since_boot
            )

            # Formata para string. Ex: "2023-10-27 10:30:55"
            # Verifica se o timestamp é válido para time.localtime
            # Alguns sistemas podem ter limites para timestamps muito antigos ou futuros.
            # Um teste simples é verificar se é positivo.
            if process_start_time_epoch > 0:
                self.start_time_str = time.strftime(
                    "%Y-%m-%d %H:%M:%S",
                    time.localtime(process_start_time_epoch),
                )
            else:
                # Isso pode acontecer se starttime_jiffies for muito pequeno (processos kernel iniciados no boot)
                # e o cálculo resultar em um tempo de boot ligeiramente "depois" do início do processo.
                # Ou se starttime_jiffies for 0.
                # Para processos muito antigos (ex: init), starttime_jiffies pode ser 1 ou 2.
                # starttime_seconds_since_boot será próximo de 0.
                # process_start_time_epoch será muito próximo de system_boot_time_epoch.
                # Se system_boot_time_epoch for válido, isso deve funcionar.
                # Se resultar em negativo, time.localtime pode falhar.
                self.start_time_str = (
                    "Boot time"  # Ou uma indicação de que iniciou no boot
                )
        except OverflowError:
            self.start_time_str = "Error (Overflow)"
        except (
            ValueError
        ):  # Ex: se system_boot_time_epoch for negativo e o resultado também
            self.start_time_str = "Error (TimeValue)"
        except Exception:
            self.start_time_str = "N/A (Calc Error)"


class SystemGlobalInfo:
    """Classe para armazenar e processar informações globais do sistema operacional."""

    def __init__(self) -> None:
        """Inicializa um objeto SystemGlobalInfo com valores padrão."""
        # Métricas de CPU
        self.cpu_usage_percent: float = 0.0  # Percentual de uso da CPU (todas as cores)
        self.cpu_idle_percent: float = 0.0  # Percentual de tempo ocioso da CPU
        self.individual_cpu_usages: list[float] = []  # Lista de % de uso para cada core
        self.last_cpu_times_jiffies_all: list[
            int
        ] = []  # Tempos de CPU global (da linha 'cpu' do /proc/stat)
        self.last_cpu_times_jiffies_cores: list[
            list[int]
        ] = []  # Tempos para cada core ('cpu0', 'cpu1', etc.)

        # Métricas de memória (valores em KB)
        self.mem_total_kb: int = 0  # Memória RAM física total
        self.mem_free_kb: int = (
            0  # Memória RAM livre (conforme relatado pelo 'MemFree')
        )
        self.mem_available_kb: int = (
            0  # Memória RAM disponível (considerando cache/buffer)
        )
        self.mem_buffers_kb: int = 0  # Memória usada para buffers do kernel
        self.mem_cached_kb: int = 0  # Memória usada para cache do sistema de arquivos
        self.mem_used_kb: int = 0  # Memória RAM em uso (calculada: total - available)
        self.mem_used_percent: float = 0.0  # Percentual de memória em uso

        # Métricas de swap (valores em KB)
        self.swap_total_kb: int = 0  # Espaço total de swap
        self.swap_free_kb: int = 0  # Espaço livre de swap
        self.swap_used_kb: int = 0  # Espaço de swap em uso
        self.swap_used_percent: float = 0.0  # Percentual de swap em uso

        # Contadores de processos e threads
        self.total_processes: int = 0  # Número total de processos no sistema
        self.total_threads: int = 0  # Número total de threads no sistema
        self.running_processes: int = 0  # Número de processos no estado 'running' (R)

        # Configurações do sistema
        # Obtém o valor de HZ (clock ticks por segundo) do sistema
        with open("/proc/self/stat", "r") as f:
            campos = f.read().split()
            t1 = int(campos[13]) + int(campos[14])

        time.sleep(1)

        with open("/proc/self/stat", "r") as f:
            campos = f.read().split()
            t2 = int(campos[13]) + int(campos[14])

        self.system_hz = round(t2 - t1)

        # Outras informações do sistema
        self.uptime_seconds: float = (
            0.0  # Tempo de funcionamento do sistema em segundos
        )
        self.load_avg: tuple[float, float, float] = (
            0.0,
            0.0,
            0.0,
        )  # Carga média (1, 5, 15 min)

        # Número de cores de CPU disponíveis
        with open("/proc/cpuinfo") as f:
            self.num_cores = sum(1 for line in f if line.startswith("processor"))
        

    def __repr__(self) -> str:
        """Retorna uma representação em string do objeto SystemGlobalInfo.

        Returns:
            str: Representação formatada com estatísticas principais do sistema.
        """
        return (
            f"<SystemGlobalInfo CPU:{self.cpu_usage_percent:.2f}% "
            f"Mem:{self.mem_used_percent:.2f}% Procs:{self.total_processes}>"
        )

    @staticmethod
    def _calculate_cpu_percent(
        cpu_times_curr: list[int],
        cpu_times_prev: list[int],
    ) -> tuple[float, float]:
        """Calcula o percentual de uso da CPU e o percentual de tempo ocioso.
        Os percentuais são calculados a partir das diferenças entre as medições atuais e anteriores.

        Args:
            cpu_times_curr (list[int]): Lista de tempos de CPU atuais.
                Formato esperado: [user, nice, system, idle, iowait, irq, softirq, steal]
            cpu_times_prev (list[int]): Lista de tempos de CPU anteriores no mesmo formato.

        Returns:
            tuple[float, float]: Tupla contendo (percentual_uso, percentual_ocioso).
        """
        # Verifica se há dados suficientes para realizar o cálculo
        if (
            not cpu_times_prev
            or not cpu_times_curr
            or len(cpu_times_prev) < 4
            or len(cpu_times_curr) < 4  # Precisa pelo menos user, nice, system, idle
        ):
            return 0.0, 0.0

        # Soma os campos principais de tempo de CPU
        prev_total: int = sum(
            cpu_times_prev[: len(cpu_times_curr)]
        )  # Garante compatibilidade dos tamanhos
        prev_idle: int = cpu_times_prev[3]  # idle é o 4º campo (índice 3)

        curr_total: int = sum(cpu_times_curr)
        curr_idle: int = cpu_times_curr[3]

        # Calcula as diferenças entre medições
        delta_total: int = curr_total - prev_total
        delta_idle: int = curr_idle - prev_idle

        # Calcula os percentuais de uso e ociosidade
        if delta_total <= 0:  # Previne divisão por zero ou valores negativos
            cpu_usage_percent: float = 0.0
            # Se o total não mudou mas o idle sim, define idle conforme a direção da mudança
            cpu_idle_percent: float = (
                100.0 if (delta_total == 0 and delta_idle >= 0) else 0.0
            )
        else:
            # Fórmulas padrão para cálculo de %CPU e %idle
            cpu_usage_percent = (1.0 - (delta_idle / delta_total)) * 100.0
            cpu_idle_percent = (delta_idle / delta_total) * 100.0

        # Garante que os percentuais estão no intervalo válido de 0-100%
        cpu_usage_percent = max(0.0, min(100.0, cpu_usage_percent))
        cpu_idle_percent = max(0.0, min(100.0, cpu_idle_percent))

        return cpu_usage_percent, cpu_idle_percent

    def copy_data_from(self, other: "SystemGlobalInfo") -> None:
        """Copia todos os dados de outro objeto SystemGlobalInfo para este.
        Usado para atualizar a instância principal com dados de uma cópia temporária.

        Args:
            other (SystemGlobalInfo): Objeto fonte dos dados a serem copiados.
        """
        # Copia os dados de CPU com clones seguros (copy) das listas
        self.cpu_usage_percent = other.cpu_usage_percent
        self.cpu_idle_percent = other.cpu_idle_percent
        self.individual_cpu_usages = other.individual_cpu_usages.copy()
        self.last_cpu_times_jiffies_all = other.last_cpu_times_jiffies_all.copy()
        self.last_cpu_times_jiffies_cores = other.last_cpu_times_jiffies_cores.copy()

        # Copia os dados de memória
        self.mem_total_kb = other.mem_total_kb
        self.mem_free_kb = other.mem_free_kb
        self.mem_available_kb = other.mem_available_kb
        self.mem_buffers_kb = other.mem_buffers_kb
        self.mem_cached_kb = other.mem_cached_kb
        self.mem_used_kb = other.mem_used_kb
        self.mem_used_percent = other.mem_used_percent

        # Copia os dados de swap
        self.swap_total_kb = other.swap_total_kb
        self.swap_free_kb = other.swap_free_kb
        self.swap_used_kb = other.swap_used_kb
        self.swap_used_percent = other.swap_used_percent

        # Copia os contadores de processos e threads
        self.total_processes = other.total_processes
        self.total_threads = other.total_threads
        self.running_processes = other.running_processes

        # Copia outras informações do sistema
        self.uptime_seconds = other.uptime_seconds
        self.load_avg = other.load_avg

    def calculate_and_set_per_core_cpu_usages(
        self, prev_per_core_cpu_times: list[list[int]]
    ) -> None:
        """Calcula e armazena o percentual de uso para cada núcleo de CPU.

        Compara os tempos de CPU atuais com os anteriores para cada núcleo
        e calcula o percentual de uso para cada um.

        Args:
            prev_per_core_cpu_times (list[list[int]]): Lista de listas de tempos anteriores por núcleo.
                Cada lista interna contém tempos no formato [user, nice, system, idle, ...].
        """
        # Reinicia a lista de uso por core
        self.individual_cpu_usages = []

        # Verifica se a quantidade de cores corresponde entre as medições
        if (
            len(prev_per_core_cpu_times) == self.num_cores
            and len(self.last_cpu_times_jiffies_cores) == self.num_cores
        ):
            # Calcula o uso de CPU para cada núcleo
            for i in range(self.num_cores):
                usage, _ = self._calculate_cpu_percent(
                    cpu_times_curr=self.last_cpu_times_jiffies_cores[i],
                    cpu_times_prev=prev_per_core_cpu_times[i],
                )
                self.individual_cpu_usages.append(usage)
        else:
            # Se houver discrepância na quantidade de cores, inicializa com zeros
            self.individual_cpu_usages = [0.0] * self.num_cores
            # Registra aviso se houver dados anteriores mas não correspondem
            if len(prev_per_core_cpu_times) != 0:
                print(
                    f"Aviso: Número de núcleos não corresponde entre cpu_times_prev e cpu_times_curr. "
                    f"Prev: {len(prev_per_core_cpu_times)}, Curr: {len(self.last_cpu_times_jiffies_cores)}"
                    f" (Esperado: {self.num_cores})"
                )

    def calculate_and_set_cpu_percent(self, prev_cpu_times: list[int]) -> None:
        """Calcula e armazena o percentual de uso total da CPU do sistema.

        Usa a diferença entre tempos de CPU atuais e anteriores para calcular
        tanto o percentual de uso quanto o percentual de tempo ocioso.

        Args:
            prev_cpu_times (list[int]): Lista de tempos de CPU anteriores.
                Formato: [user, nice, system, idle, iowait, irq, softirq, steal]
        """
        # Calcula os percentuais de uso e ociosidade
        usage, idle = self._calculate_cpu_percent(
            cpu_times_curr=self.last_cpu_times_jiffies_all,
            cpu_times_prev=prev_cpu_times,
        )

        # Armazena os resultados nos atributos da instância
        self.cpu_usage_percent = usage
        self.cpu_idle_percent = idle
