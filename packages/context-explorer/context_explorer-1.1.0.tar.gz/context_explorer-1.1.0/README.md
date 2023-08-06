Thanks for stopping by! `（ ^_^）o自自o（^_^ ）`

# ContextExplorer

ContextExplorer facilitates analyses and visualization of data extracted from
microscope images of cells.

## Relevance

The analyses methods in ContextExplorer focuses on how populations of cells are
affected by their microenvironment, including local variations in cell
signalling and cell density. It is currently difficult for scientists without
previous programming experience to quantify these variables, although it is
relevant for many research areas. Facilitating this type of analyses can help
scientists around the world to improve their understanding of cellular behavior
and accelerate their research.

## Overview

![Workflow overview](doc/img/fig1-overview.png)

ContextExplorer is controlled via a graphical user interface and aims to enable
powerful analysis and visualizations of single cell data extracted from
microscope images for a broad scientific audience. ContextExplorer can
work in tandem with many other tools since it only depends on a correctly
formatted CSV-file as input and only outputs commonly used file formats (`.csv`,
`.jpg`, `.png`, and `.pdf`)


## Installation

ContextExplorer can be installed via the package managers `conda` or `pip`. The
recommended way is to use `conda`:

1. Download and install the [Anaconda Python
   distribution](https://www.anaconda.com/download/) (version 3.x). This is an
   easy way to install Python and gives access to the powerful package manager
   `conda`.
2. If you are using Windows, open up the `Anaconda Prompt` from the start menu.
   On MacOS and Linux you can use your default terminal (e.g. `terminal.app` on
   MacOS).
3. Type `conda install -c joelostblom context_explorer` and press return.

## Using ContextExplorer

If you are new to ContextExplorer, first download [the sample
data](https://gitlab.com/stemcellbioengineering/context-explorer/raw/master/sample-data/ce-sample.csv)
(right click link -> Save as). Launch ContextExplorer by typing
`context_explorer` in the terminal/`Anaconda Prompt`, then choose the sample file
(or your own data) from the file selector. That's all you need to start testing
ContextExplorer!

Detailed documentation and workflow examples are available at the [documentation
page](http://contextexplorer.readthedocs.io/en/latest/).

## Support

If you run into troubles, please [check the issue
list](https://gitlab.com/stemcellbioengineering/context-explorer/issues) to see
if your problem has already been reported. If not, open a new issue or [ask for
help in the gitter chat](https://gitter.im/context_explorer/Lobby).

## Contributions

Feedback and suggestions are always welcome! This does not have to be
code-related, don't be shy =) Please read [the contributing
guidelines](https://gitlab.com/joelostblom/context-explorer/blob/master/CONTRIBUTING.md)
to get started.

## Roadmap

An overview of the projects direction is available in [the project
wiki](https://gitlab.com/stemcellbioengineering/context-explorer/wikis/Roadmap).

## Code of conduct

Be welcoming, friendly, and patient; be direct and respectful; understand and
learn from disagreement and different perspectives; lead by example; ask for
help when unsure; give people the benefit of the doubt; a simple apology can go
a long way; be considerate in the words that you choose. Detailed descriptions
of these points can be found in
[`CODE_OF_CONDUCT.md`](https://gitlab.com/stemcellbioengineering/context-explorer/blob/master/CODE_OF_CONDUCT.md).
