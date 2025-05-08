# Como estamos utilizando modelo MVC, estaremos encapsulando para melhor visualizacao
# aqui vai ser a parte Control, onde vai processar dados e mandar para interface

import threading
import time
from model import LeituraCPU

class ControleDashboard:
    def __init__(self, Interface):
        self.Interface = Interface
        self.CPUtotal_tempoanterior, self.CPUparado_tempoanterior = LeituraCPU()

        self.CPUthread = threading.Thread(target=self.CPUatualizacao_continua)
        self.CPUthread.daemon = True
        self.CPUthread.start()

        self.Processo_Threads_thread = threading.Thread(target=self.Processos_Threads_atualizacao_continua)
        self.Processo_Threads_thread.daemon = True
        self.Processo_Threads_thread.start()

    def CPUatualizacao_continua(self):
        while True:
            tempototal, tempoparado = LeituraCPU()
            diferenca_tempo = tempototal - self.CPUtotal_tempoanterior
            diferenca_parado = tempoparado - self.CPUparado_tempoanterior

            CPU_uso = 100 * (1 - diferenca_parado / diferenca_tempo) if diferenca_tempo > 0 else 0
            
            self.CPUtotal_tempoanterior, self.CPUparado_tempoanterior = tempototal, tempoparado

            self.Interface.Dashboard.after(0, self.Interface.CPU_atualizacao, CPU_uso, 100 - CPU_uso)
            time.sleep(5)

    def Processos_Threads_atualizacao_continua(self):
        while True:
            processos, threads = Quantidade_Processos_Threads()

            self.Interface.Dashboard.after(0, self.Interface.ProcessosThreads_atualizacao, processos, threads)
            time.sleep(5)

