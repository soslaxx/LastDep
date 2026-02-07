from typing import List, Tuple
from dataclasses import dataclass


@dataclass
class PatternMatch:
    pat_type: str
    symbols: List[Tuple[int, int]]
    sym_type: str
    length: int
    base_val: int


class Patt:
    def __init__(self, rows: int = 3, cols: int = 5):
        self.rows = rows
        self.cols = cols

    def find_all(self, grid: List[List[str]]) -> List[PatternMatch]:
        matches = []
        matches.extend(self._hor(grid))
        matches.extend(self._vert(grid))
        matches.extend(self._diag(grid))
        matches.extend(self._horxl(grid))
        matches.extend(self._zig(grid))
        matches.extend(self._eye(grid))
        matches.extend(self._jack(grid))
        return self._dedup(matches)
    
    def _hor(self, grid: List[List[str]]) -> List[PatternMatch]:

        matches = []
        for row in range(self.rows):
            for length in range(5, 2, -1):
                for start_col in range(self.cols - length + 1):
                    symbols = [grid[row][start_col + i] for i in range(length)]
                    if len(set(symbols)) == 1:
                        positions = [(row, start_col + i) for i in range(length)]
                        multiplier = 3.0 if length == 5 else 2.0 if length == 4 else 1.0
                        matches.append(PatternMatch(
                            pat_type=f"HOR-{length}",
                            symbols=positions,
                            sym_type=symbols[0],
                            length=length,
                            base_val=multiplier
                        ))
                        break
        return matches
    
    def _vert(self, grid: List[List[str]]) -> List[PatternMatch]:
        matches = []
        for col in range(self.cols):
            symbols = [grid[row][col] for row in range(self.rows)]
            if len(set(symbols)) == 1:
                positions = [(row, col) for row in range(self.rows)]
                matches.append(PatternMatch(
                    pat_type="VERT",
                    symbols=positions,
                    sym_type=symbols[0],
                    length=3,
                    base_val=1.0
                ))
        return matches
    
    def _diag(self, grid: List[List[str]]) -> List[PatternMatch]:
        matches = []
        
        for start_col in range(self.cols - 2):
            max_length = min(3, self.cols - start_col)
            if max_length >= 3:
                symbols = [grid[i][start_col + i] for i in range(max_length)]
                if len(set(symbols)) == 1:
                    positions = [(i, start_col + i) for i in range(max_length)]
                    matches.append(PatternMatch(
                        pat_type="DIAG-DOWN",
                        symbols=positions,
                        sym_type=symbols[0],
                        length=max_length,
                        base_val=1.0
                    ))
        for start_col in range(2, self.cols):
            max_length = min(3, start_col + 1)
            if max_length >= 3:
                symbols = [grid[i][start_col - i] for i in range(max_length)]
                if len(set(symbols)) == 1:
                    positions = [(i, start_col - i) for i in range(max_length)]
                    matches.append(PatternMatch(
                        pat_type="DIAG-UP",
                        symbols=positions,
                        sym_type=symbols[0],
                        length=max_length,
                        base_val=1.0
                    ))

        return matches
    
    def _horxl(self, grid: List[List[str]]) -> List[PatternMatch]:
        matches = []
        for row in range(self.rows):
            symbols = grid[row]
            if len(set(symbols)) == 1:
                positions = [(row, col) for col in range(self.cols)]
                matches.append(PatternMatch(
                    pat_type="HOR-XL",
                    symbols=positions,
                    sym_type=symbols[0],
                    length=5,
                    base_val=3.0
                ))
        return matches
    
    def _zig(self, grid: List[List[str]]) -> List[PatternMatch]:
        matches = []
        for start_col in range(self.cols - 2):
            if start_col + 2 < self.cols:
                zig = [
                    grid[0][start_col],
                    grid[1][start_col + 1],
                    grid[2][start_col + 2]
                ]
                if len(set(zig)) == 1:
                    positions = [
                        (0, start_col),
                        (1, start_col + 1),
                        (2, start_col + 2)
                    ]
                    matches.append(PatternMatch(
                        pat_type="ZIG",
                        symbols=positions,
                        sym_type=zig[0],
                        length=3,
                        base_val=7.0
                    ))

        for start_col in range(2, self.cols):
            zag = [
                grid[0][start_col],
                grid[1][start_col - 1],
                grid[2][start_col - 2]
            ]
            if len(set(zag)) == 1:
                positions = [
                    (0, start_col),
                    (1, start_col - 1),
                    (2, start_col - 2)
                ]
                matches.append(PatternMatch(
                    pat_type="ZAG",
                    symbols=positions,
                    sym_type=zag[0],
                    length=3,
                    base_val=7.0
                ))

        return matches
    
    def _updown(self, grid: List[List[str]]) -> List[PatternMatch]:
        matches = []
        
        for col in range(1, self.cols - 1):
            if grid[0][col] == grid[1][col]:
                positions = [(0, col), (1, col)]
                matches.append(PatternMatch(
                    pat_type="ABOVE",
                    symbols=positions,
                    sym_type=grid[0][col],
                    length=2,
                    base_val=4.0
                ))
            if grid[1][col] == grid[2][col]:
                positions = [(1, col), (2, col)]
                matches.append(PatternMatch(
                    pat_type="BELOW",
                    symbols=positions,
                    sym_type=grid[1][col],
                    length=2,
                    base_val=4.0
                ))

        return matches
    
    def _eye(self, grid: List[List[str]]) -> List[PatternMatch]:
        matches = []
        
        for ctr_row in range(1, self.rows - 1):
            for ctr_col in range(1, self.cols - 1):
                center = grid[ctr_row][ctr_col]
                top = grid[ctr_row - 1][ctr_col]
                bottom = grid[ctr_row + 1][ctr_col]
                left = grid[ctr_row][ctr_col - 1]
                right = grid[ctr_row][ctr_col + 1]
                
                if center == top == bottom == left == right:
                    positions = [
                        (ctr_row, ctr_col),
                        (ctr_row - 1, ctr_col),
                        (ctr_row + 1, ctr_col),
                        (ctr_row, ctr_col - 1),
                        (ctr_row, ctr_col + 1)
                    ]
                    matches.append(PatternMatch(
                        pat_type="EYE",
                        symbols=positions,
                        sym_type=center,
                        length=5,
                        base_val=8.0
                    ))

        return matches
    
    def _jack(self, grid: List[List[str]]) -> List[PatternMatch]:
        all_syms = []
        for row in grid:
            all_syms.extend(row)
        
        if len(set(all_syms)) == 1:
            positions = [(r, c) for r in range(self.rows) for c in range(self.cols)]
            return [PatternMatch(
                pat_type="JACKPOT",
                symbols=positions,
                sym_type=all_syms[0],
                length=15,
                base_val=10.0
            )]
        return []
    
    def _dedup(self, matches: List[PatternMatch]) -> List[PatternMatch]:
        if not matches:
            return matches
        matches.sort(key=lambda m: (m.length, m.pat_type), reverse=True)
        
        used_pos = set()
        uniq_matches = []
        
        for match in matches:
            match_pos = set(match.symbols)
            if not match_pos.intersection(used_pos):
                uniq_matches.append(match)
                used_pos.update(match_pos)
        
        return uniq_matches



