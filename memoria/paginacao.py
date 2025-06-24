"""
Comparar o sistema de paginação: FIFO x Algoritmo de envelhecimento
Parametros:
- Número de molduras

Páginas: a sequência de referências de página deve ser organizada simulando conjuntos de trabalho de processos
Cada conjunto de trabalho deve simular algo real, com diferentes tempo de duração e tamanhos

A sequência de referências geradas deve ser anotado para conferência
Analise o número de falta de páginas por 1000 referências de memória, como função do número de molduras de páginas disponíveis
"""

# ------------ Algoritmo FIFO ------------
from collections import deque

def fifo (ref, num_mold):
  memoria = deque() # Memória deve ser uma fila
  faltas = 0
  for pagina in ref:
    if pagina not in memoria:
      faltas += 1
      if len(memoria) >= num_mold:
        memoria.popleft() # Sai o primeiro que entrou
      memoria.append(pagina)
    logs("FIFO", memoria, faltas)
  return faltas

# ------------ Algoritmo de Envelhecimento ------------
def envelhecimento (ref, num_mold,bits=8):
  memoria = []
  frequencia = {}
  faltas = 0

  for pagina in ref:
    for p in memoria: 
      frequencia[p] >>= 1
    if pagina in memoria: 
      frequencia[pagina] |= 1 << (bits - 1)
    else:
      faltas += 1
      if len(memoria) >= num_mold:
        pag_sub = min(memoria, key=frequencia.get)
        memoria.remove(pag_sub)
        del frequencia[pag_sub]
      memoria.append(pagina)
      frequencia[pagina] = 256

    logs("ENVELHECIMENTO", memoria, faltas, frequencia)  
  return faltas

# ------------ Logs ------------
import json
from collections import defaultdict

global_logs = defaultdict(list)

def logs (algoritmo, memoria, faltas, frequencia=None, save_to_file=True):
  log_entry = {
      "memoria": list(memoria),
      "frequencia": frequencia if frequencia else None,
      "faltas": faltas
  }

  global_logs[algoritmo].append(log_entry)

  # print(f"\033[1;4m{algoritmo}\033[0m")
  # print(f"\033[1;34mMemória\033[0m\t-> \033[32m{list(memoria)}\033[0m")
  # if frequencia:
  #   print(f"\033[1;36mFreq\033[0m\t-> \033[35m{frequencia}\033[0m")
  # print(f"\033[1;33mFaltas\033[0m\t-> \033[31m{faltas}\033[0m")

from pathlib import Path

def save_logs_to_file(processos, logs, filename='./logs/memoria_logs.json'):
    try:
        Path(filename).parent.mkdir(parents=True, exist_ok=True)

        data_to_save = {
            "sequencia_processos": processos,
            "logs_algoritmos": logs
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, indent=4, ensure_ascii=False)
            
        print(f"Logs salvos com sucesso em: {filename}")
    except (IOError, OSError) as e:
        print(f"Erro ao salvar logs: {str(e)}")
        raise
  

# ------------ Simulação ------------
def simular (ref, num_mold):
  faltas_fifo = fifo(ref, num_mold)
  faltas_envelhecimento = envelhecimento(ref, num_mold)
  return faltas_fifo, faltas_envelhecimento

from gaussiana import gerar_rastro_acesso

if __name__ == "__main__":
    rastro_do_processo = gerar_rastro_acesso()

    simular(rastro_do_processo, 10)

    save_logs_to_file(rastro_do_processo, global_logs)