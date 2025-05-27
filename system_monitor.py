# scr/system_monitor.py
"""
Módulo responsável pela coleta de dados do sistema operacional Linux.
Atua como uma camada de abstração para ler e processar informações do sistema de arquivos /proc.
"""

import os
from typing import Dict, List, Tuple, Optional

# Importação dos modelos de dados utilizados pelo monitor
from data_model import (
    ProcessInfo,
    ThreadInfo,
    SystemGlobalInfo,
)

# --- Funções de Coleta de Dados de CPU ---


def get_cpu_times_global() -> List[int]:
    """Lê a primeira linha 'cpu' do /proc/stat e retorna os tempos em jiffies.

    A primeira linha do arquivo representa a soma de todos os cores da CPU.

    Returns:
        List[int]: Lista com os valores de tempo da CPU em jiffies na seguinte ordem:
                  [user, nice, system, idle, iowait, irq, softirq, steal]
                  ou lista vazia em caso de erro.
    """
    try:
        with open("/proc/stat", "r") as f:
            # Lê a primeira linha que contém os dados de CPU agregados
            line = f.readline()
            parts = line.split()

            # Verifica se a linha começa com "cpu" (formato esperado)
            if parts[0] == "cpu":
                # Retorna os primeiros 8 campos numéricos após "cpu"
                # Estes representam: user, nice, system, idle, iowait, irq, softirq, steal
                return [int(p) for p in parts[1:9]]
    except (FileNotFoundError, IndexError, ValueError) as e:
        # Registra erro para ajudar na depuração de problemas
        print(f"Aviso: Erro ao ler /proc/stat para tempos de CPU global: {e}")
        return []  # Retorna lista vazia em caso de erro

    return []  # Retorna lista vazia se o formato não for o esperado


def get_cpu_times_per_core() -> List[List[int]]:
    """Lê as linhas 'cpuX' do /proc/stat e retorna uma lista de tempos para cada core.

    Cada linha cpuX representa os dados de tempo de um núcleo específico de CPU.

    Returns:
        List[List[int]]: Lista de listas, onde cada lista interna contém os tempos
                        de um núcleo de CPU no mesmo formato que get_cpu_times_global().
    """
    core_times_list: List[List[int]] = []

    try:
        with open("/proc/stat", "r") as f:
            for line in f:
                parts = line.split()
                # Identifica linhas que começam com "cpuN" onde N é um número
                if parts and parts[0].startswith("cpu") and parts[0][3:].isdigit():
                    # Coleta os 8 campos de tempo para este core
                    core_times_list.append([int(p) for p in parts[1:9]])
    except (FileNotFoundError, IndexError, ValueError) as e:
        print(f"Aviso: Erro ao ler /proc/stat para tempos de CPU por core: {e}")
        return []  # Retorna lista vazia em caso de erro

    return core_times_list


# --- Funções de Coleta de Dados de Memória ---


def get_mem_info_dict() -> Dict[str, int]:
    """Lê /proc/meminfo e retorna um dicionário com os dados de memória do sistema.

    Este arquivo contém informações detalhadas sobre o uso de memória do sistema,
    incluindo memória total, livre, buffers, cached, swap, etc.

    Returns:
        Dict[str, int]: Dicionário com chaves correspondendo aos nomes dos campos
                        e valores em KB, ou dicionário vazio em caso de erro.
    """
    mem_info: Dict[str, int] = {}

    try:
        with open("/proc/meminfo", "r") as f:
            for line in f:
                # Divide cada linha em nome e valor (formato "MemTotal: 8192 kB")
                parts = line.split(":")
                if len(parts) == 2:
                    key = parts[0].strip()  # Nome do campo (ex: "MemTotal")
                    value_part = parts[1].strip().split()  # Ex: ["8192", "kB"]
                    # Converte o primeiro valor para inteiro se for um número
                    if value_part and value_part[0].isdigit():
                        mem_info[key] = int(value_part[0])
    except FileNotFoundError:
        print("Aviso: /proc/meminfo não encontrado.")
        return {}
    except Exception as e:
        print(f"Aviso: Erro ao ler /proc/meminfo: {e}")
        return {}

    return mem_info


# --- Funções de Coleta de Dados de Uptime e Load ---


def get_uptime() -> float:
    """Lê /proc/uptime e retorna o tempo de funcionamento do sistema em segundos.

    O arquivo /proc/uptime contém dois valores: o uptime total do sistema
    e o tempo que todos os cores de CPU passaram ociosos. Esta função
    retorna apenas o primeiro valor.

    Returns:
        float: Uptime do sistema em segundos ou -1 em caso de erro.
    """
    try:
        with open("/proc/uptime", "r") as f:
            # O arquivo contém dois números: uptime e tempo ocioso acumulado
            parts = f.readline().split()
            # Retorna o primeiro número (uptime)
            return float(parts[0])
    except FileNotFoundError:
        print("Aviso: /proc/uptime não encontrado.")
        return -1.0
    except (IndexError, ValueError, Exception) as e:
        print(f"Aviso: Erro ao ler /proc/uptime: {e}")
        return -1.0


def get_load_average() -> Tuple[float, float, float]:
    """Lê /proc/loadavg e retorna a carga média do sistema.

    O arquivo /proc/loadavg contém cinco valores: as médias de carga em 1, 5 e 15 minutos,
    o número de processos em execução/total e o PID do último processo criado.
    Esta função retorna apenas as três médias de carga.

    Returns:
        Tuple[float, float, float]: Carga média em 1, 5 e 15 minutos respectivamente,
                                    ou (-1, -1, -1) em caso de erro.
    """
    try:
        with open("/proc/loadavg", "r") as f:
            # O formato é "0.00 0.01 0.05 1/109 7389"
            parts = f.readline().split()
            # Retorna os três primeiros valores convertidos para float
            return (float(parts[0]), float(parts[1]), float(parts[2]))
    except FileNotFoundError:
        print("Aviso: /proc/loadavg não encontrado.")
        return (-1.0, -1.0, -1.0)
    except (IndexError, ValueError, Exception) as e:
        print(f"Aviso: Erro ao ler /proc/loadavg: {e}")
        return (-1.0, -1.0, -1.0)


# --- Funções de Coleta de Dados de Processos ---


def get_process_details(pid: int) -> Optional[ProcessInfo]:
    """Coleta detalhes de um processo específico a partir do sistema de arquivos /proc.

    Lê múltiplos arquivos em /proc/[pid]/ para obter informações completas sobre um processo:
    - /proc/[pid]/stat: Status do processo, tempos de CPU, etc.
    - /proc/[pid]/status: Informações detalhadas incluindo uso de memória.
    - /proc/[pid]/cmdline: Linha de comando completa do processo.

    Args:
        pid (int): ID do processo a ser analisado.

    Returns:
        Optional[ProcessInfo]: Objeto ProcessInfo populado com os dados do processo,
                              ou None se o processo não existe ou ocorreu erro.
    """
    # Variáveis para debugging e registro de erros
    line_content_stat: str = ""
    line_content_status: str = ""
    stat_fields_for_log: list = []

    try:
        # Cria a instância para armazenar os dados do processo
        process_info = ProcessInfo(pid)

        # --- 1. Lendo e parseando /proc/[pid]/stat ---
        with open(f"/proc/{pid}/stat", "r") as f_stat:
            line_content_stat = f_stat.read()  # Lê a linha inteira do arquivo

            # O parsing é complexo pois o nome do comando (comm) pode conter parênteses
            try:
                # Localiza os parênteses que delimitam o nome do comando
                first_paren = line_content_stat.index("(")
                last_paren = line_content_stat.rindex(")")
            except ValueError:
                raise ValueError(
                    "Formato de /proc/[pid]/stat inválido, 'comm' não encontrado."
                )

            # Extrai o nome do comando (comm) de dentro dos parênteses
            process_info.comm = line_content_stat[first_paren + 1 : last_paren]

            # O restante dos campos vem após o último parêntese, separados por espaço
            remaining_stat_str = line_content_stat[last_paren + 1 :].strip()
            stat_fields = remaining_stat_str.split()
            stat_fields_for_log = stat_fields  # Para registro em caso de erro

            # Verifica se há campos suficientes conforme a estrutura do arquivo
            if len(stat_fields) < 20:  # Precisa de ao menos 20 campos para starttime
                raise ValueError(
                    f"Campos insuficientes em /proc/{pid}/stat: {len(stat_fields)} encontrados."
                )

            # Extrai e atribui os valores dos campos conforme documentação do /proc/[pid]/stat
            process_info.state = stat_fields[
                0
            ]  # Estado do processo (R=running, S=sleeping, etc.)
            process_info.ppid = int(stat_fields[1])  # PID do processo pai

            # Campos de tempo de CPU em jiffies
            process_info.utime = int(stat_fields[11])  # Tempo de CPU em modo usuário
            process_info.stime = int(stat_fields[12])  # Tempo de CPU em modo kernel

            # Informações de prioridade e agendamento
            process_info.priority = int(stat_fields[15])
            process_info.nice = int(stat_fields[16])  # Valor nice (-20 a +19)

            # Número de threads no processo
            process_info.num_threads = int(stat_fields[17])

            # Tempo de início do processo (em jiffies desde o boot)
            process_info.starttime_jiffies = int(stat_fields[19])

        # --- 2. Lendo e parseando /proc/[pid]/status ---
        uid_val: int = -1  # UID padrão caso não seja encontrado
        with open(f"/proc/{pid}/status", "r") as f_status_file:
            for line_content_status in f_status_file:
                line = line_content_status.strip()
                if not line:  # Pula linhas vazias
                    continue

                # Divide a linha em chave e valor (formato "Chave: Valor")
                parts = line.split(":", 1)
                if len(parts) != 2:
                    continue

                key = parts[0].strip()  # Nome do campo (ex: "Uid", "VmRSS")
                value_str = parts[1].strip()  # Valor como string
                val_parts = value_str.split()  # Divide em tokens (ex: ["1234", "kB"])

                # Extrai o valor numérico dos campos relevantes
                current_field_int_val: int = 0
                if val_parts and val_parts[0].isdigit():
                    try:
                        current_field_int_val = int(val_parts[0])
                    except ValueError:
                        current_field_int_val = 0

                # Processa os diferentes tipos de campos conforme suas chaves
                if key == "Uid":
                    # Extrai o UID real do processo (primeiro valor)
                    if val_parts and val_parts[0].isdigit():
                        try:
                            uid_val = int(val_parts[0])
                            process_info.uid = uid_val
                        except ValueError:
                            pass
                # Campos de memória (todos em KB)
                elif key == "VmPeak":
                    process_info.vm_peak_kb = current_field_int_val
                elif key == "VmSize":
                    process_info.vm_size_kb = current_field_int_val
                elif key == "VmLck":
                    process_info.vm_lck_kb = current_field_int_val
                elif key == "VmPin":
                    process_info.vm_pin_kb = current_field_int_val
                elif key == "VmHWM":
                    process_info.vm_hwm_kb = current_field_int_val
                elif key == "VmRSS":
                    process_info.vm_rss_kb = current_field_int_val
                elif key == "RssAnon":
                    process_info.rss_anon_kb = current_field_int_val
                elif key == "RssFile":
                    process_info.rss_file_kb = current_field_int_val
                elif key == "RssShmem":
                    process_info.rss_shmem_kb = current_field_int_val
                elif key == "VmData":
                    process_info.vm_data_kb = current_field_int_val
                elif key == "VmStk":
                    process_info.vm_stk_kb = current_field_int_val
                elif key == "VmExe":
                    process_info.vm_exe_kb = current_field_int_val
                elif key == "VmLib":
                    process_info.vm_lib_kb = current_field_int_val
                elif key == "VmPTE":
                    process_info.vm_pte_kb = current_field_int_val
                elif key == "VmSwap":
                    process_info.vm_swap_kb = current_field_int_val

        # Obtém o nome de usuário a partir do UID
        process_info.user = get_username_from_uid(uid_val)

        # --- 3. Lendo /proc/[pid]/cmdline ---
        try:
            # Lê como binário já que pode conter bytes nulos (\0)
            with open(f"/proc/{pid}/cmdline", "rb") as f_cmdline:
                cmdline_raw = f_cmdline.read()
                # Substitui bytes nulos por espaços e converte para string
                process_info.cmdline = (
                    cmdline_raw.replace(b"\x00", b" ")
                    .decode("utf-8", "replace")
                    .strip()
                )
                # Se cmdline estiver vazio, usa o 'comm' entre colchetes
                if not process_info.cmdline:
                    process_info.cmdline = f"[{process_info.comm}]"
        except Exception:
            # Fallback em caso de erro
            process_info.cmdline = f"[{process_info.comm}]"

        return process_info

    except FileNotFoundError:
        # O processo pode ter terminado entre a listagem e a leitura
        return None
    except (IndexError, ValueError) as e:
        # Erros de parsing ou acesso a índices inválidos
        problematic_context = ""
        try:
            if (
                line_content_stat
                and isinstance(e, ValueError)
                and "stat" in str(e).lower()
            ):
                problematic_context = f"Contexto do erro em /proc/{pid}/stat, linha: '{line_content_stat.strip()}'"
            elif line_content_status:
                problematic_context = f"Contexto do erro em /proc/{pid}/status, linha: '{line_content_status.strip()}'"
            elif stat_fields_for_log:
                problematic_context = f"Contexto do erro em /proc/{pid}/stat, campos após comm: '{' '.join(stat_fields_for_log[:10])}...'"
        except Exception:
            print(
                f"AVISO: Erro de parsing (IndexError ou ValueError) para PID {pid}: {e}. {problematic_context}"
            )
            pass
        return None
    except Exception as e:
        # Captura outros erros inesperados
        print(f"AVISO: Erro GENÉRICO inesperado ao obter detalhes para PID {pid}: {e}")
        import traceback

        traceback.print_exc()
        return None


def get_thread_details_for_process(process_pid: int) -> List[ThreadInfo]:
    """Coleta informações sobre todas as threads de um processo específico.

    Lê os dados de cada thread no diretório /proc/[pid]/task/[tid]/
    para obter estado e nome de cada thread.

    Args:
        process_pid (int): ID do processo para o qual coletar informações de threads.

    Returns:
        List[ThreadInfo]: Lista de objetos ThreadInfo com informações das threads,
                         ou lista vazia se o processo não existe ou não tem threads.
    """
    threads_list: List[ThreadInfo] = []
    task_path = f"/proc/{process_pid}/task/"

    try:
        # Verifica se o diretório de tasks existe
        if os.path.isdir(task_path):
            # Itera por cada thread (diretório dentro de task/)
            for tid_str in os.listdir(task_path):
                if tid_str.isdigit():
                    try:
                        tid = int(tid_str)
                        # Cria objeto para armazenar informações da thread
                        thread_info = ThreadInfo(tid=tid, process_pid=process_pid)

                        # Obtém o estado da thread a partir de /proc/[pid]/task/[tid]/stat
                        try:
                            with open(
                                f"{task_path}{tid_str}/stat", "r"
                            ) as f_thread_stat:
                                thread_stat_line = f_thread_stat.read()
                                # Extrai o estado (similar ao processo, mas simplificado)
                                t_last_paren = thread_stat_line.rindex(")")
                                t_remaining_stat = thread_stat_line[
                                    t_last_paren + 1 :
                                ].strip()
                                t_stat_fields = t_remaining_stat.split()
                                if t_stat_fields:
                                    thread_info.state = t_stat_fields[0]
                        except FileNotFoundError:
                            thread_info.state = (
                                "Ended?"  # Thread terminou durante a coleta
                            )
                        except ValueError:
                            thread_info.state = "?"  # Erro no formato do arquivo
                        except Exception:
                            thread_info.state = "ErrS"  # Outro erro

                        # Obtém o nome da thread de /proc/[pid]/task/[tid]/comm
                        try:
                            with open(
                                f"{task_path}{tid_str}/comm", "r"
                            ) as f_thread_comm:
                                thread_info.name = f_thread_comm.read().strip()
                        except Exception:
                            # Nome padrão baseado no TID se falhar a leitura
                            thread_info.name = f"tid_{tid}"

                        threads_list.append(thread_info)
                    except ValueError:  # Se tid_str não for um número válido
                        pass

        return threads_list

    except FileNotFoundError:  # Diretório /proc/[pid]/task não existe
        return []
    except Exception:  # Outros erros durante a listagem
        import traceback

        traceback.print_exc()  # Log para depuração
        return []


def get_all_processes_info_list() -> List[ProcessInfo]:
    """Coleta informações de todos os processos em execução no sistema.

    Percorre todos os diretórios numéricos em /proc/ que representam processos
    e obtém detalhes de cada um.

    Returns:
        List[ProcessInfo]: Lista de objetos ProcessInfo com dados dos processos ativos,
                          sem o cálculo de percentual de CPU (feito posteriormente).
    """
    processes_list: List[ProcessInfo] = []

    try:
        # Lista todos os diretórios em /proc/ que são números (PIDs)
        pids = [pid for pid in os.listdir("/proc") if pid.isdigit()]
    except FileNotFoundError:
        print("Aviso: Diretório /proc não encontrado.")
        return []

    # Coleta informações para cada PID encontrado
    for pid_str in pids:
        try:
            pid = int(pid_str)
            # Obtém detalhes completos do processo
            process_info = get_process_details(pid)
            if process_info:
                processes_list.append(process_info)
        except (
            ValueError
        ):  # Se o pid_str não for um número válido (improvável com isdigit())
            continue

    return processes_list


# --- Função Principal para Coleta de Dados do Sistema ---


def populate_system_global_data(system_info_instance: SystemGlobalInfo) -> None:
    """Popula um objeto SystemGlobalInfo com dados atuais do sistema.

    Coleta e armazena informações básicas do sistema, incluindo tempos de CPU,
    uso de memória, uptime e carga média. Não calcula percentuais de CPU nem
    conta processos/threads, o que é feito pelo controller posteriormente.

    Args:
        system_info_instance (SystemGlobalInfo): Instância a ser populada com dados.
    """
    # 1. Coleta os tempos de CPU (global e por core) para cálculos de percentuais
    system_info_instance.last_cpu_times_jiffies_all = get_cpu_times_global()
    system_info_instance.last_cpu_times_jiffies_cores = get_cpu_times_per_core()

    # 2. Coleta e processa informações de memória do sistema
    mem_data = get_mem_info_dict()
    if mem_data:
        # Armazena dados de memória RAM
        system_info_instance.mem_total_kb = mem_data.get("MemTotal", 0)
        system_info_instance.mem_free_kb = mem_data.get("MemFree", 0)
        system_info_instance.mem_available_kb = mem_data.get(
            "MemAvailable", system_info_instance.mem_free_kb
        )  # Fallback para MemFree se MemAvailable não estiver disponível
        system_info_instance.mem_buffers_kb = mem_data.get("Buffers", 0)
        system_info_instance.mem_cached_kb = mem_data.get("Cached", 0)

        # Calcula memória utilizada e percentual
        system_info_instance.mem_used_kb = (
            system_info_instance.mem_total_kb - system_info_instance.mem_available_kb
        )
        # Evita divisão por zero se mem_total_kb for 0
        system_info_instance.mem_used_percent = (
            (system_info_instance.mem_used_kb / system_info_instance.mem_total_kb)
            * 100.0
            if system_info_instance.mem_total_kb
            else 0.0
        )

        # Armazena dados de swap
        system_info_instance.swap_total_kb = mem_data.get("SwapTotal", 0)
        system_info_instance.swap_free_kb = mem_data.get("SwapFree", 0)
        system_info_instance.swap_used_kb = (
            system_info_instance.swap_total_kb - system_info_instance.swap_free_kb
        )
        # Evita divisão por zero se swap_total_kb for 0
        system_info_instance.swap_used_percent = (
            (system_info_instance.swap_used_kb / system_info_instance.swap_total_kb)
            * 100.0
            if system_info_instance.swap_total_kb
            else 0.0
        )
    else:
        # Define valores padrão se não for possível obter dados de memória
        system_info_instance.mem_total_kb = 0
        system_info_instance.mem_free_kb = 0
        system_info_instance.mem_available_kb = 0
        system_info_instance.mem_buffers_kb = 0
        system_info_instance.mem_cached_kb = 0
        system_info_instance.mem_used_kb = 0
        system_info_instance.mem_used_percent = 0.0
        system_info_instance.swap_total_kb = 0
        system_info_instance.swap_free_kb = 0
        system_info_instance.swap_used_kb = 0
        system_info_instance.swap_used_percent = 0.0

    # 3. Coleta uptime e carga média do sistema
    system_info_instance.uptime_seconds = get_uptime()
    system_info_instance.load_avg = get_load_average()


# --- Função Auxiliar para Obter Nome de Usuário ---


def get_username_from_uid(uid: int) -> str:
    """Obtém o nome do usuário a partir do UID lendo /etc/passwd diretamente."""
    try:
        with open("/etc/passwd", "r") as f:
            for line in f:
                parts = line.split(":")
                if len(parts) >= 3 and parts[2].isdigit() and int(parts[2]) == uid:
                    return parts[0]  # Nome do usuário
    except Exception:
        pass
    return str(uid)  # Se não encontrar, retorna o UID como string

