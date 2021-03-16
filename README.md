# MTG Curve

MTG Curve helps Magic: the Gathering players estimate the amount of
mana they will have on a specific turn. It is primarily geared towards
EDH/Commander players, but will hopefully be generic enough to support
other formats in the future.

## Installation

While the project is very early in the development cycle, it will be
submitted on Pypi once it is a tad more stable. In the meantime,
clone the repository and install locally:
```
git clone https://github.com/ihowell/mtgcurve
cd mtgcurve
pip install -e .
```

## Usage

First, host your deck on Moxfield (text input coming soon TM). Then
copy the url of the deck and run:
```
python -m mtgcurve https://www.moxfield.com/decks/IlUDC5c-MUejd0psQ6HNoA
```

replacing the above url with your own. It may take some time to run,
as more mana producing cards and higher max turn parameters will
provide exponential effects to runtime. To modify the maximum CMC to
play on curve, modify the `--max_turn` parameter.

## Method

This estimator works by performing a tree search and assigning
probability from each starting hand. Each starting hand has a number
of land cards, mana producing card (i.e. dorks or mana rocks), and
then other cards. Given a starting hand, the following gives the
probability of any specific hand:
![equation](http://www.sciweavers.org/tex2img.php?eq=%5Ccfrac%7B%7Blands_%7Blibrary%7D%5Cchoose%20lands_%7Bhand%7D%7Dprod_h%21%7Bcards_%7Blibrary%7D-lands_%7Blibrary%7D-prod_%7Blibrary%7D%5Cchoose%207-lands_%7Bhand%7D-prod_%7Bhand%7D%7D%7D%7B%7Bcards_%7Blibrary%7D%5Cchoose%207%7D%7D&bc=White&fc=Black&im=png&fs=24&ff=txfonts&edit=0)

After an initial hand is generated, a tree search is performed to
account for the probabilities that could come from that specific
hand. When the search tree has finished, it moves on to the next hand.

### Assumptions

There are a few assumptions that are made to make this project possible:
1. All lands are basic. Currently, all lands are assumed to be basic
   lands. While future versions may allow for tapped lands, this
   assumption feels fine and is close to how the on-curve estimator of
   Moxfield functions.
2. All mana costs are generic. Future iterations could support
   specific casting costs, however it is too expensive for the time
   being.
3. Every turn, we try to make the mana-optimal play. That is, every
   card we play is a mana producer. This tool does not take into
   account holding mana open for counterspells or any other
   reasons. That being said, the 'mana-optimal' play would require
   more search and would depend on which CMC was most
   important. Future versions may include other heuristics like this
   and if you would like to contribute one, please look into
   submitting a pull request.
4. Enchantments like Wild Growth and Utopia Sprawl take a turn to
   activate. This will be fixed in a future iteration that will check
   the number of lands in play when these are cast.
