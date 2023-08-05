# PLDAC-Galaxies
**galaxies** est un logiciel permettant une visualisation graphique ainsi qu'une interaction avec un réseau d'agrégats de réutilisations. Il est développé en **Python 3.5** et utilise les bases de données générées par <a href="https://github.com/ARTFL-Project/text-align">text-align</a>.


## Installation
**galaxies** est disponible depuis le dépôt <a href="https://pypi.python.org/pypi/fforest">PyPI</a>, il vous suffit juste de lancer :
```shell
$ pip install galaxies
```
dans un `shell` pour installer le logiciel. Le package installé met alors à disposition **2** commandes :
```shell
$ galaxies
$ galaxies_gui
```


## Utilisation


## Requirements
* Ce logiciel peut être utilisé avec **Python 3.5** ou une version supérieure. Il ne devrait pas marcher avec une version antèrieure de Python car le code utilise des `type hint`, introduit avec Python 3.5.
* L'interface graphique nécessite <a href="https://graph-tool.skewed.de/">**graph-tool**</a> pour pouvoir fonctionner.


## Dependencies
* click >= 6.7
* progressbar33 >= 2.4


## Todo


## Remerciements
Nous voudrions remercier le professeur <a href="http://www-poleia.lip6.fr/~ganascia">JG. Ganascia</a> du <a href="https://www.lip6.fr/">laboratoire du LIP6</a> pour nous avoir supervisé durant la conception de ce logiciel.


## License
The projet est délivré sous la licence TODO. Voir le fichier [LICENSE.txt](LICENSE.txt) pour plus d'explications.


## References
* Ganascia J.-G., Glaudes P., Del Lungo A., "Automatic detection of reuses and citations in literary texts", Literary and Linguistic Computing, 2014, doi: 10.1093/llc/fqu020
* Blondel, Vincent D; Guillaume, Jean-Loup; Lambiotte, Renaud; Lefebvre, Etienne (9 October 2008). "Fast unfolding of communities in large networks". Journal of Statistical Mechanics: Theory and Experiment. 2008 (10): P10008. doi:10.1088/1742-5468/2008/10/P10008
* RFC 4180: Common Format and MIME Type for Comma-Separated Values (CSV) Files Vol. 2007, No. 02/04. (2005) by Y. Shafranovich


