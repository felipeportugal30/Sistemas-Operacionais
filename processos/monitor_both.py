import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_json("/home/felipe-portugal/sistemas-operacionais/event_log.json")

def process_event(df, event_on, event_off):
    states = {}
    last_time = 0

    for _, log in df.iterrows():
        thread_id = log["thread_id"]
        if thread_id not in states:
            states[thread_id] = {"times": [0], "states": [0]}

        last_time = max(last_time, log["time"])

        if log["event"] == event_on:
            states[thread_id]["times"].append(log["time"])
            states[thread_id]["states"].append(1)
        elif log["event"] == event_off:
            states[thread_id]["times"].append(log["time"])
            states[thread_id]["states"].append(0)

    for thread_id in states:
        states[thread_id]["times"].append(last_time + 1)
        states[thread_id]["states"].append(states[thread_id]["states"][-1])

    return states


# Preparar dados
db_states = process_event(df, "acquire_db", "release_db")
comp_states = process_event(df, "acquire_compiler", "release_compiler")

# Plot lado a lado
fig, axs = plt.subplots(2, 1, figsize=(14, 12), sharex=True)

offset = 1.5

# Banco de Dados
for i, (thread_id, data) in enumerate(db_states.items()):
    shifted = [s + i * offset for s in data["states"]]
    axs[0].step(data["times"], shifted, where="post", label=f"Thread {thread_id}", linewidth=1)

axs[0].set_title("Acesso ao Banco de Dados")
axs[0].set_yticks([i * offset for i in db_states])
axs[0].set_yticklabels([f"Thread {i}" for i in db_states])
axs[0].grid(True, linestyle="--", alpha=0.5)
axs[0].legend(loc="upper right")

# Compilador
for i, (thread_id, data) in enumerate(comp_states.items()):
    shifted = [s + i * offset for s in data["states"]]
    axs[1].step(data["times"], shifted, where="post", label=f"Thread {thread_id}", linewidth=2.5)

axs[1].set_title("Acesso ao Compilador")
axs[1].set_xlabel("Tempo (s)")
axs[1].set_yticks([i * offset for i in comp_states])
axs[1].set_yticklabels([f"Thread {i}" for i in comp_states])
axs[1].grid(True, linestyle="--", alpha=0.5)
axs[1].legend(loc="upper right")

plt.tight_layout()
plt.savefig("painel_acesso.png")
