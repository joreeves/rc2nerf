# Reality Capture camera location to NERF conversion tool with per camera intrinsics
This tool is for use with https://github.com/NVlabs/instant-ngp and allows the use of Reality Capture camera locations.

## Installation
Copy rc2nerf.py file into instant-ngp\scripts folder

## Usage
Use Reality Capture to align cameras.

Export cameras alignment
```
Alignment -> Export -> Registration -> Internal/External camera parameters...
```

Save the CSV file exported from Reality Capture into the directory that contains your /images folder.

Open a shell (CMD, Powershell, Bash, etc.) and navigate to the directory with your XML file and /images folder:

cd [PATH TO FOLDER]

Run the rc2nerf.py on this CSV file using the following command, replacing the text in brackets […] with the file names and paths on your machine:

## Commands
Example:
```
python "[PATH TO iNGP]\rc2nerf.py" --csv_in "[NAME_OF_XML_FILE].xml" --imgfolder .\images
```
The quotes are only required if you have spaces in any of the folder or file names.

## Additional command examples
Scale the scene down by 0.01
```
python "[PATH TO iNGP]\rc2nerf.py" --csv_in "[NAME_OF_XML_FILE].xml" --imgfolder .\images --scale 0.01
```

Display the cameras in 3d and set the camera size (for debugging only, requires installing `matplotlib` and `pytransform3d`)
```
python "[PATH TO iNGP]\rc2nerf.py" --csv_in "[NAME_OF_XML_FILE].xml" --imgfolder .\images --plot --camera_size 1
```

Arguments:

| Argument               | Default Value   | Description                                  |
|------------------------|-----------------|----------------------------------------------|
| --csv_in               | None            | specify xml file location                    |
| --out                  | transforms.json | specify output file path                     |
| --imgfolder            | .\images        | location of image folder                     |
| --imgtype              | jpg             | ex.: jpg, png, ...                           |
| --aabb_scale           | 16              | sets the aabb scale                          |
| --no_scene_orientation | False           | disable the Reality Capture orientation      |
| --no_scale             | False           | disable the Reality Capture scale            |
| --no_center            | False           | disable the scene centering                  |
| --plot                 | False           | display the camera positions                 |
| --camera_size          | 0.1             | the size of the displayed cameras            |
| --debug_ignore_images  | False           | ignores the input images, for debugging only |
| --threads              | 8               | number of threads to use when reading images |
