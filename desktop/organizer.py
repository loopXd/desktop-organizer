from utils.logger import info
from desktop.icons import (
    get_desktop_listview,
    set_icon_position
)


class DesktopOrganizer:

    def __init__(
        self,
        layout,
        dry_run=True
    ):
        self.layout = layout
        self.dry_run = dry_run

    def organize(self, icons):

        info("Iniciando organização...")

        listview = None

        if not self.dry_run:
            listview = get_desktop_listview()

        for icon in icons:

            name = icon["name"]

            if name not in self.layout:

                info(
                    f"Ignorando: {name}"
                )

                continue

            target = self.layout[name]

            current_x = icon["x"]
            current_y = icon["y"]

            target_x = target["x"]
            target_y = target["y"]

            # Já está no lugar
            if (
                current_x == target_x
                and current_y == target_y
            ):

                info(
                    f"{name} já está no lugar."
                )

                continue

            # Mostra a alteração
            info(
                f"{name}: "
                f"({current_x}, {current_y}) "
                f"→ "
                f"({target_x}, {target_y})"
            )

            # DRY RUN
            if self.dry_run:

                info(
                    f"[DRY RUN] "
                    f"{name} não foi movido."
                )

                continue

            # Movimento real
            set_icon_position(
                listview,
                icon["index"],
                target_x,
                target_y
            )

            info(
                f"{name} movido com sucesso."
            )