import ctypes
from ctypes import wintypes

import win32api
import win32con
import win32gui
import win32process


# ============================================================
# Windows API
# ============================================================

kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

OpenProcess = kernel32.OpenProcess
OpenProcess.argtypes = [
    wintypes.DWORD,
    wintypes.BOOL,
    wintypes.DWORD
]
OpenProcess.restype = wintypes.HANDLE

CloseHandle = kernel32.CloseHandle
CloseHandle.argtypes = [wintypes.HANDLE]
CloseHandle.restype = wintypes.BOOL

VirtualAllocEx = kernel32.VirtualAllocEx
VirtualAllocEx.argtypes = [
    wintypes.HANDLE,
    ctypes.c_void_p,
    ctypes.c_size_t,
    wintypes.DWORD,
    wintypes.DWORD
]
VirtualAllocEx.restype = ctypes.c_void_p

VirtualFreeEx = kernel32.VirtualFreeEx
VirtualFreeEx.argtypes = [
    wintypes.HANDLE,
    ctypes.c_void_p,
    ctypes.c_size_t,
    wintypes.DWORD
]
VirtualFreeEx.restype = wintypes.BOOL

ReadProcessMemory = kernel32.ReadProcessMemory
ReadProcessMemory.argtypes = [
    wintypes.HANDLE,
    ctypes.c_void_p,
    ctypes.c_void_p,
    ctypes.c_size_t,
    ctypes.POINTER(ctypes.c_size_t)
]
ReadProcessMemory.restype = wintypes.BOOL

WriteProcessMemory = kernel32.WriteProcessMemory
WriteProcessMemory.argtypes = [
    wintypes.HANDLE,
    ctypes.c_void_p,
    ctypes.c_void_p,
    ctypes.c_size_t,
    ctypes.POINTER(ctypes.c_size_t)
]
WriteProcessMemory.restype = wintypes.BOOL


# ============================================================
# Constantes
# ============================================================

PROCESS_VM_OPERATION = 0x0008
PROCESS_VM_READ = 0x0010
PROCESS_VM_WRITE = 0x0020

MEM_COMMIT = 0x1000
MEM_RESERVE = 0x2000

MEM_RELEASE = 0x8000

PAGE_READWRITE = 0x04

LVIF_TEXT = 0x0001

LVM_FIRST = 0x1000
LVM_SETITEMPOSITION = LVM_FIRST + 15
LVM_GETITEMCOUNT = LVM_FIRST + 4
LVM_GETITEMPOSITION = LVM_FIRST + 16
LVM_GETITEMTEXTW = LVM_FIRST + 115


# ============================================================
# Estruturas
# ============================================================

class POINT(ctypes.Structure):
    _fields_ = [
        ("x", wintypes.LONG),
        ("y", wintypes.LONG),
    ]


class LVITEMW(ctypes.Structure):
    _fields_ = [
        ("mask", wintypes.UINT),
        ("iItem", wintypes.INT),
        ("iSubItem", wintypes.INT),
        ("state", wintypes.UINT),
        ("stateMask", wintypes.UINT),
        ("pszText", ctypes.c_void_p),
        ("cchTextMax", wintypes.INT),
        ("iImage", wintypes.INT),
        ("lParam", ctypes.c_void_p),
        ("iIndent", wintypes.INT),
        ("iGroupId", wintypes.INT),
        ("cColumns", wintypes.UINT),
        ("puColumns", ctypes.c_void_p),
        ("piColFmt", ctypes.c_void_p),
        ("iGroup", wintypes.UINT),
    ]


# ============================================================
# Localizar SysListView32
# ============================================================

def get_desktop_listview():
    """
    Localiza a janela SysListView32 responsável
    pelos ícones da Área de Trabalho.
    """

    progman = win32gui.FindWindow(
        "Progman",
        None
    )

    if not progman:
        raise RuntimeError(
            "Progman não encontrado."
        )

    shell_view = win32gui.FindWindowEx(
        progman,
        0,
        "SHELLDLL_DefView",
        None
    )

    # Em algumas versões do Windows,
    # o SHELLDLL_DefView está dentro de um WorkerW.
    if not shell_view:

        workerw = win32gui.FindWindowEx(
            0,
            0,
            "WorkerW",
            None
        )

        while workerw:

            shell_view = win32gui.FindWindowEx(
                workerw,
                0,
                "SHELLDLL_DefView",
                None
            )

            if shell_view:
                break

            workerw = win32gui.FindWindowEx(
                0,
                workerw,
                "WorkerW",
                None
            )

    if not shell_view:
        raise RuntimeError(
            "SHELLDLL_DefView não encontrado."
        )

    listview = win32gui.FindWindowEx(
        shell_view,
        0,
        "SysListView32",
        None
    )

    if not listview:
        raise RuntimeError(
            "SysListView32 não encontrado."
        )

    return listview


# ============================================================
# Abrir processo do Explorer
# ============================================================

def open_explorer_process(listview):
    """
    Descobre o processo responsável pelo SysListView32
    e abre o processo para leitura/escrita de memória.
    """

    _, process_id = win32process.GetWindowThreadProcessId(
        listview
    )

    access = (
        PROCESS_VM_OPERATION
        | PROCESS_VM_READ
        | PROCESS_VM_WRITE
    )

    process = OpenProcess(
        access,
        False,
        process_id
    )

    if not process:
        raise ctypes.WinError(
            ctypes.get_last_error()
        )

    return process, process_id


# ============================================================
# Memória remota
# ============================================================

def allocate_memory(process, size):
    """
    Reserva memória dentro do processo do Explorer.
    """

    address = VirtualAllocEx(
        process,
        None,
        size,
        MEM_COMMIT | MEM_RESERVE,
        PAGE_READWRITE
    )

    if not address:
        raise ctypes.WinError(
            ctypes.get_last_error()
        )

    return address


def free_memory(process, address):
    """
    Libera memória previamente reservada.
    """

    if address:
        VirtualFreeEx(
            process,
            address,
            0,
            MEM_RELEASE
        )


# ============================================================
# Ler nome do ícone
# ============================================================

def get_icon_name(
    listview,
    process,
    index
):
    """
    Obtém o texto/nome de um item do Desktop.
    """

    text_buffer_size = 512

    text_buffer = ctypes.create_unicode_buffer(
        text_buffer_size
    )

    item = LVITEMW()

    item.mask = LVIF_TEXT
    item.iItem = index
    item.iSubItem = 0
    item.pszText = 0
    item.cchTextMax = text_buffer_size

    item_size = ctypes.sizeof(item)

    remote_item = allocate_memory(
        process,
        item_size
    )

    remote_text = allocate_memory(
        process,
        ctypes.sizeof(text_buffer)
    )

    try:

        item.pszText = remote_text

        bytes_written = ctypes.c_size_t()

        success = WriteProcessMemory(
            process,
            remote_item,
            ctypes.byref(item),
            item_size,
            ctypes.byref(bytes_written)
        )

        if not success:
            raise ctypes.WinError(
                ctypes.get_last_error()
            )

        win32gui.SendMessage(
            listview,
            LVM_GETITEMTEXTW,
            index,
            remote_item
        )

        bytes_read = ctypes.c_size_t()

        success = ReadProcessMemory(
            process,
            remote_text,
            ctypes.byref(text_buffer),
            ctypes.sizeof(text_buffer),
            ctypes.byref(bytes_read)
        )

        if not success:
            raise ctypes.WinError(
                ctypes.get_last_error()
            )

        return text_buffer.value

    finally:

        free_memory(
            process,
            remote_text
        )

        free_memory(
            process,
            remote_item
        )


# ============================================================
# Ler posição do ícone
# ============================================================

def get_icon_position(
    listview,
    process,
    index
):
    """
    Obtém a posição X/Y de um item do Desktop.
    """

    point = POINT()

    point_size = ctypes.sizeof(point)

    remote_point = allocate_memory(
        process,
        point_size
    )

    try:

        # Inicializa a estrutura remota.
        bytes_written = ctypes.c_size_t()

        WriteProcessMemory(
            process,
            remote_point,
            ctypes.byref(point),
            point_size,
            ctypes.byref(bytes_written)
        )

        result = win32gui.SendMessage(
            listview,
            LVM_GETITEMPOSITION,
            index,
            remote_point
        )

        if not result:
            raise RuntimeError(
                f"Não foi possível obter a posição "
                f"do item {index}."
            )

        bytes_read = ctypes.c_size_t()

        success = ReadProcessMemory(
            process,
            remote_point,
            ctypes.byref(point),
            point_size,
            ctypes.byref(bytes_read)
        )

        if not success:
            raise ctypes.WinError(
                ctypes.get_last_error()
            )

        return point.x, point.y

    finally:

        free_memory(
            process,
            remote_point
        )


# ============================================================
# Obter todos os ícones
# ============================================================

def get_desktop_icons():

    listview = get_desktop_listview()

    print(
        f"SysListView32 encontrado: {listview}"
    )

    process, process_id = open_explorer_process(
        listview
    )

    print(
        f"Explorer encontrado. PID: {process_id}"
    )

    try:

        count = win32gui.SendMessage(
            listview,
            LVM_GETITEMCOUNT
        )

        print(
            f"Quantidade de itens: {count}"
        )

        icons = []

        for index in range(count):

            try:

                name = get_icon_name(
                    listview,
                    process,
                    index
                )

                x, y = get_icon_position(
                    listview,
                    process,
                    index
                )

                icon = {
                    "index": index,
                    "name": name,
                    "x": x,
                    "y": y
                }

                icons.append(icon)

            except Exception as error:

                print(
                    f"Erro no item {index}: {error}"
                )

        return icons

    finally:

        CloseHandle(process)

def set_icon_position(
    listview,
    index,
    x,
    y
):
    """
    Altera a posição de um ícone do Desktop.
    """

    position = (
        (y & 0xFFFF) << 16
    ) | (
        x & 0xFFFF
    )

    result = win32gui.SendMessage(
        listview,
        LVM_SETITEMPOSITION,
        index,
        position
    )

    return result
