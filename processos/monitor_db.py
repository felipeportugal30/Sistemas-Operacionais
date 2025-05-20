import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_json("/home/felipe-portugal/sistemas-operacionais/event_log.json")

thread_states = {}
last_time = 0

for _, log in df.iterrows():
    thread_id = log["thread_id"]

    if thread_id not in thread_states:
        thread_states[thread_id] = {"times": [0], "states": [0]}

    last_time = max(last_time, log["time"])

    if log["event"] == "acquire_db":
        thread_states[thread_id]["times"].append(log["time"])
        thread_states[thread_id]["states"].append(1)

    elif log["event"] in ["release_db", "release_both"]:
        thread_states[thread_id]["times"].append(log["time"])
        thread_states[thread_id]["states"].append(0)

for thread_id in thread_states:
    thread_states[thread_id]["times"].append(last_time + 1)
    thread_states[thread_id]["states"].append(thread_states[thread_id]["states"][-1])

# Gráfico do BANCO DE DADOS
plt.figure(figsize=(14, 8))

offset = 1.5  # Para espaçar visualmente as linhas

for i, (thread_id, data) in enumerate(thread_states.items()):
    shifted_states = [s + i * offset for s in data["states"]]
    plt.step(data["times"], shifted_states, where="post", label=f"Thread {thread_id}", linewidth=2.5)

plt.title("Acesso ao Banco de Dados por Programador", fontsize=16)
plt.xlabel("Tempo (s)", fontsize=12)
plt.yticks(
    [i * offset for i in thread_states],
    [f"Thread {i}" for i in thread_states]
)
plt.grid(True, linestyle="--", alpha=0.5)
plt.legend(loc="upper right")
plt.tight_layout()
plt.savefig("grafico_banco.png")

