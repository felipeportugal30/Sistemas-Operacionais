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
    logs(memoria, faltas)
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

    logs(memoria, faltas, frequencia)  
  return faltas

# ------------ Logs ------------
def logs (memoria, faltas, frequencia=None):
  print(f"\033[34mMemória\033[0m\t-> \033[32m{list(memoria)}\033[0m")
  if frequencia:
    print(f"\033[34mFreq\033[0m\t-> \033[32m{frequencia}\033[0m")
  print(f"\033[33mFaltas\033[0m\t-> \033[31m{faltas}\033[0m")
  

# ------------ Simulação ------------
def simular (ref, num_mold):
  faltas_fifo = fifo(ref, num_mold)
  faltas_envelhecimento = envelhecimento(ref, num_mold)
  return faltas_fifo, faltas_envelhecimento

ref = ["A","B","A","C","D","E","F","G","F","G","E","H","H","E","F","G"]
envelhecimento(ref, 3)