# OneBaronyACounty

## Motivation

Some Crusader Kings 3 mods like [AveMaria](https://github.com/alltheatreides/AVE_MARIA_CK3) removed barony by creating counties to have only one barony a county.

The goal of this tool is to automate this transformation to :

* Update mods to Paradox map edits
* Help to make mods editing the map and/or the history files compatible to mods merging baronies and counties

## Installation

* Download or clone this repository.
* Install python (for example with [miniconda](https://docs.conda.io/en/latest/miniconda.html)
I recommend you to install a Python environment with conda or virtualenv.

## Usage

```
python one_barony_one_county.py <path_to_source_landed_titles> <path_to_generated_landed_titles>
```

## Tests

You can run the tests (unittest) with VScode settings provided in the repository or with another way.

For example you can use the following commands:

```
cd tests
python -m unittest discover
```

## Future

In future, the history files will also be adapted to the county modifications.

## License

OneBaronyACounty is released under the [MIT License](http://www.opensource.org/licenses/MIT).
