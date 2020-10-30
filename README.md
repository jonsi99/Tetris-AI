# Tetris AI
The `tetris.py` script runs a game of Tetris played by an AI. Given a particular piece, the AI simulates a set of key sequences before executing whichever sequence results in the best state.

## Usage
The script is to be run from the command line.
```
python tetris.py
```
You can set the random seed by feeding an integer to `-s`.
```
python tetris.py -s 99
```
The program periodically saves the state of the game into a JSON file. This allows you to, if you terminate the program, continue where it left off by reading the file. You can set the file name via `-w`, otherwise it is `tetrisdefault.json`.
```
python tetris.py -w example.json
python tetris.py -s 0 -w withseed0.json
```
To continue from a saved state, specify the file to read from via `-r`.
```
python tetris.py -r samefile.json -w samefile.json
python tetris.py -r afile.json -w anotherfile.json
```

## Libraries
The `numpy` library is required.