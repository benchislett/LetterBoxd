import ext.TWL06.twl as twl
import numpy as np
import random
import argparse

maxdepth = 5

try:
    import wordfreq
except ImportError:
    print('Failed to import wordfreq library. Solutions will be returned in arbitrary order.')
    wordfreq = None

def word_frequency(w, lang):
    if wordfreq is not None:
        return wordfreq.word_frequency(w, lang)
    else:
        return 0.0

def whereis(letter):
    for i in range(4):
        if letter in letters[i]:
            return i
    raise

def validate(word, pos=None):
    if word == '':
        return True, pos
    elif pos is not None:
        if word[0] in options[pos]:
            return validate(word[1:], whereis(word[0]))
    else:
        if word[0] in all:
            return validate(word[1:], whereis(word[0]))
    return False, pos

def simplify(lst):
    newlst = []
    for i in range(len(lst)):
        newword = True
        for j in range(len(lst)):
            if set(lst[i]) < set(lst[j]):
                newword = False
            elif set(lst[i]) == set(lst[j]) and i < j:
                newword = False
        if newword:
            newlst.append(lst[i])
    return newlst

def score(coll):
    return len((set(coll) - set([' '])).intersection(set(all)))

def solve_bfs(words=[], depth=0):
    opts = []
    if depth == 0:
        opts = starters
    else:
        for coll in words:
            opts.extend([coll + ' ' + word for word in connections[coll[-1]]])

    scores = list(map(score, opts))

    combo = sorted(zip(scores, opts), reverse=True)

    if combo[0][0] == 12 or depth + 1 == maxdepth:
        return combo
    else:
        return solve_bfs(opts, depth + 1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                    prog='LetterBoxedSolver',
                    description='Computes optimal solutions for the NYT Word Game "Letterboxed"')
    parser.add_argument('letters', type=str, nargs='?',
                    help='A pattern of letters, optionally with dashes separating the sides of the box. For example ABC-DEF-GHI-JKL. If omitted, a random pattern is generated.')
    args = parser.parse_args()

    global letters, all, options, validwords, connections, starters

    letters = args.letters
    if letters is None:
        all = ''.join(random.sample('abcdefghijklmnopqrstuvwxyz', 12))
        letters = all
    letters = letters.replace('-', ' ')
    letters = letters.replace('|', ' ')
    letters = letters.replace('/', ' ')
    all = letters.replace(' ', '')
    if ' ' not in letters:
        letters = [letters[0:3], letters[3:6], letters[6:9], letters[9:12]]
    else:
        letters = letters.split(' ')

    print(' '.join(letters).upper(), '\n')

    # letters: a list of four strings, each with the 3 letters per side. Example: ['abc', 'def', 'ghi', 'jkl']
    # all: a string of all available letters. Example: 'abcdefghijkl'
    
    options = [''.join([a for a in letters if a != b]) for b in letters]

    # options: inverse of 'letters', with the connecting letters from each side. Example: ['defghijkl', 'abcghijkl', 'abcdefjkl', 'defghijkl']

    results = list(filter(lambda x: x[0], [(*validate(word), word) for word in twl.iterator() if len(word) > 2]))
    endpositions = list(map(lambda x: x[1], results))
    validwords = list(map(lambda x: x[2], results))

    starters = simplify(validwords)

    if len(starters) == 0:
        raise ValueError("No words possible!")

    connections = {}
    for letter in all:
        connections[letter] = list(filter(lambda word: word[0] == letter, validwords))
        connections[letter] = simplify(connections[letter])

    res = solve_bfs()
    if res[0][0] != 12:
        print('Score insufficient. Best: ', res[0])
    else:
        res = list(filter(lambda i: i[0] == 12, res))
        scores = list(map(lambda s: min(map(lambda w: word_frequency(w, 'en'), s[1].strip().split(' '))), res))
        combo = sorted(zip(scores, res), reverse=True)
        for freq_score, (depth_score, coll) in combo[:10]:
            print(coll.strip())
