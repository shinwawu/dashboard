# Como estamos utilizando modelo MVC, estaremos encapsulando para melhor visualizacao
# aqui vai ser a parte Model, onde le dados


def LeituraCPU():
    with open("/proc/stat", "r") as f:
        linha = f.readline()
    cpupartes = list(map(int, linha.split()[1:]))
    tempototal = sum(cpupartes)
    tempoparado = cpupartes[3]
    return tempototal, tempoparado



