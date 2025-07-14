import uuid

class Inode:
    def __init__(self, name, is_dir, parent='~'):
        self.id = uuid.uuid4()
        self.name = name
        self.is_dir = is_dir
        self.size = 0
        self.children = {} if is_dir else None
        self.parent = parent
        self.content = "" if not is_dir else None

    def __repr__(self):
        return f"{'[DIR]' if self.is_dir else '[FILE]'} {self.name} (size: {self.size})"

NUMBER_INODES = 100

class FileSystem:
    def __init__(self):
        self.inode_table = [None] * NUMBER_INODES
        self.list_allocated_inodes = [-1] * NUMBER_INODES
        self.available_space = NUMBER_INODES

        self.root = Inode("/", True)
        self.root.id = 0 # Id para a raiz
        self.inode_table[0] = self.root
        self.list_allocated_inodes[0] = 0
        self.available_space -= 1

        self.current = self.root
        self.path = [self.root]

        print(f"available space: {self.available_space}")

    def has_space(self):
        return self.available_space > 0

    def space_can_use(self):
        print(f"available space: {self.available_space}")
        for index, inode_id in enumerate(self.list_allocated_inodes):
            print(f"index {index}: id {inode_id}")

    def _get_path_str(self): # Mostra o caminho atual no path
        return "/" + "/".join(node.name for node in self.path[1:])

    def mkdir(self, name):
        if name in self.current.children:
            print("Directory already exists.")
        elif self.available_space > 0: #Se tiver espaço disponível, vai passar desse if
            for i, value in enumerate(self.list_allocated_inodes):
                if value == -1:
                    new_inode = Inode(name, True, self.current)
                    self.inode_table[i] = new_inode
                    self.list_allocated_inodes[i] = new_inode.id
                    self.current.children[name] = new_inode
                    self.available_space -= 1
                    break
        else: 
            print("No free space available.")
        
    def touch(self, name): # Cria um novo arquivo
        if name in self.current.children:
            print("File already exists.")
        elif self.available_space > 0: #Se tiver espaço disponível, vai passar desse if
            for i, value in enumerate(self.list_allocated_inodes):
                if value == -1:
                    new_inode = Inode(name, False, self.current)
                    self.inode_table[i] = new_inode
                    self.list_allocated_inodes[i] = new_inode.id
                    self.current.children[name] = new_inode
                    self.available_space -= 1
                    break
        else: 
            print("No free space available.")

    def ls(self, detailed=False):
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
    
    # Função acessório para mv
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

    def write(self, name, data):
        if name in self.current.children and not self.current.children[name].is_dir:
            inode = self.current.children[name]
            inode.content = data  # substituição direta (mais justo no benchmark)
            inode.size = len(inode.content)
        else:
            if self.debug:
                print("File not found.")

    def read(self, name, position=None):
        if name in self.current.children and not self.current.children[name].is_dir:
            inode = self.current.children[name]
            if position is not None:
                return inode.content[position]
            else:
                return inode.content
        else:
            if self.debug:
                print("File not found.")
            return None

    def rm(self, name):
        if name in self.current.children:
            def _recursive_delete(inode):
                if inode.is_dir:
                    for child in list(inode.children.values()):
                        _recursive_delete(child)
                    inode.children.clear()
                inode.content = ""
                inode.size = 0
                for i, value in enumerate(self.list_allocated_inodes):
                    if value == inode.id:
                        self.list_allocated_inodes[i] = -1
                        self.inode_table[i] = None
                        break
                self.available_space += 1  # Mover para fora do loop
                inode.id = -1

            inode = self.current.children[name]
            _recursive_delete(inode)
            del self.current.children[name]

    def inode(self, name): # Comando para verificar o inode do arquivo ou diretório
        if name == ".":
            target = self.current
        elif name in self.current.children:
            target = self.current.children[name]
        else:
            print("File or directory not found.")
            return

        parent_name = target.parent.name if isinstance(target.parent, Inode) else target.parent
        print(f"Informações do INode:\n"
              f"Id\t\t{target.id}\n"
              f"Name\t\t{target.name}\n"
              f"Is_dir\t\t{target.is_dir}\n"
              f"Parent\t\t{parent_name}\n"
              f"Content\t\t{target.content}\n")
        if target.is_dir:
            print(f"Children:\t{list(target.children.keys())}")

    def pwd(self):
        print(self._get_path_str())

    def help(self):
        print("Available commands:")
        print("  cd <directory>      - Change current directory (use '..' for parent, '.' for current)")
        print("  mkdir <name>        - Create a new directory")
        print("  touch <name>        - Create a new file")
        print("  ls                  - List contents of current directory")
        print("  mv <src> <dest>     - Move file/directory from source to destination")
        print("  write <file> <data> - Write data to a file (overwrites existing content)")
        print("  read <file>         - Read content from a file")
        print("  rm <name>           - Remove a file or directory (recursively)")
        print("  inode <name>        - Show inode information for a file/directory")
        print("  pwd                 - Print current working directory path")
        print("  space               - Show available space and inode allocation")
        print("  help                - Show this help message")
        print("  exit                - Exit the file system")


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
                case 'space':
                    self.space_can_use()
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
                case 'pwd':
                    self.pwd()
                case 'help':
                    self.help()
                case _:
                    print("Invalid command or arguments")

if __name__ == "__main__":
    fs = FileSystem()
    fs.run()