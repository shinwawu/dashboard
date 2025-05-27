# Dashboard de Sistemas Operacionais - Linux

Este projeto é um dashboard para monitoramento de um sistema operacional Linux, desenvolvido para a disciplina de Sistemas Operacionais.

## Funcionalidades (Projeto A)

- Monitoramento global de CPU e memória.
- Listagem de processos com detalhes (PID, usuário, CPU%, Mem%, estado, etc.).
- Detalhes de uso de memória por processo.
- Informações sobre threads de cada processo.
### Requisitos
* Python3.
* Make.
* Tkinter(usar `make install` para baixar).
## Como executar diretamente (exemplo)
```bash
python3 scr/View.py
```
## Como executar pelo Make (exemplo)
```bash
make install
make run
```
## Introdução

## Funcionalidades Implementadas (Escopo do Projeto A)

O dashboard atualmente implementa as seguintes funcionalidades de monitoramento para o sistema Linux:

**1. Monitoramento Global do Sistema:**
*   **CPU:**
    *   Percentual de uso total da CPU.
    *   Percentual de tempo ocioso total da CPU.
    *   Percentual de uso individual para cada núcleo do processador (quando aplicável).
*   **Memória:**
    *   Quantidade total de memória física (RAM) em KB.
    *   Quantidade de memória livre e disponível em KB.
    *   Quantidade de memória usada (buffers, cache, etc.) em KB.
    *   Percentual de uso da memória física.
    *   Quantidade total, livre, usada e percentual de uso da memória de swap (quando configurada).
*   **Processos e Threads:**
    *   Número total de processos em execução.
    *   Número total de threads no sistema.
    *   Número de processos em estado "Running" (R).
*   **Informações Adicionais do Sistema:**
    *   Tempo de atividade do sistema (Uptime).
    *   Médias de carga do sistema (Load Average para 1, 5 e 15 minutos).
    *   Número de núcleos do processador.
    *   Frequência do clock do sistema (HZ).

**2. Monitoramento de Processos:**
*   **Listagem de Processos:**
    *   Exibição de uma lista de todos os processos ativos no sistema.
*   **Detalhes por Processo:** Para cada processo na lista, ela possui as seguintes informações:
    *   **PID:** Identificador do Processo.
    *   **Comm:** Nome do comando/programa.
    *   **User:** Nome do usuário proprietário do processo.
    *   **State:** Estado atual do processo (ex: R, S, D, Z, T).
    *   **PPID:** PID do processo pai.
    *   **Priority & Nice:** Valores de prioridade e "nice".
    *   **%CPU:** Percentual de uso da CPU pelo processo.
    *   **%Memory:** Percentual de uso da memória física (RAM) pelo processo (baseado no RSS).
    *   **VM RSS:** Resident Set Size - quantidade de memória física (RAM) usada pelo processo (em KB).
    *   **Start Time:** Data e hora de início do processo.
    *   **Cmdline:** Linha de comando completa usada para iniciar o processo.
    *   **Num Threads:** Número de threads pertencentes ao processo.
*   **Detalhes Adicionais de Memória por Processo (coletados, prontos para visualização detalhada):**
    *   Pico de memória virtual (VmPeak), Tamanho total da memória virtual (VmSize).
    *   Memória bloqueada (VmLck), Memória "pinned" (VmPin).
    *   Pico do RSS (VmHWM).
    *   RSS de páginas anônimas (RssAnon), mapeadas em arquivo (RssFile) e compartilhada (RssShmem).
    *   Tamanho do segmento de dados (VmData), pilha (VmStk), código executável (VmExe) e bibliotecas (VmLib).
    *   Tamanho das Page Table Entries (VmPTE) e memória em swap pelo processo (VmSwap).

**3. Monitoramento de Threads (por Processo):**
*   Para um processo selecionado, é possível visualizar uma lista de suas threads.
*   **Detalhes por Thread:**
    *   **TID:** Identificador da Thread.
    *   **Name:** Nome da thread (conforme registrado pelo kernel).
    *   **State:** Estado atual da thread.

**4. Características Gerais da Aplicação:**
*   **Atualização Periódica:** Os dados do dashboard são atualizados automaticamente em intervalos regulares.
*   **Coleta de Dados via `/proc`:** Todas as informações são obtidas diretamente do sistema de arquivos `/proc`, sem o uso de comandos de shell externos.
*   **Processamento de Dados:** As informações brutas são processadas para exibição de métricas compreensíveis.
*   **Interface Multitarefa:** A coleta e atualização de dados ocorrem em uma thread separada para não bloquear a interface do usuário.

## Arquitetura e Design

O dashboard foi desenvolvido utilizando a linguagem de programação Python (versão 3.11.2) e adota o padrão de arquitetura Model-View-Controller (MVC) para organizar seus componentes e responsabilidades. A seguir, detalhamos cada parte da arquitetura:

### 1. Model (Modelo de Dados e Lógica de Coleta)

O Model é responsável por representar os dados do sistema e por obter essas informações diretamente do sistema operacional. Ele é composto por dois arquivos principais:

*   **`scr/model/data_model.py`:**
    *   Define as estruturas de dados (classes) que armazenam as informações coletadas. As classes principais são:
        *   `SystemGlobalInfo`: Contém métricas globais do sistema (CPU, memória, contagem de processos/threads, uptime, load average, HZ, número de cores).
        *   `ProcessInfo`: Armazena informações detalhadas sobre cada processo individual (PID, nome, usuário, estado, %CPU, %Memória, RSS, tempos de CPU, informações de memória virtual, etc.).
        *   `ThreadInfo`: Guarda detalhes sobre cada thread de um processo (TID, nome, estado).
    *   Essas classes também incluem métodos para calcular atributos derivados (como percentuais de uso de CPU e memória, e formatação da hora de início do processo) a partir dos dados brutos.

*   **`scr/system_monitor.py`:**
    *   Contém as funções de baixo nível responsáveis por interagir diretamente com o sistema de arquivos `/proc` do Linux para coletar os dados brutos.
    *   Implementa a lógica para ler e parsear arquivos como `/proc/stat`, `/proc/meminfo`, `/proc/[pid]/stat`, `/proc/[pid]/status`, `/proc/[pid]/cmdline`, e os diretórios `/proc/[pid]/task/`.
    *   Fornece funções para obter informações sobre o nome de usuário a partir do UID.
    *   Este módulo foca exclusivamente na coleta de dados crus, deixando o processamento e os cálculos mais elaborados para as classes do `data_model.py` ou para o `controller.py`.

### 2. View (Interface com o Usuário)

O View é responsável por apresentar graficamente as informações do sistemas  para o usuário.
*   **`scr/View.py`:**
    *   Este arquivo contém a classe InterfaceDashboard, que constrói toda a interface gráfica do sistema.
    *   Utiliza a biblioteca Tkinter de Python para criar gráficos e tabelas.
    *   Atualiza a interface com as informações obtidas ao longo dos intervalos.
      
### Interface

A interface gráfica é implementada utilizando Tkinter (biblioteca do Python), e organizada usando frames, gráficos, tabelas e listas interativas para exibir dados de uso de CPU, memória, processos e threads.

### Estrutura da Interface
A interface é dividida em duas abas principais:

* Visão Geral — Exibe gráficos de uso da CPU, memória, processos, threads e estatísticas agregadas.
* Processos — Exibe uma lista detalhada de todos os processos ativos, com opção de visualizar detalhes de memória e threads.

### Graficos

Os gráficos são gerados com Canvas e atualizados dinamicamente a cada ciclo (5 segundos). Os dados são obtidos via SystemMonitorController, que coleta de `/proc`.

* Uso da CPU (%): gráfico de linha que o uso da CPU nos últimos segundos. As informações são obtidas pelo Controller, utilizando a fonte de dados `/proc/stat`.
* Uso da Memória (%): gráfico de linha que indica a quantidade de RAM utilizada. As informações são obtidas pelo Controller, utilizando a fonte de dados `/proc/meminfo`.
* Total de Processos: gráfico de linha com a quantidade de processos nos últimos segundos. As informações são obtidas pelo Controller, utilizando a fonte de dados `/proc/`.
* Total de Threads: gráfico de linha com a contagem de threads do sistema nos últimos segundos. As informações são obtidas pelo Controller, utilizando a fonte de dados `/proc/[PID]/stat`. 
* Gráfico de Barras de Memória: representa a quantidade de memória total vs usada de forma vertical. As informações são obtidas ao realizar o cálculo de Memória Total - Memória Usada.

### Tabela de Estatística

* A tabela utiliza uma Treeview que apresenta estatísticas como menor, maior, médio e valor atual dos gráficos.
* Os dados são organizados em colunas para facilitar a leitura e comparação.
* Essas estatísticas são calculadas em tempo real para cada métrica (CPU, memória, processos, threads).
  
### Lista de Processos

Na aba "Processos", é exibida uma tabela dinâmica, ordenada pelo uso de CPU,  com os seguintes campos:

* PID : ID do processo. As informações são obtidas pelo Controller, utilizando a fonte de dados `/proc/[PID]/stat	`.
* User : Usuário que iniciou o processo. As informações são obtidas pelo Controller, utilizando a fonte de dados `/etc/passwd + UID`.
* CPU : Utilização da CPU pelo processo. As informações são obtidas pelo Controller, utilizando a fonte de dados `ProcessInfo`.
* Mem : Utilização da Memória pelo processo. As informações são obtidas pelo Controller, utilizando a fonte de dados `/proc/[PID]/status`.
* Cmd : Comando que iniciou o processo. As informações são obtidas pelo Controller, utilizando a fonte de dados `/proc/[PID]/cmdline`.

  Os processos são ordenados dinamicamente por uso de CPU.


### Detalhamento de Processo

Ao selecionar um processo na lista e clicar em "Ver Detalhes do Processo", uma nova janela é aberta com:

* Informações básicas: usuário, CPU, memória, horário de início, comando.
* Informações de memória detalhadas: VmSize, VmRSS, VmExe, VmData, VmStk, VmLib, VmSwap.
* Lista de threads do processo com TID, nome e estado (R, S, Z, etc.).
* As informações são obtidas pelo `/proc/[PID]/status` , `/proc/[PID]/cmdline`, `/proc/[PID]/task/[TID]/stat` e `/comm`



### Atualização Periódica

* A interface usa o método atualizacao_interface() para atualizar os gráficos e tabelas a cada intervalo definido (o valor utilizado é, 5 segundos).
* Esse método coleta dados pela SystemMonitorController, que se comunica com o backend.


### 3. Controller (Controlador)

O Controller atua como o intermediário entre o Model e a View, orquestrando o fluxo de dados e a lógica da aplicação.

*   **`scr/controller.py`:**
    *   Gerencia a atualização periódica dos dados do sistema. Utiliza uma `threading.Thread` para executar a coleta e o processamento de dados em segundo plano, garantindo que a interface do usuário (View) não seja bloqueada.
    *   Mantém o estado atual das informações globais do sistema e da lista de processos.
    *   Armazena os dados da leitura anterior (ex: tempos de CPU) para permitir o cálculo de deltas e métricas que variam com o tempo (como o percentual de uso da CPU).
    *   Invoca as funções de coleta de dados do `system_monitor.py` e os métodos de cálculo das classes do `data_model.py`.
    *   Utiliza `threading.Lock` para garantir o acesso seguro (thread-safe) aos dados compartilhados que são lidos pela View e escritos pela thread de atualização.
    *   Fornece métodos para a View obter os dados processados (informações globais, lista de processos, detalhes de um processo específico, threads de um processo).

### Fluxo de Dados e Atualização

1.  O `SystemMonitorController` inicia uma thread dedicada à atualização de dados.
2.  Em intervalos regulares, esta thread:
    a.  Chama funções em `system_monitor.py` para coletar dados brutos do `/proc` e popular instâncias temporárias de `SystemGlobalInfo` e `ProcessInfo`.
    b.  Invoca métodos de cálculo nessas instâncias (definidos em `data_model.py`) para processar os dados brutos (ex: calcular %CPU, %Memória).
    c.  Atualiza as instâncias principais de dados (protegidas por lock) que são mantidas pelo Controller.
3.  A View solicita dados ao Controller através de seus métodos públicos. O Controller, por sua vez, fornece cópias dos dados atuais, garantindo que a View sempre acesse um estado consistente e seguro.

## Coleta de Dados (Interação com o Sistema de Arquivos `/proc`)

A obtenção de todas as métricas de sistema e de processos é realizada através da leitura e interpretação de arquivos virtuais localizados no sistema de arquivos `/proc`. Este método permite o acesso direto a informações mantidas pelo kernel Linux, sem a necessidade de executar comandos de shell externos.

A seguir, são detalhadas as fontes de dados no `/proc` para as principais informações exibidas pelo dashboard:

### 1. Informações Globais da CPU

*   **Fonte Principal:** `/proc/stat`
*   **Linha 'cpu' (primeira linha):** Fornece os tempos agregados da CPU em diferentes estados (em jiffies, ou unidades de clock ticks). Os campos lidos e utilizados para calcular o uso total e o tempo ocioso são:
    1.  `user`: Tempo gasto em modo usuário.
    2.  `nice`: Tempo gasto em modo usuário com prioridade "nice".
    3.  `system`: Tempo gasto em modo kernel.
    4.  `idle`: Tempo gasto em ociosidade.
    5.  `iowait`: Tempo gasto esperando por E/S (opcionalmente incluído no cálculo de tempo não-ocioso).
    6.  `irq`: Tempo gasto servindo interrupções de hardware.
    7.  `softirq`: Tempo gasto servindo interrupções de software.
    8.  `steal`: Tempo roubado por outras máquinas virtuais em um ambiente virtualizado (hypervisor).
*   **Linhas 'cpuX' (ex: `cpu0`, `cpu1`, ...):** Fornecem os mesmos campos da linha `cpu`, mas individualmente para cada núcleo do processador. Utilizadas para calcular o percentual de uso de cada core.
*   **Cálculo de Percentual:** O percentual de uso é calculado pela variação (delta) desses tempos entre duas leituras consecutivas, comparando o delta do tempo não-ocioso com o delta do tempo total.

### 2. Informações Globais de Memória

*   **Fonte Principal:** `/proc/meminfo`
*   Este arquivo contém diversos pares chave-valor sobre o estado da memória. Os principais campos lidos são (valores geralmente em KB):
    *   `MemTotal`: Memória RAM total física.
    *   `MemFree`: Memória RAM não utilizada.
    *   `MemAvailable`: Estimativa da memória disponível para iniciar novas aplicações sem entrar em swap.
    *   `Buffers`: Memória usada por buffers do kernel.
    *   `Cached`: Memória usada para cache de páginas de arquivos.
    *   `SwapTotal`: Memória de swap total.
    *   `SwapFree`: Memória de swap não utilizada.
*   **Cálculo de Percentual:** O percentual de memória usada é calculado como `((MemTotal - MemAvailable) / MemTotal) * 100`. O uso de swap é calculado similarmente.

### 3. Informações de Processos

Para cada processo (identificado por seu PID), as informações são coletadas de múltiplos arquivos dentro do diretório `/proc/[PID]/`:

*   **Fonte: `/proc/[PID]/stat`**
    *   Este arquivo contém informações de status do processo em uma única linha com campos separados por espaço. O parsing é cuidadoso devido ao segundo campo (nome do comando, `comm`) poder conter espaços e estar entre parênteses.
    *   Campos chave lidos:
        *   `(1) pid`: ID do processo.
        *   `(2) comm`: Nome do comando (entre parênteses).
        *   `(3) state`: Estado do processo (R, S, D, Z, T, etc.).
        *   `(4) ppid`: PID do processo pai.
        *   `(14) utime`: Tempo de CPU gasto em modo usuário pelo processo (em jiffies).
        *   `(15) stime`: Tempo de CPU gasto em modo kernel pelo processo (em jiffies).
        *   `(18) priority`: Prioridade do processo.
        *   `(19) nice`: Valor "nice" do processo.
        *   `(20) num_threads`: Número de threads no processo.
        *   `(22) starttime`: Tempo de início do processo após o boot do sistema (em jiffies).

*   **Fonte: `/proc/[PID]/status`**
    *   Este arquivo fornece informações de status mais legíveis em formato "Chave: Valor".
    *   Campos chave lidos:
        *   `Uid`: User ID (real, efetivo, salvo, fs). O primeiro valor (UID) é usado para obter o nome do usuário.
        *   `VmPeak`: Pico de memória virtual usada.
        *   `VmSize`: Tamanho total da memória virtual.
        *   `VmLck`: Memória bloqueada.
        *   `VmPin`: Memória "pinned" (não pode ser paginada para disco).
        *   `VmHWM`: Pico do Resident Set Size (RSS - "High Water Mark").
        *   `VmRSS`: Resident Set Size - memória física atualmente usada pelo processo.
        *   `RssAnon`, `RssFile`, `RssShmem`: Componentes do RSS (anônima, mapeada em arquivo, compartilhada).
        *   `VmData`: Tamanho do segmento de dados.
        *   `VmStk`: Tamanho da pilha (stack).
        *   `VmExe`: Tamanho do segmento de código (executável).
        *   `VmLib`: Tamanho do código de bibliotecas compartilhadas.
        *   `VmPTE`: Tamanho das Page Table Entries.
        *   `VmSwap`: Memória de swap usada pelo processo.

*   **Fonte: `/proc/[PID]/cmdline`**
    *   Contém a linha de comando completa usada para iniciar o processo. Os argumentos são separados por caracteres nulos (`\0`). É lido e processado para exibir o comando de forma legível.

### 4. Informações de Threads (por Processo)

Para cada thread de um processo (identificada por seu TID, que é o mesmo que PID para a thread principal), as informações são coletadas de `/proc/[PID]/task/[TID]/`:

*   **Fonte: `/proc/[PID]/task/[TID]/comm`**
    *   Contém o nome da thread, conforme definido pelo processo ou kernel.
*   **Fonte: `/proc/[PID]/task/[TID]/stat`**
    *   Similar ao `/proc/[PID]/stat`, mas para a thread específica. O campo de estado da thread é lido daqui.

### 5. Outras Informações do Sistema

*   **Uptime do Sistema:**
    *   **Fonte:** `/proc/uptime`
    *   O primeiro valor na linha é o tempo total de atividade do sistema em segundos.
*   **Load Average:**
    *   **Fonte:** `/proc/loadavg`
    *   Os três primeiros valores na linha representam as médias de carga do sistema para 1, 5 e 15 minutos.

## Processamento de Dados e Cálculos

Após a coleta dos dados brutos do sistema de arquivos `/proc`, diversas transformações e cálculos são realizados para apresentar informações úteis e compreensíveis no dashboard. Esses processamentos são, em grande parte, encapsulados nos métodos das classes de modelo (`SystemGlobalInfo`, `ProcessInfo`) e orquestrados pelo `SystemMonitorController`.

### 1. Cálculo do Percentual de Uso da CPU

O percentual de uso da CPU (tanto global, por core, quanto por processo) é uma métrica dinâmica que requer a comparação de valores ao longo do tempo.

*   **Base:** Os tempos de CPU são coletados em "jiffies" (ticks de clock do sistema) do arquivo `/proc/stat` (para CPU global/por core) e `/proc/[PID]/stat` (para processos).
*   **Metodologia:**
    1.  **Leituras Intervaladas:** O `SystemMonitorController` realiza leituras dos tempos de CPU em intervalos regulares.
    2.  **Cálculo do Delta:** Para cada intervalo, calcula-se a diferença (delta) entre os tempos da leitura atual e da leitura anterior para cada estado da CPU (usuário, sistema, ocioso, etc.).
        *   `Delta Total de Jiffies do Sistema = (Soma dos Jiffies Atuais de todos os estados) - (Soma dos Jiffies Anteriores de todos os estados)`
        *   `Delta de Jiffies Ociosos = (Jiffies Ociosos Atuais) - (Jiffies Ociosos Anteriores)`
    3.  **Percentual de Uso Global/Por Core:**
        *   `% CPU Ociosa = (Delta de Jiffies Ociosos / Delta Total de Jiffies do Sistema) * 100`
        *   `% CPU Usada = 100 - % CPU Ociosa`
        *   Este cálculo é realizado pela classe `SystemGlobalInfo` utilizando os dados de `last_cpu_times_jiffies_all` (para global) e `last_cpu_times_jiffies_cores` (para cada core), comparando com os valores da iteração anterior armazenados no controller.
    4.  **Percentual de Uso por Processo:**
        *   `Delta de Jiffies do Processo = (utime_atual + stime_atual) - (utime_anterior + stime_anterior)`
        *   A fórmula utilizada para o percentual de CPU de um processo, refletindo o uso em relação a um único core (onde 100% significa um core totalmente utilizado), é:
            `%CPU Processo = (Delta de Jiffies do Processo * Número de Cores * 100) / Delta Total de Jiffies do Sistema`
        *   Este cálculo é realizado pela classe `ProcessInfo`, utilizando os `utime` e `stime` do processo, os valores da iteração anterior (armazenados no controller), o `Delta Total de Jiffies do Sistema`, a frequência do clock do sistema (`system_hz` da `SystemGlobalInfo`) e o número de cores (`num_cores` da `SystemGlobalInfo`).

### 2. Cálculo do Percentual de Uso de Memória

*   **Memória Global:**
    *   O percentual de memória RAM usada é calculado com base nos campos `MemTotal` e `MemAvailable` de `/proc/meminfo`:
        `% Memória Usada = ((MemTotal - MemAvailable) / MemTotal) * 100`
    *   Um cálculo similar é feito para a memória de swap usando `SwapTotal` e `SwapFree`.
    *   Esses cálculos são realizados dentro da classe `SystemGlobalInfo` (ou na função `populate_system_global_data` que a preenche).
*   **Memória por Processo:**
    *   O percentual de memória RAM usada por um processo é calculado com base no seu `VmRSS` (Resident Set Size) e na `MemTotal` do sistema:
        `% Memória Processo = (VmRSS do Processo / MemTotal do Sistema) * 100`
    *   Este cálculo é realizado pela classe `ProcessInfo`.

### 3. Conversão do Tempo de Início do Processo

*   O tempo de início de um processo (`starttime`) é obtido de `/proc/[PID]/stat` em jiffies desde o boot do sistema.
*   Para converter em uma data e hora legíveis:
    1.  O tempo de atividade do sistema (uptime) é obtido de `/proc/uptime` em segundos.
    2.  A frequência do clock do sistema (`system_hz`) é obtido pela diferença de número de ticks obtidos de um intervalo de 1 segundo`/proc/self/stat`.
    3.  Calcula-se o momento do boot do sistema em tempo epoch: `Tempo Epoch do Boot = Tempo Epoch Atual - Uptime em Segundos`.
    4.  Converte-se o `starttime` do processo de jiffies para segundos desde o boot: `Início do Processo em Segundos Após Boot = starttime_jiffies / system_hz`.
    5.  Calcula-se o tempo epoch de início do processo: `Tempo Epoch de Início do Processo = Tempo Epoch do Boot + Início do Processo em Segundos Após Boot`.
    6.  Este valor epoch é então formatado para uma string de data/hora (ex: "AAAA-MM-DD HH:MM:SS") usando `time.strftime`.
*   Este cálculo é realizado pela classe `ProcessInfo`.

### 4. Obtenção do Nome de Usuário

*   O Nome de Usuário é obtido de `/etc/passwd`, que compara o terceiro campo com o UID fornecido.
*   Ele é obtido através da função `get_process_details()`.

### 5. Processamento da Linha de Comando (`cmdline`)

*   O arquivo `/proc/[PID]/cmdline` contém os argumentos da linha de comando separados por caracteres nulos.
*   Para exibição, esses caracteres nulos são substituídos por espaços para formar uma string legível.

### 6. Agregação de Contagens Totais

*   **Total de Processos:** Contagem direta do número de diretórios numéricos em `/proc/` (ou o tamanho da lista de objetos `ProcessInfo` coletada).
*   **Total de Threads:** Soma do campo `num_threads` (obtido de `/proc/[PID]/stat`) de todos os objetos `ProcessInfo` coletados.
*   **Processos em Execução (Running):** Contagem de processos cujo campo `state` é 'R'.
*   Essas agregações são realizadas pelo `SystemMonitorController` e armazenadas na instância `SystemGlobalInfo`.

