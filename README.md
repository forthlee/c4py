# c4py - A Python-Powered C Compiler

`c4py` is a Python-based C compiler inspired by Robert Swierczek's [c4](https://github.com/rswier/c4), a minimalist C compiler implemented in four functions. This project reimplements `c4` in Python, maintaining its simplicity while leveraging Python's clarity and flexibility. It compiles a subset of C code into an intermediate representation and executes it using a virtual machine (VM).

## Features
- **Python Implementation**: Rewrites `c4`'s core functionality in Python for readability and maintainability.
- **C Subset Support**: Compiles basic C constructs, including `int`, `char`, pointers, functions, conditionals, loops, and standard library functions (`printf`, `malloc`, etc.).
- **Virtual Machine**: Executes compiled code via a simple VM, similar to the original `c4`.
- **Debugging**: Supports a `-s` flag to print source code and generated opcodes for debugging.
- **Cross-Platform**: Runs on any system with Python 3.6+.

## Installation

### Prerequisites
- Python 3.6 or higher
- A POSIX-compatible system (Linux, macOS, or Windows with WSL for full functionality)

### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/forthlee/c4py.git
   cd c4py
   ```
2. No compilation is required, as the project is written in Python.

## Usage
Run the compiler with a C source file:
```bash
python c4py.py [-s|-d] <source_file.c>
```
- `-s`: Optional flag to display source code and intermediate opcodes.
- `-d`: Optional flag to debug.
- `<source_file.c>`: The input C source file to compile and execute.

### Example
Create a file `hello.c`:
```c
#include <stdio.h>
int main() {
    printf("Hello, Python World!\n");
    return 0;
}
```
Run:
```bash
python c4py.py hello.c
```
Output:
```
Hello, Python World!
```
self-hosting:
```bash
python c4py.py c4.c c4.c hello.c
```

## How It Works
1. **Parsing**: The compiler reads the C source, tokenizes it, and constructs a symbol table.
2. **Code Generation**: Produces intermediate opcodes (e.g., `IMM`, `PSH`, `ADD`) for the VM.
3. **Execution**: The VM interprets the opcodes, managing a stack and calling system functions as needed.
4. **System Calls**: Emulates standard library functions (`printf`, `malloc`, etc.) using Python's capabilities.

## Differences from Original c4
- **Language**: Written in Python instead of C, making it easier to modify and extend.
- **Readability**: Python's syntax improves code clarity compared to `c4`'s compact C implementation.
- **Portability**: Runs anywhere Python is installed, though some system calls may be platform-dependent.
- **Performance**: Slower than `c4` due to Python's interpreted nature but prioritizes development ease.

## Limitations
- Supports only a subset of C (no structs, unions, or floating-point types).
- Minimal error handling, with basic error messages for syntax issues.
- System call support may vary by platform (e.g., `open`, `read` on POSIX systems).
- Performance is not optimized, as the focus is on simplicity and clarity.
