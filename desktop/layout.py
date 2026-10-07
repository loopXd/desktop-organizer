import json
import os


LAYOUT_FOLDER = "layouts"


def ensure_layout_folder():
    """
    Garante que a pasta de layouts exista.
    """

    if not os.path.exists(LAYOUT_FOLDER):
        os.makedirs(LAYOUT_FOLDER)


def save_layout(
    name,
    icons
):
    """
    Salva a posição atual dos ícones
    como um layout.
    """

    ensure_layout_folder()

    layout = {
        "name": name,
        "items": {}
    }

    for icon in icons:

        layout["items"][icon["name"]] = {
            "x": icon["x"],
            "y": icon["y"]
        }

    filename = os.path.join(
        LAYOUT_FOLDER,
        f"{name}.json"
    )

    with open(
        filename,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            layout,
            file,
            indent=4,
            ensure_ascii=False
        )

    return filename


def load_layout(name):

    filename = os.path.join(
        LAYOUT_FOLDER,
        f"{name}.json"
    )

    if not os.path.exists(filename):

        raise FileNotFoundError(
            f"Layout '{name}' não encontrado."
        )

    with open(
        filename,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)