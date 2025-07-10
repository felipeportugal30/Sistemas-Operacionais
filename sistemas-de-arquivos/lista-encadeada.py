import uuid

BLOCK_SIZE = 4

class Block:
    def __init__(self, data='', next = None):
        self.data = data
        self.next = next

class Inode:
    def __init__(self, name, is_dir):
        self.id = uuid.uuid4()
        self.name = name
        self.is_dir = is_dir
        self.size = 0
        self.first_block = 0
        self.children = {} if is_dir else None
        self.parent = None

    def __repr__(self):
        return f"{'[DIR]' if self.is_dir else '[FILE]'} {self.name} (size: {self.size})"

class FileSystem:
    def __init__(self):
        self.root = Inode("/", True)
        self.current = self.root
        self.path = [self.root]    
        self.disk = []
        self.free_space = []

    def allocate_block(self, data):
        idx = self.free_space.pop() if self.free_space else len(self.disk)
        if idx < len(self.disk):
            self.disk[idx] = Block(data)
        else:
            self.disk.append(Block(data))
        return idx

    def write_blocks(self, data):
        parts = [data[i: i + BLOCK_SIZE] for i in range(0, len(data), BLOCK_SIZE)]
        head = None
        previous = None

        for part in parts:
            idx = self.allocate_block(part)
            if previous is not None:
                self.disk[previous].next = idx
            else:
                head = idx
            previous = idx
        return head
            
    def read_blocks(self, start_index):
        if start_index == None:
            return ''

        data = ''
        current = start_index
        while current is not None:
            block = self.disk[current]
            data += block.data
            current = block.next
        return data
    
    def free_blocks(self, start_index):
        current = start_index
        while current is not None:
            next = self.disk[current].next
            self.disk[current] = Block()
            self.free_space.append(current)
            current = next


    def _get_path_str(self): # Mostra o caminho atual no path
        return "/" + "/".join(node.name for node in self.path[1:])

    def mkdir(self, name):  # Cria um novo diretório
        if name in self.current.children:
            print("Directory already exists.")
        else: 
            new_dir = Inode(name, True)
            new_dir.parent = self.current
            self.current.children[name] = new_dir


    def touch(self, name):  # Cria um novo arquivo
        if name in self.current.children:
            print("File already exists.")
        else:
            new_file = Inode(name, False)
            new_file.parent = self.current
            self.current.children[name] = new_file

    def ls(self): # Lista os filhos do diretório atual
        for name in self.current.children:
            inode = self.current.children[name]
            print(f"{name}/" if inode.is_dir else name)

    def cd(self, name): # Navega entre os repositórios
        if name == "..":
            if len(self.path) > 1:
                self.path.pop()
                self.current = self.path[-1]
        elif name == ".":
            pass
        elif name in self.current.children and self.current.children[name].is_dir:
            self.current = self.current.children[name]
            self.path.append(self.current)
        else:
            print("Directory not found.")

    def resolve_path(self, path):
        parts = path.strip("/").split("/")
        node = self.root if path.startswith("/") else self.current

        for part in parts:
            if part == '' or part == '.':
                continue
            elif part == '..':
                if node.parent != '~':
                    node = node.parent
            elif part in node.children and node.children[part].is_dir:
                node = node.children[part]
            else:
                return None
        return node

    def mv(self, src, dest_path):
        if src not in self.current.children:
            print("Source file not found.")
            return

        dest_dir = self.resolve_path(dest_path)
        if not dest_dir or not dest_dir.is_dir:
            print("Destination directory not found.")
            return

        inode = self.current.children.pop(src)
        dest_dir.children[src] = inode
        inode.parent = dest_dir

    # def mv(self, src, dest):  # Move arquivos/diretórios
    #     if src not in self.current.children:
    #         print("Source file not found.")
    #         return
    #     if dest not in self.current.children or not self.current.children[dest].is_dir:
    #         print("Destination directory not found.")
    #         return
    #     inode = self.current.children.pop(src)
    #     inode.parent = self.current.children[dest]  # Atualiza o parent
    #     self.current.children[dest].children[src] = inode

    def write(self, name, data): # Escreve dentro de um arquivo
        if name in self.current.children and not self.current.children[name].is_dir:
            inode = self.current.children[name]
            inode.first_block = self.write_blocks(data)
            self.free_blocks(inode.first_block)
            inode.first_block = self.write_blocks(data)
            inode.size = len(data)
        else:
            print("File not found.")

    def read(self, name): # Le um arquivo
        if name in self.current.children and not self.current.children[name].is_dir:
            inode = self.current.children[name]
            print(self.read_blocks(inode.first_block))
        else:
            print("File not found.")

    def rm(self, name):  # Remove arquivo ou diretório
        if name in self.current.children:
            inode = self.current.children[name]
            if not inode.is_dir:
                self.free_blocks(inode.first_block)
            del self.current.children[name]
        else:
            print("File or directory not found.")


    def inode(self, name): # Comando para verificar o inode do arquivo ou diretório
        
        if len(name) == 1 and name == ".":
            print(f"Informações do INode: \nId\t\t{self.current.id}\nName\t\t{name}\nIs_dir\t\t{self.current.is_dir}\nParent\t\t{self.current.parent}\nContent\t\t{self.current.content}\nBlocks\t\t{self.current.blocks}\n")
        if name in self.current.children:
            print(f"Informações do INode: \nId\t\t{self.current.children[name].id}\nName\t\t{name}\nIs_dir\t\t{self.current.children[name].is_dir}\nParent\t\t{self.current.children[name].parent}")
        else:
            print("Directory not found.")


    def run(self):
        while True:
            cmd = input(f"{self._get_path_str()}$ ").strip().split()
            if not cmd:
                continue
            command = cmd[0]
            args = cmd[1:]

            match command:
                case 'exit': # Finaliza a execução
                    break
                case 'cd':
                    if args:
                        self.cd(args[0])
                case 'mkdir':
                    if args:
                        self.mkdir(args[0])
                case 'touch':
                    if args:
                        self.touch(args[0])
                case 'mv':
                    if len(args) == 2:
                        self.mv(args[0], args[1])
                case 'write':
                    if len(args) >= 2:
                        self.write(args[0], " ".join(args[1:]))
                case 'read':
                    if args:
                        self.read(args[0])
                case 'ls':
                    self.ls()
                case 'rm':
                    if args:
                        self.rm(args[0])
                case 'inode':
                    if args:
                        self.inode(args[0])
                case _:
                    print("Invalid command or arguments")

if __name__ == "__main__":
    fs = FileSystem()
    fs.run()
