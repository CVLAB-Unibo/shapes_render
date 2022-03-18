from pathlib import Path

from PIL import Image


def load_and_crop(
    path_image: str, margin_left: int, margin_right: int, margin_bottom: int, margin_top: int
) -> Image.Image:
    """Load one image and crop it.

    Args:
        path_image: the path to the image to load.
        margin_left: the number of pixels to select on the left starting from the center of the image.
        margin_right: the number of pixels to select on the right starting from the center of the image.
        margin_bottom: the number of pixels to select on bottom starting from the center of the image.
        margin_top: the number of pixels to select on top starting from the center of the image.

    Returns:
        The cropped image.
    """
    image = Image.open(path_image)

    w, h = image.size
    center_image_w = w // 2
    center_image_h = h // 2

    left = center_image_w - margin_left
    top = center_image_h - margin_top
    right = center_image_w + margin_right
    bottom = center_image_h + margin_bottom

    image_cropped = image.crop((left, top, right, bottom))
    return image_cropped


def main():

    path_image = Path("/home/rspezialetti/mlpio/rec_voxels_renders/00/17647_gt.png")
    dir_cropped = Path("/home/rspezialetti/mlpio/reconstruction_voxels_renders_cropped/")
    dir_cropped.mkdir(exist_ok=True)

    image_cropped = load_and_crop(
        str(path_image), margin_left=140, margin_right=180, margin_bottom=140, margin_top=130
    )
    image_cropped.show()
    image_cropped.save(dir_cropped / f"{path_image.stem}.png")


if __name__ == "__main__":
    main()
