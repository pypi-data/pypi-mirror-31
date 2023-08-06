# PLDAC-Galaxies
**galaxies** est un logiciel permettant une visualisation graphique ainsi qu'une interaction avec un réseau d'agrégats de réutilisations.
Il est développé en **Python 3.5** et utilise les bases de données générées par <a href="https://github.com/ARTFL-Project/text-align">text-align</a>.


## Installation
**galaxies** is available under <a href="https://pypi.python.org/pypi/galaxies">PyPI</a>, the official disributor for Python packages.
Just type :
```shell
$ pip install galaxies
```
in a `shell` to install this software. Then the package create **2** new commands :
```shell
$ galaxies
$ galaxies_gui
```


## Usage
### GUI
The GUI's usage is pretty straightforward. The main menu has two

## Requirements
* This software can be used with **Python 3.5** or a greater version. It shouldn't work with any anterior version because the source code uses `type hint`, introduced with Python 3.5.
* The graphical interface needs <a href="https://graph-tool.skewed.de/">**graph-tool**</a> for plotting and interacting with graphs.
* The window system used is **GTK**, the default system for the **Gnome** distribution. Your machine needs GTK or <a href="http://www.pygtk.org/downloads.html">**pyGTK**</a> for the GUI of this software.


## Dependencies
* click >= 6.7
* progressbar33 >= 2.4


## Todo


## Many thanks
We would like to thanks our teacher <a href="http://www-poleia.lip6.fr/~ganascia">JG. Ganascia</a> from <a href="https://www.lip6.fr/">LIP6 laboratory</a> for his supervision and his help through our production of the entire software.


## License
The project is delivered under the GPL3 license. Read the [LICENSE.txt](LICENSE.txt) file for more details.


## References
* Ganascia J.-G., Glaudes P., Del Lungo A., "Automatic detection of reuses and citations in literary texts", Literary and Linguistic Computing, 2014, doi: 10.1093/llc/fqu020
* Blondel, Vincent D; Guillaume, Jean-Loup; Lambiotte, Renaud; Lefebvre, Etienne (9 October 2008). "Fast unfolding of communities in large networks". Journal of Statistical Mechanics: Theory and Experiment. 2008 (10): P10008. doi:10.1088/1742-5468/2008/10/P10008
* RFC 4180: Common Format and MIME Type for Comma-Separated Values (CSV) Files Vol. 2007, No. 02/04. (2005) by Y. Shafranovich
