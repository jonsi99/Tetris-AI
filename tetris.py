import numpy as np
import random as rd
import json
import argparse
import os

HEIGHT = 20
WIDTH = 10
PAD = 3

piecelist = [
    1 * np.array([[0,0,0,0],[1,1,1,1],[0,0,0,0],[0,0,0,0]], dtype=np.int8),
    2 * np.array([[1,0,0],[1,1,1],[0,0,0]], dtype=np.int8),
    3 * np.array([[0,0,1],[1,1,1],[0,0,0]], dtype=np.int8),
    4 * np.array([[1,1],[1,1]], dtype=np.int8),
    5 * np.array([[0,1,1],[1,1,0],[0,0,0]], dtype=np.int8),
    6 * np.array([[0,1,0],[1,1,1],[0,0,0]], dtype=np.int8),
    7 * np.array([[1,1,0],[0,1,1],[0,0,0]], dtype=np.int8)
]

icon = {
    0: '▄▄▄▄', 1: '█▄▄ ', 2: '▄▄█ ', 3: ' ██ ',
    4: '▄█▀ ', 5: '▄█▄ ', 6: '▀█▄ ', -1: '    '
}

dic = {'<':'left', '>':'right', '^':'rotate', 'c':'hold'}

class ANSI:
    
    def __init__(self):
        os.system('')
        color = [
            '31;31;31m',    '0;255;255m',
            '0;0;255m',     '255;127;0m',
            '255;255;0m',   '0;255;0m',
            '255;0;255m',   '255;0;0m'
        ]
        self.bc = ['\33[48;2;'+c for c in color]
        self.fc = ['\33[38;2;'+c for c in color]
        self.resetcolor = '\33[0m'
        self.resetcursor = '\33[H'
        self.clearscreen = '\33[2J'

    def bcfc(self, ind, string):
        return self.bc[ind[0]] + self.fc[ind[1]] + string

ansi = ANSI()

class SetLib:

    def __init__(self):
        self.list = [
            self.make([[3,3], [5,4]]),
            self.make([[3,4], [4,4], [3,4], [3,5]]),
            self.make([[3,4], [4,4], [3,4], [3,5]]),
            self.make([[4,4]]),
            self.make([[3,4], [4,4]]),
            self.make([[3,4], [4,4], [3,4], [3,5]]),
            self.make([[3,4], [4,4]])
        ]
        self.arr = [[self.join(i,j) for j in range(7)] for i in range(7)]

    def make(self, x):
        seq_set = []
        for r in range(len(x)):
            rot_seq = r*'^'
            shift_seq_set = [i*'<' for i in range(x[r][0], 0, -1)]
            shift_seq_set += [i*'>' for i in range(x[r][1] + 1)]
            for shift_seq in shift_seq_set:
                seq_set.append(rot_seq + shift_seq)
        return seq_set

    def join(self, i, j):
        if i == j: return self.list[i]
        else: return self.list[i] + ['c'+seq for seq in self.list[j]]

setlib = SetLib()

################################################################

class Game:

    def __init__(self, seed=None, readfile=None, writefile=None):
        rd.seed(seed)
        self.readfile = readfile
        self.writefile = writefile or 'tetrisdefault.json'
        self.field = np.full([HEIGHT+PAD, WIDTH+2*PAD], 8, dtype=np.int8)
        self.field[:-PAD, PAD:-PAD] = 0
        self.piece = piecelist[0]
        self.row = -1
        self.col = -1
        self.curr = -1
        self.hold = -1
        self.next = rd.randrange(7)
        self.linescleared = 0

    def print(self):
        scr = ansi.resetcursor
        for i in range(0, HEIGHT, 2):
            if i == 0: scr += 'HOLD '
            elif i == 2: scr += ansi.fc[self.hold+1] + icon[self.hold] + ' '
            else: scr += 5*' '
            for j in range(PAD, PAD+WIDTH):
                scr += ansi.bcfc(self.field[i:i+2,j], '▄')
            scr += ansi.resetcolor
            if i == 0: scr += ' NEXT'
            elif i == 2: scr += ' ' + ansi.fc[self.next+1] + icon[self.next]
            scr += '\n'
        scr += 4*' ' + 'LINES' + str(self.linescleared).rjust(WIDTH-3,' ')
        print(scr)

    def loadcurr(self):
        self.piece = piecelist[self.curr]
        self.row = 0
        self.col = PAD + 3 + (self.curr==3)

    def cutpiece(self):
        r,c,l = self.row, self.col, len(self.piece)
        subfield = self.field[r:r+l, c:c+l]
        subfield -= self.piece

    def pastepiece(self):
        r,c,l = self.row, self.col, len(self.piece)
        subfield = self.field[r:r+l, c:c+l]
        clash = (subfield * self.piece).any()
        if not clash: subfield += self.piece
        return clash

    def spawnpiece(self):
        self.curr = self.next
        self.next = rd.randrange(7)
        self.loadcurr()
        clash = self.pastepiece()
        self.print()
        return not clash

    def clearlines(self):
        subfield = self.field[:-PAD, PAD:-PAD]
        for i in range(1, HEIGHT):
            if subfield[i].all():
                subfield[1:i+1] = subfield[:i]
                self.linescleared += 1

    def switch(self, case, sim, undo=False):
        k = -1 if undo else 1
        if case == 'descend':
            self.row += k
        elif case == 'left':
            self.col -= k
        elif case == 'right':
            self.col += k
        elif case == 'rotate':
            self.piece = np.rot90(self.piece, -k)
        elif case == 'hold':
            if self.hold == -1:
                self.hold, self.curr = self.curr, self.next
                if not sim: self.next = rd.randrange(7)
            else:
                self.hold, self.curr = self.curr, self.hold
            self.loadcurr()

    def step(self, case, sim):
        self.cutpiece()
        self.switch(case, sim)
        clash = self.pastepiece()
        if clash:
            self.switch(case, sim, undo=True)
            self.pastepiece()
        return not clash

    def execute(self, seq, sim=False):
        for key in seq:
            self.step(dic[key], sim)
            if not sim: self.print()
        while self.step('descend', sim): pass
        self.clearlines()

    def getset(self):
        i = self.curr
        j = self.next if self.hold==-1 else self.hold
        return setlib.arr[i][j]

    def getcost(self):
        heights = [HEIGHT]
        holes = 0
        for col in range(PAD, PAD+WIDTH):
            row = 0
            while self.field[row, col] == 0: row += 1
            heights.append(HEIGHT - row)
            for row in range(row+1, HEIGHT):
                if self.field[row, col] == 0: holes += 1
        heights.append(HEIGHT)
        valleys = 0
        for i in range(1, 1+WIDTH):
            if heights[i-1] - heights[i] > 2 and heights[i+1] - heights[i] > 2:
                valleys += 1
        return 2*holes + 5*valleys - self.row

    def simulate(self):
        cpfield = self.field.copy()
        cpnums = [self.linescleared, self.curr, self.hold]
        mincost = np.inf
        for seq in self.getset():
            self.execute(seq, sim=True)
            cost = self.getcost()
            if cost < mincost:
                mincost = cost
                bestseq = seq
            self.field = cpfield.copy()
            self.linescleared, self.curr, self.hold = cpnums
            self.loadcurr()
        return bestseq

    def write(self):
        data = {
            'state' : rd.getstate(),
            'field' : self.field[:-PAD, PAD:-PAD].tolist(),
            'nums'  : [self.linescleared, self.hold, self.next]
        }
        with open(self.writefile, 'w') as f: json.dump(data, f)

    def read(self):
        with open(self.readfile) as f: data = json.load(f)
        a,b,c = data['state']
        rd.setstate((a, tuple(b), c))
        self.field[:-PAD, PAD:-PAD] = np.array(data['field'])
        self.linescleared, self.hold, self.next = data['nums']

    def main(self):
        if self.readfile != None: self.read()
        print(ansi.clearscreen)
        count = 0
        while self.spawnpiece():
            bestseq = self.simulate()
            self.execute(bestseq)
            count = (count + 1) % 2500
            if count == 0: self.write()

################################################################

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--seed', type=int)
    parser.add_argument('-r', '--readfile')
    parser.add_argument('-w', '--writefile')
    args = parser.parse_args()
    game = Game(args.seed, args.readfile, args.writefile)
    game.main()
