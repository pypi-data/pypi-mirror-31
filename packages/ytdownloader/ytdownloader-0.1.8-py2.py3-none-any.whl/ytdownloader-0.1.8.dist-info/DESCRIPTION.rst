
# YoutubeDownloader

**YoutubeDownloader** is an automated service to download multiple youtube videos at a one time.

## About

**YoutubeDownloader** is written in `Python`. It uses ``Python Multiprocessing`` at its heart which facilitates user to download more than one video at a time.


**YoutubeDownloader** supports a YAML / JSON format configuration file. This configuration file gives more structure and usability to the package. It defines what **videos/playlists** needs to be downloaded and how they are going to be stored.


## Configuration Syntax

**YoutubeDownloader** supports YAML / JSON configuration formats. Below is the snippet of sample configurations in YAML / JSON format.


```
settings:
  process: 2
download:
  mostlyinsane:
    dirname: 'mostlyinsane'
    videos: 
      - 'https://www.youtube.com/watch?v=vcKPjDUc5EQ'
  trippling:
    dirname: 'trippling'
    playlist: 'https://www.youtube.com/watch?list=PLTB0eCoUXEraZe3d7fJRdB-znE5D0cMZ7'
```

```
{
	"settings": {
		"process": 5
	},
	"download": {
		"mostlyinsane": {
			"dirname": "mostlyinsane",
			"videos": [
				"https://www.youtube.com/watch?v=vcKPjDUc5EQ"
			]

		},
		"trippling": {
			"dirname": "trippling",
			"playlist": "https://www.youtube.com/watch?list=PLTB0eCoUXEraZe3d7fJRdB-znE5D0cMZ7"

		}
	}
}
```

`settings` defines package level variables. 
- `process` to force **YoutubeDownloader** to use `Python Multiprocessing` and tells how many processes should be deployed to download videos at a time.

`download` defines what **videos/playlists** to download. It tags **dirnames** with **videos/playlists** internally and store the downloaded **videos/playlists** in the respective **directory**.

- `dirname` **relative / absolute directory path** to store videos in.
- `videos` **single / array of youtube videos link** to download
- `playlist` **single / array of youtube playlist link** to download


## Install

This is a pure-Python package built for Python 2.6+ and Python 3.0+. To set up:

```
    sudo pip install ytdownloader
```

## Options

```
    ytdownloader --help
```

- `configuration` specifies the location for the configuration file to **YoutubeDownloader**. If it omits, **YoutubeDownloader** looks in the current directory for the configuration file.
- `version` specifies the currect version of **YoutubeDownloader**.

