import sys
from pathlib import Path

from PIL import Image

from src.make_shot import select_region
from src.structure import scan_n_structure


def main() -> None:
    image = select_region()
    if isinstance(image, Image):
        scan_n_structure(image)
    else:
        print('Sorry, was not able to scan image.')

    
if __name__ == "__main__":
    main()
