import sys
from pathlib import Path

from PIL import Image

from src.make_shot import select_region
from src.structure import scan_n_structure


def main() -> None:
    if len(sys.argv) != 2:
        print("Error: only one path argument is required.", file=sys.stderr)
        sys.exit(1)
    
    path = Path(sys.argv[1])
    
    if not path.is_file():
        print(f"Warning: '{path}' is not a valid file. Falling back to screen capture.", file=sys.stderr)
        image = select_region()
    else:
        try:
            image = Image.open(path)
            image.load()
        except Exception as e:
            print(f"Error loading image: {e}. Falling back to screen capture.", file=sys.stderr)
            image = select_region()
    
    scan_n_structure(image)

if __name__ == '__main__':
    main()
    
if __name__ == "__main__":
    main()
