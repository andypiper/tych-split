# TYCH Split

Process [Alfie TYCH](https://alfiecameras.com/) film images into individual half frames.

This script processes images from a [TYCH](https://alfiecameras.com/) camera, which exposes two half frames on each frame of 35mm film. The script splits the images into individual half frames. It can also optionally generate a contact sheet for each roll of film / directory processed.

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

## License

MIT License. See `LICENSE` for more information.

### Acknowledgements

This script use Komika Axis font by Vigilante Typeface Corporation. See `LICENSE-KOMIKA.txt` for more information.

This script uses Open Sans font by Steve Matteson. See `LICENSE-OPEN-SANS.txt` for more information.

The script is not affiliated with [Alfie Cameras](https://alfiecameras.com/).
