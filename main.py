import json
import sys

from desktop.icons import get_desktop_icons
from desktop.organizer import DesktopOrganizer
from desktop.layout import (
    save_layout,
    load_layout
)


def load_config():

    with open(
        "config.json",
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def save_current_layout(name):

    print()
    print("=" * 50)
    print("SALVANDO LAYOUT")
    print("=" * 50)

    icons = get_desktop_icons()

    filename = save_layout(
        name,
        icons
    )

    print()
    print(f"Layout salvo com sucesso:")
    print(filename)

    print()
    print(f"{len(icons)} itens salvos.")


def organize_layout(name):

    print()
    print("=" * 50)
    print("ORGANIZANDO DESKTOP")
    print("=" * 50)

    layout = load_layout(name)

    icons = get_desktop_icons()

    organizer = DesktopOrganizer(
        layout=layout["items"],
        dry_run=False
    )

    organizer.organize(
        icons
    )


def show_help():

    print()
    print("=" * 50)
    print("DESKTOP ORGANIZER")
    print("=" * 50)

    print()
    print("Comandos:")
    print()

    print(
        "  python main.py save <nome>"
    )

    print(
        "      Salva a posição atual."
    )

    print()

    print(
        "  python main.py organize <nome>"
    )

    print(
        "      Organiza usando um layout salvo."
    )

    print()

    print(
        "  python main.py"
    )

    print(
        "      Mostra informações do Desktop."
    )

    print()


def main():

    args = sys.argv

    if len(args) == 1:

        config = load_config()

        print("=" * 50)
        print("       DESKTOP ORGANIZER - MVP 1.5")
        print("=" * 50)

        print()

        icons = get_desktop_icons()

        print()
        print("ÍCONES ENCONTRADOS:")
        print()

        for icon in icons:

            print(
                f"[{icon['index']:02}] "
                f"{icon['name']:<30} "
                f"X={icon['x']:<5} "
                f"Y={icon['y']:<5}"
            )

        return

    command = args[1].lower()

    if command == "save":

        if len(args) < 3:

            print(
                "Informe o nome do layout."
            )

            print(
                "Exemplo:"
            )

            print(
                "python main.py save trabalho"
            )

            return

        name = args[2]

        save_current_layout(
            name
        )

        return

    if command == "organize":

        if len(args) < 3:

            print(
                "Informe o nome do layout."
            )

            return

        name = args[2]

        organize_layout(
            name
        )

        return

    show_help()


if __name__ == "__main__":
    main()