from ...abstracted import list
from ....constants.files import filenames, folders
from ....constants.output import thresholds

class ShowdownMoveList(list.List):
    '''The move list stores Showdown's list of moves.'''

    def __init__(self):
        super().__init__(f'{folders.asset}/{folders.txt}/{filenames.move_txt}', thresholds.move_threshold)