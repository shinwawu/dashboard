# Como estamos utilizando modelo MVC, estaremos encapsulando para melhor visualizacao
# aqui vai ser a parte Model, onde le dados
import os

def LeituraCPU():
    with open("/proc/stat", "r") as cpu:
        linha = cpu.readline()
    cpupartes = list(map(int, linha.split()[1:]))
    tempototal = sum(cpupartes)
    tempoparado = cpupartes[3]
    return tempototal, tempoparado


def Quantidade_Processos_Threads():
    processos = 0
    threads = 0
    for ProcessosID in os.listdir("/proc"):
        if ProcessosID.isdigit():
            processos += 1
            try:
                with open(f"/proc/{ProcessosID}/status") as Process:
                    for linha in Process:
                        if linha.startswith("Threads:"):
                            threads += int(linha.split()[1])
                            break
            except:
                continue
    return processos, threads
