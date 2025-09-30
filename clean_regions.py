import os
import re
from pathlib import Path


def mca_coords(filename):
    """Return (rx, rz) for r.x.z.mca files"""
    m = re.match(r"r\.(-?\d+)\.(-?\d+)\.mca$", filename)
    return (int(m.group(1)), int(m.group(2))) if m else None


def mcc_coords(filename):
    """Return (cx, cz) for c.x.z.mcc files"""
    m = re.match(r"c\.(-?\d+)\.(-?\d+)\.mcc$", filename)
    return (int(m.group(1)), int(m.group(2))) if m else None


def region_bounds(rx, rz):
    """Return x, z limits of a region file in blocks"""
    return (
        rx * 512, (rx + 1) * 512 - 1,
        rz * 512, (rz + 1) * 512 - 1
    )

  
def chunk_bounds(cx, cz):
    """Return x, z limits of a chunk file in blocks"""
    return (
        cx * 16, (cx + 1) * 16 - 1,
        cz * 16, (cz + 1) * 16 - 1
    )
  

def within_border(minx, maxx, minz, maxz, center_x, center_z, diameter):
    """Test if within world border"""
    half = diameter // 2
    border_min_x = center_x - half
    border_max_x = center_x + half - 1
    border_min_z = center_z - half
    border_max_z = center_z + half - 1

    return not (maxx < border_min_x or minx > border_max_x or
                maxz < border_min_z or minz > border_max_z)


def mca_within_border(rx, rz, center_x, center_z, diameter):
    return within_border(*region_bounds(rx, rz), center_x, center_z, diameter)


def mcc_within_border(cx, cz, center_x, center_z, diameter):
    return within_border(*chunk_bounds(cx, cz), center_x, center_z, diameter)


def find_files(directories, center_x, center_z, diameter):
    to_delete = []
    for d in directories:
        path = Path(d)
        if not path.exists():
            continue
        for file in path.glob("*"):
            if file.suffix == ".mca":
                coords = mca_coords(file.name)
                if coords and not mca_within_border(*coords, center_x, center_z, diameter):
                    to_delete.append((file, region_bounds(*coords)))
            elif file.suffix == ".mcc":
                coords = mcc_coords(file.name)
                if coords and not mcc_within_border(*coords, center_x, center_z, diameter):
                    to_delete.append((file, chunk_bounds(*coords)))
    return to_delete


def format_table(files_to_delete, center_x, center_z, diameter):
    """Create a table with coordinates that are out of border shown in red"""
    half = diameter // 2
    border_min_x = center_x - half
    border_max_x = center_x + half - 1
    border_min_z = center_z - half
    border_max_z = center_z + half - 1

    # Max column width, without color
    file_width = max(len(str(f)) for f, _ in files_to_delete)
    minx_width = max(len(str(minx)) for _, (minx, _, _, _) in files_to_delete)
    maxx_width = max(len(str(maxx)) for _, (_, maxx, _, _) in files_to_delete)
    minz_width = max(len(str(minz)) for _, (_, _, minz, _) in files_to_delete)
    maxz_width = max(len(str(maxz)) for _, (_, _, _, maxz) in files_to_delete)

    header = (
        f"| {'fichier'.ljust(file_width)}"
        f" | {'min X'.rjust(minx_width)} | {'max X'.rjust(maxx_width)}"
        f" | {'min Z'.rjust(minz_width)} | {'max Z'.rjust(maxz_width)} |"
    )
    sep = (
        f"|{'-' * (file_width + 2)}"
        f"|{'-' * (minx_width + 2)}|{'-' * (maxx_width + 2)}"
        f"|{'-' * (minz_width + 2)}|{'-' * (maxz_width + 2)}|"
    )

    # Add color
    def color_if_out(val, min_border, max_border):
        return f"\033[31m{val}\033[0m" if val < min_border or val > max_border else str(val)

    lines = [header, sep]
    for f, (minx, maxx, minz, maxz) in files_to_delete:
        lines.append(
            f"| {str(f).ljust(file_width)}"
            f" | {color_if_out(minx, border_min_x, border_max_x).rjust(minx_width + 9 if '\033' in color_if_out(minx, border_min_x, border_max_x) else minx_width)}"
            f" | {color_if_out(maxx, border_min_x, border_max_x).rjust(maxx_width + 9 if '\033' in color_if_out(maxx, border_min_x, border_max_x) else maxx_width)}"
            f" | {color_if_out(minz, border_min_z, border_max_z).rjust(minz_width + 9 if '\033' in color_if_out(minz, border_min_z, border_max_z) else minz_width)}"
            f" | {color_if_out(maxz, border_min_z, border_max_z).rjust(maxz_width + 9 if '\033' in color_if_out(maxz, border_min_z, border_max_z) else maxz_width)} |"
        )

    return "\n".join(lines)


def main():
    center_x = int(input("Worldborder center, X: "))
    center_z = int(input("Worldborder center, Z: "))
    diameter = int(input("Worldborder diameter: "))

    dirs = ["region", "entities", "poi"]
    files_to_delete = find_files(dirs, center_x, center_z, diameter)

    if not files_to_delete:
        print("No file to delete.")
        return

    print("\nFiles to delete:")
    print(format_table(files_to_delete, center_x, center_z, diameter))

    confirm = input("\nConfirm deletion? (o/N) ").lower()
    if confirm != "o":
        print("Operation canceled.")
        return

    for f, _ in files_to_delete:
        os.remove(f)
    print(f"\nFinished. {len(files_to_delete)} files deleted.")

if __name__ == "__main__":
    main()
