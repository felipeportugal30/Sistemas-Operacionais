import numpy as np
import random

def gerar_referencia_numpy(num_total_paginas_logicas, centro, desvio):
    #Gera uma referência de página usando a função do numpy numpy.random.normal

    referencia_continua = np.random.normal(loc=centro, scale=desvio)
    pagina_acessada = int(round(referencia_continua))
    pagina_acessada = max(0, min(pagina_acessada, num_total_paginas_logicas - 1))
    return pagina_acessada

# --- 3. Função Principal de Simulação para Gerar o Rastro ---
def gerar_rastro_acesso(num_total_paginas_logicas=26, centro_inicial=3, desvio=3,
                         passo_inicial=0.3, total_ref=5000):
    #Simula uma sequência de acessos a páginas lógicas (A-Z) com um conjunto de trabalho
    #que se move de forma gradual e alternada.

    #Input:
    #    num_total_paginas_logicas: O número total de páginas lógicas (fixo em 26 para A-Z).
    #    centro_inicial: O centro inicial da distribuição gaussiana (0 a 25).
    #    desvio: O desvio padrão da distribuição gaussiana.
    #    passo_inicial: O quanto o centro se move em cada iteração.
    #    total_ref: O número total de referências de páginas a serem geradas.

    #Output:
    #    list: Um vetor (lista) de strings, representando as páginas acessadas
    #
    centro_atual = float(centro_inicial)
    passo_atual = float(passo_inicial)
    acessos = []

    # Mapeamento fixo para 'A' a 'Z', já que num_total_paginas_logicas é 26
    mapeamento_pagina_para_representacao = {i: chr(65 + i) for i in range(num_total_paginas_logicas)}

    print(f"\n--- Gerando Rastro de Acesso para {num_total_paginas_logicas} Páginas Lógicas (A-Z) ---")
    print(f"Configurações do Conjunto de Trabalho: Centro Inicial={centro_inicial}, Desvio={desvio}, Passo={passo_inicial}, Total Referências={total_ref}")

    for _ in range(total_ref):
        # A referência gerada é um número de 0 a 25
        pagina_acessada_numero = gerar_referencia_numpy(num_total_paginas_logicas, centro_atual, desvio)
        
        # Converte o número da página para a letra correspondente
        pagina_acessada_string = mapeamento_pagina_para_representacao[pagina_acessada_numero]
        acessos.append(pagina_acessada_string)

        # Lógica para Movimento Gradativo e Alternado do Centro (dentro das 26 páginas)
        # Os limites agora são em relação ao intervalo [0, 25]
        limite_inferior_movimento = desvio * 0.5 # Mantém a distribuição afastada da página 0
        limite_superior_movimento = num_total_paginas_logicas - 1 - desvio * 0.5 # Mantém a distribuição afastada da página 25

        centro_atual += passo_atual

        if centro_atual > limite_superior_movimento:
            centro_atual = limite_superior_movimento
            passo_atual *= -1
        elif centro_atual < limite_inferior_movimento:
            centro_atual = limite_inferior_movimento
            passo_atual *= -1

    print(f"--- Geração do Rastro Concluída. Centro final: {centro_atual:.2f} ---")
    return acessos

if __name__ == "__main__":
    rastro_do_processo = gerar_rastro_acesso()

    print("\n--- AMOSTRA DO RASTRO DE ACESSO GERADO (primeiros 150 acessos) ---")
    print(rastro_do_processo[:150])