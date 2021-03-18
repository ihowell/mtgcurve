# Azusa
[![Python](https://img.shields.io/pypi/pyversions/azusa.svg)](https://badge.fury.io/py/azusa)
[![PyPI](https://img.shields.io/pypi/v/azusa.svg)](https://badge.fury.io/py/azusa)
[![Status](https://img.shields.io/pypi/status/azusa.svg)](https://badge.fury.io/py/azusa)
[![License](https://img.shields.io/pypi/l/azusa.svg)](https://badge.fury.io/py/azusa)

MTG Curve helps Magic: the Gathering players estimate the amount of mana they will have on a specific turn. It is primarily geared towards EDH/Commander players, but will hopefully be generic enough to support other formats in the future.

## Installation

We are on Pypi, so all you have to do is:
```
pip install azusa
```

## Usage

First, host your deck on Moxfield (text input coming soon TM). Then copy the url of the deck and run:
```
python -m azusa https://www.moxfield.com/decks/IlUDC5c-MUejd0psQ6HNoA
```

replacing the above url with your own. It may take some time to run, as more mana producing cards and higher max turn parameters will provide exponential effects to runtime. To modify the maximum CMC to play on curve, modify the `--max_turn` parameter.

## Vocabulary

The explanations in this document assume familiarity with Magic the Gathering terms. In addition to these terms, we describe two additional terms:
1. A *mana producer*, or *producer*, ramps the player by at least one mana in some way. This includes mana rocks, mana dorks, land fetch effects (like Rampant Growth, not actual fetch lands), etc.
2. Cards that are not lands nor producers are termed as *other*.

## Method

This estimator works by performing a tree search and assigning probability from each starting hand. Each starting hand has a number of land cards, mana producing card (i.e. dorks or mana rocks), and then other cards. Given a starting hand, the following gives the probability of any specific hand:
<img src="https://render.githubusercontent.com/render/math?math={{\left|lands_{library}\right|}\choose {\left|lands_{hand}\right|}}{{\left|other_{library}\right|}\choose {\left|other_{hand}\right|}} / {{\left|cards_{library}\right|} \choose 7}">.

After an initial hand is generated, a tree search is performed to account for the probabilities that come from drawing cards at the beginning of a turn. Turn actions are performed according to a heuristic. When the search tree has finished, it moves on to the next hand. This process has further been multi-threaded allowing multiple hands to be considered at a time.

### Complexity

This package performs a tree search per hand, which is bounded by <img src="https://render.githubusercontent.com/render/math?math=O((\left|producers\right| %2B 2)^{turns})"> time, so be careful in defining the maximum number of turns and realize that the more producers included in the decklist, the longer this method will take. Further, the number of starting hands is: <img src="https://render.githubusercontent.com/render/math?math=\sum_{i=0}^7\sum_{j=0}^{7-i}{{\left|producers\right|} \choose j}\in O(|producers|^7)">, so be careful of running with a high number of turns and mana producers. This bound will be lowered in practice when equivalent mana producers are grouped, e.g. Llanowar Elves and Fyndhorn Elves.

### Assumptions

There are a few assumptions that are made to make this project possible:
1. All lands are basic. Currently, all lands are assumed to be basic lands. While future versions may allow for tapped lands, this assumption feels fine and is close to how the on-curve estimator of Moxfield functions.
2. All mana costs are generic. Future iterations could support specific casting costs, however it is too expensive for the time being.
3. Every turn, we try to make the mana-optimal play. That is, every card we play is a mana producer. This tool does not take into account holding mana open for counterspells or any other reasons. That being said, the 'mana-optimal' play would require more search and would depend on which CMC was most important. Future versions may include other heuristics like this and if you would like to contribute one, please look submitting a pull request.
4. Enchantments like Wild Growth and Utopia Sprawl take a turn to activate. This will be fixed in a future iteration that will check the number of lands in play when these are cast.

## Contributions

Contributions are heavily encouraged! Even if you don't have much experience with Python, there is a lot of work to be done on this project. If you have any suggestions or contributions, please go ahead and open a Github Issue or submit a Pull Request.

## Appendix A: Probability of each starting hand

Suppose we have a library with c cards at the beginning of the game. For a commander deck with one commander, c would be 99. Let us suppose that there are n lands in the deck, s mana producers, and u other cards. We can formulate the total number of possible opening hands without mulligaining as: <img src="https://render.githubusercontent.com/render/math?math={c \choose 7}={{n %2B s %2B u} \choose 7}">

This can be expanded using [Vandermonde's Identity](https://en.wikipedia.org/wiki/Vandermonde%27s_identity) to first break up the lands from the rest of the library:
<img src="https://render.githubusercontent.com/render/math?math={c \choose 7}={{n %2B s %2B u} \choose 7}=\sum_{i=0}^7{n\choose i}{{s %2B u}\choose {7-i}}">

Then, we can break apart the mana producers from the other cards in the library:
<img src="https://render.githubusercontent.com/render/math?math=\sum_{i=0}^7{n\choose i}{{s %2B u}\choose 7-i}=\sum_{i=0}^7\sum_{j=0}^{7-i}{n\choose i}{s\choose j}{u\choose {7-i-j}}">

Finally, if we consider each possible combination of mana producers separately, we can assign each starting hand with <img src="https://render.githubusercontent.com/render/math?math={n\choose i}{u\choose {7-i-j}}"> equivalent combinations. Therefore, the probability of each drawing each starting hand is:<img src="https://render.githubusercontent.com/render/math?math={n\choose i}{u\choose {7-i-j}} / {c \choose 7}">

## Appendix B: Performing probability calculations

There is an issue with calculating the probability of a starting hand:
<img src="https://render.githubusercontent.com/render/math?math={n\choose i}{u\choose {7-i-j}} / {c \choose 7}">.
The issue is that each term of the expression can, and does, grow to be quite large. To solve this problem, we perform most of the calculations in log space:
<img src="https://render.githubusercontent.com/render/math?math=\log\left({n\choose i}{u\choose {7-i-j}} / {c \choose 7}\right)=\log{n\choose i} %2B \log{u\choose {7-i-j}}-\log{c \choose 7}">
This reduces large multiplications and divisions to simple arithmatic once the log of each term has been calculated.
