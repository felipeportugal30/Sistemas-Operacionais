""" REGRAS: 
5 progamadores trabalhando em um laboratório
Cada um precisa de um acesso exclusivo ao compilador
No máximo dois compiladores podem acessar o banco
Após compilar, o programador descansa, depois compila de novo
A compilação só pode começar quando o programador tem acesso aos dois
Sistema deve evitar deadlocks e inanição
"""
""" FUNCIONAMENTO:
semáforos: para controle de recursos
thread: para cada programador
essas solicitam acesso ao banco de dados e ao compilador
essas tambem liberam o compilador e o banco de dados
essas vão ter um tempo de descanso
"""
import threading
import time
import random
import json

sem_db = threading.Semaphore(2)
sem_comp = threading.Semaphore(1)
acquire_lock = threading.Lock()
log_lock = threading.Lock()
event_log = []

class Programmer(threading.Thread):
    def __init__(self, id):
        super().__init__()
        self.id = id
        self.isComp = False
        self.isDb = False
        self.compilations = 0
        self.daemon = True

    def think(self):
        print(f"[THK {self.id}] 💭 Programmer {self.id} is thinking...")
        logEvent(self.id, "thinking")
        time.sleep(random.uniform(5, 8))

    def compile(self):
        print(f"[CMP {self.id}] 🛠️ Programmer {self.id} is compiling...")
        logEvent(self.id, "compiling")
        time.sleep(random.uniform(5, 8))
        print(f"[FNS {self.id}] ✅ Programmer {self.id} finishes the compilation!")
        logEvent(self.id, "finishing_compiling")
        self.compilations += 1

    """ 
    O Lock é uma exclusão mutua forte (uma thread pode entrar por vez)
    A thread entra no lock (apenas ela)
    Se os acquires ficarem esperando a thread mantém o Lock preso durante todo esse tempo
    Programador 1 entra no Lock,tenta entrar no banco e consegue, agora tenta entrar no compilador, mas está ocupado.  
    Ele fica esperando dentro do Lock e enquanto isso, os outros programadores não conseguem entrar nem tentar.
    """ 
    """
    def acess_db(self):
        sem_db.acquire()
        print(f"Programmer {self.id} acessed the data base")
        self.isDb = True
    def acess_comp(self):
        sem_comp.acquire()
        print(f"Programmer {self.id} acessed the compiler")
        self.isComp = True
    """
        
    
    def acess_resources(self):
      while True:
          got_db = False
          got_comp = False

          # impede que múltiplas threads entrem nesse bloco ao mesmo tempo, 
          # evitando deadlock e inaninação
          with acquire_lock:
              # blocking = False => evita que o programador segure um recurso
              got_db = sem_db.acquire(blocking=False)

              # tenta acessar o banco de dados
              if got_db:
                  logEvent(self.id, "acquire_db")
                  print(f"[ADB {self.id}] Programmer {self.id} accessed database.")

                  got_comp = sem_comp.acquire(blocking=False)

                  # se acessar o banco, tenta acessar o compilador
                  if got_comp:
                      logEvent(self.id, "acquire_compiler")
                      print(f"[ACP {self.id}] Programmer {self.id} accessed compiler.")
                      logEvent(self.id, "acquire_both")
                      print(f"[ABR {self.id}] Programmer {self.id} accessed both resources.")

                      self.isDb = True
                      self.isComp = True
                      return  # só retorna se tiver os dois
                  else:
                      # libera o banco de dados se não conseguir acessar o compilador
                      sem_db.release() 
                      logEvent(self.id, "release_db")
                      print(f"[RDB {self.id}] Programmer {self.id} released DB.")

          time.sleep(random.uniform(2, 4))  # espera antes de tentar de novo


    def release_resources(self):
      if self.isComp:
          sem_comp.release()
          logEvent(self.id, "release_compiler")
          print(f"[RCM {self.id}] ⬇️ Programmer {self.id} released compiler.")
          self.isComp = False

      if self.isDb:
          sem_db.release()
          logEvent(self.id, "release_db")
          print(f"[RDB {self.id}] ⬇️ Programmer {self.id} released DB.")
          self.isDb = False

    def run(self):
        while True:
            self.think()
            print(f"[TAR {self.id}] Programmer {self.id} is trying to acess resources...")
            self.acess_resources()

            try:
                self.compile()
            finally:
                self.release_resources()

def logEvent(thread_id, event_type):
    with log_lock:
      event_log.append({
          "time": round(time.time() - start_time, 3),
          "thread_id": thread_id,
          "event": event_type
      })


if __name__ == "__main__":
    start_time = time.time()
    programmers = []

    for i in range(5):
        p = Programmer(i)
        programmers.append(p)
        p.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        with open("./logs/event_log.json", "w") as f:
            json.dump(event_log, f, indent=2)

        print("\n✅ Logs saved in 'event_log.json'")
        print("\n❌Finishing the process...")