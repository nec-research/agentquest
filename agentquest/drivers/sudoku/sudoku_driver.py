from agentquest.utils import Observation
import pandas as pd

class SudokuDriver():
    def __init__(self, board, answer):
        self.initial = str(board)
        self.answer = str(answer)
    
    def reset(self):
        self.initial = pd.DataFrame(
            [x.split('|') for x in self.initial.split('\r\n')]
        )
        self.board = self.initial.copy()
        self.answer = pd.DataFrame(
            [x.split('|') for x in self.answer.split('\r\n')]
        )

        self.initial = self.initial.astype(str)
        self.board = self.board.astype(str)
        self.answer = self.answer.astype(str)

        obs = Observation(
            output = str(self.board.values),
            done = False
        )
        return obs

    def step(self, action):
        row = action.row_id
        col = action.col_id
        val = action.action_value

        done = False
        if not isinstance(val, str):
            val = str(val)

        if self.invalid_quadrant(row, col, val):
            obs = Observation(
                output=(f'Inadmissible action. There is already a {val} in the '
                        'provided quadrant.'),
                done=done
            )
            return obs

        if self.invalid_rows(row, val):
            obs = Observation(
                output=f'Inadmissible action. {val} is already in row {row}.',
                done=done

            )
            return obs
        
        if self.invalid_cols(col, val):
            obs = Observation(
                output=f'Inadmissible action. {val} is already in column {col}.',
                done=done
            )
            return obs
        
        if self.already_a_number(row, col):
            obs = Observation(
                output=('Inadmissible action. You cannot change the value of a '
                        'starting number.'),
                done=done
            )
            return obs

        self.board.loc[row, col] = val

        if not self.is_finished():
            obs = Observation(output=str(self.board.values), done=done)
        elif self.valid_game():
            obs = Observation(output='You won!', done=True)
        else:
            obs = Observation(output='You lost!', done=True)

        return obs
        
    def invalid_rows(self, row, val):
        return val in self.board.loc[row].values

    def invalid_cols(self, col, val):
        return val in self.board[[col]].values
    
    def already_a_number(self, row, col):
        return self.initial.loc[row, col] != '*'

    def invalid_quadrant(self, row, col, val):
        row_idx = ((row) // 3)*3
        col_idx = ((col) // 3)*3

        quadrant = self.board.loc[row_idx:row_idx+2, col_idx:col_idx+2].values
        return val in quadrant.flatten().tolist()

    def is_finished(self):
        return not '*' in self.board.values.flatten().tolist()

    def valid_game(self):
        for i in range(9):
            for j in range(9):
                if self.board.loc[i,j]!=self.answer.loc[i,j]:
                    return False
        return True