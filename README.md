# TYCH Split

Process [Alfie TYCH](https://alfiecameras.com/) film images into individual half frames.

This script processes images from a [TYCH](https://alfiecameras.com/) camera, which exposes two half frames on each frame of 35mm film. The script splits the images into individual half frames. It also adds EXIF information (currently hard-coded in the code). It can also optionally generate a contact sheet for each roll of film / directory processed.

I wrote about my first use of the TYCH [here](https://andypiper.co.uk/2023/11/27/half-frame-photography/).

## Installation

This is a simple Python application. It requires Python 3.9 or later and a number of additional packages such as Pillow, piexif, numpy, OpenCV and reportlab. These can be installed using `pip`:

```bash
pip install -r requirements.txt
```

## Usage

Run the script with the following command:

```bash
python process-tych.py [input_dir]
```

The script will process all files in the input directory and output the results to a subdirectory called `processed`. The script will create the output directory if it does not already exist.

Pass the `--with-contact-sheet` option to generate a contact sheet for each roll of film. The contact sheet will be saved in the `processed` directory. The default is not to generate contact sheets, as this takes longer than processing the images.

> [!NOTE]
> There are a number of comments marked `TODO` and `FIXME` in the code. These are things I would like to improve in the future.

## Known Issues

> [!IMPORTANT]
>  In some cases, the attempt to split the images into half frames will fail. This may be because the image is too dark, or the half frames are not sufficiently distinct.

> [!IMPORTANT]
> The EXIF information - specifically author copyright - is hard-coded at the moment.

## License

MIT License. See `LICENSE` for more information.

### Acknowledgements

This script use Komika Axis font by Vigilante Typeface Corporation. See `LICENSE-KOMIKA.txt` for more information.

This script uses Open Sans font by Steve Matteson. See `LICENSE-OPEN-SANS.txt` for more information.

This code is not affiliated with [Alfie Cameras](https://alfiecameras.com/).
