from tkinter import Tk


def set_window_position(tk: Tk, width: int = 600, height: int = 600, position: str = "center") -> str:
    """
        Takes:
            required Tk() instance to retrieve screen size:
                _tk: <tk.Tk>

            optional tk window size parameters:
                width: int = 600 by default
                height: int = 600 by default

            optional screen position:
                position: str = 'center' by default:
                    use "center", "top", "bottom", "left", "right" or
                    any 2 combination("left top"): X val then Y val

                    use 'POSITIVE' int values for precise positioning:
                        position = "{x_pos}x{y_pos}" or "{x_pos} {y_pos}"
                        negative values return an exception

                    mix and match: "center 200" or "100xbottom"

        Returns:
            tk.geometry string value
    """
    sw = tk.winfo_screenwidth()
    sh = tk.winfo_screenheight()
    position = position if position else "center"
    positions = {
        'center_x': (sw // 2) - (width // 2),
        'right_x': sw - width,
        'left_x': 0,
        'center_y': (sh // 2) - (height // 2),
        'top_y': 0,
        'bottom_y': sh - height
    }
    x = positions['center_x'] if position == "center" else None
    y = positions['center_y'] if position == "center" else None
    if x and y:
        return f"{width}x{height}+{x}+{y}"
    pos = position.split("x" if "x" in position else " ")
    if not pos[0]:
        x = positions['center_x']
    else:
        if pos[0].isdigit():
            x = pos[0]
        else:
            x = positions.get(f"{pos[0]}_x")
    if pos[1]:
        if pos[1].isdigit():
            y = pos[1]
        else:
            y = positions.get(f"{pos[1]}_y")
    else:
        y = positions['center_y']
    if int(x) >= 0 and int(y) >= 0:
        return f"{width}x{height}+{x}+{y}"
    else:
        raise ValueError("Invalid position -> use: center, top, bottom, left, right, top center, top left etc...")
