import uuid

BLOCK_SIZE = 4
MAX_BLOCKS = 16

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
        self.first_block = None
        self.children = {} if is_dir else None
        self.parent = None

    def __repr__(self):
        return f"{'[DIR]' if self.is_dir else '[FILE]'} {self.name} (size: {self.size})"

class FileSystem:
    def __init__(self):
        self.root = Inode("/", True)
        self.current = self.root
        self.path = [self.root]
        self.disk = [None] * MAX_BLOCKS
        self.free_space = list(range(MAX_BLOCKS - 1, -1, -1))
        print(self.free_space)

    def allocate_block(self, data):
        if not self.free_space:
            print("Error: No free space available on disk.")
            return None
        idx = self.free_space.pop(0)
        self.disk[idx] = Block(data)
        return idx

    def write_blocks(self, data):
        parts = [data[i: i + BLOCK_SIZE] for i in range(0, len(data), BLOCK_SIZE)]
        if len(parts) > len(self.free_space):
            print("Error: Not enough free blocks to write data.")
            return None

        head = None
        previous = None

        for part in parts:
            idx = self.allocate_block(part)
            if idx is None:
                return None
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
            block = self.disk[current]
            if block is None:
                break
            next_block = block.next
            self.disk[current] = None  # libera bloco
            self.free_space.append(current)
            current = next_block


    def _get_path_str(self): # Mostra o caminho atual no path
        return "/" + "/".join(node.name for node in self.path[1:])

    def mkdir(self, name):
        if name in self.current.children:
            print("Directory already exists.")
        else:
            new_dir = Inode(name, True)
            new_dir.parent = self.current

            idx = self.allocate_block("")  # <-- aloca bloco para o diretório
            if idx is None:
                print("No space to allocate directory block.")
                return

            new_dir.first_block = idx
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

    def space(self):
        print(f"Total blocks: {len(self.disk)}")
        print(f"Free blocks: {len(self.free_space)} - {sorted(self.free_space)}")
        print("Disk blocks status:")
        for i, block in enumerate(self.disk):
            if block is None:
                print(f"  Block {i}: [FREE]")
            else:
                print(f"  Block {i}: [USED] Content: '{block.data}' Next: {block.next}")


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
            if inode.first_block is not None:
                self.free_blocks(inode.first_block)

            head = self.write_blocks(data)
            if head is not None:
                inode.first_block = head
                inode.size = len(data)
            else:
                print("Failed to write: Not enough space.")
        else:
            print("File not found.")
    
    def read(self, name, position=None):
        if name in self.current.children and not self.current.children[name].is_dir:
            inode = self.current.children[name]
            full_content = self.read_blocks(inode.first_block)
            
            if position is not None:
                try:
                    return full_content[position] if position < len(full_content) else None
                except IndexError:
                    return None
            return full_content
        return None
    
    def rm(self, name):
        if name in self.current.children:
            inode = self.current.children[name]

            if inode.is_dir:
                for child in list(inode.children.values()):
                    self._recursive_delete(child)
            else:
                self.free_blocks(inode.first_block)

            if inode.first_block is not None:
                self.free_blocks(inode.first_block)  # <-- libera o bloco do diretório

            del self.current.children[name]
        else:
            print("File or directory not found.")


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
                case 'space':
                    self.space()
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
                case _:
                    print("Invalid command or arguments")

if __name__ == "__main__":
    fs = FileSystem()
    fs.run()