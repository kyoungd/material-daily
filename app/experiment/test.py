import flask



# # import pandas as pd
# # import requests
# # from _pickle import dump
# # import re

# # # DEFAULT_TICKERS = ['goog', 'aapl']
# # # URL = 'http://www.sec.gov/cgi-bin/browse-edgar?CIK={}&Find=Search&owner=exclude&action=getcompany'
# # # CIK_RE = re.compile(r'.CIK=(\d{10}).')

# # # cik_dict = {}
# # # for ticker in DEFAULT_TICKERS:
# # #     f = requests.get(URL.format(ticker), stream=True)
# # #     results = CIK_RE.findall(f.text)
# # #     print (results)


# # def print_one(one):
# #     print(one)
# #     return one

# # arr = [1, 2, 3, 4, 5]
# # print(list(map(print_one, arr)))


# matrix:tuple = ('..........',
#           'xx........',
#           'xxxx......',
#           'xx........',
#           '.......xx.',
#           'xx.....xx.',
#           'xx.....xx.',
#           '..........',
#           '........xx',
#           '........xx')

# # convert matrix to list of tuples
# grid = []
# for row in matrix:
#     grid.append([*row])


# class CountLand:
#     def __init__(self, matrix:tuple):
#         self.grid = []
#         for row in matrix:
#             self.grid.append([*row])
#         self.counter = 0
#         self.row = len(grid)
#         self.col = len(grid[0])

#     def count_island(self):
#         for r in range(self.row):
#             for c in range(self.col):
#                 if self.grid[r][c] == 'x':
#                     self.counter += 1
#                     self.dfs(r, c)
    
#     def dfs(self, row, col):
#         if row < 0 or row >= self.row:
#             return
#         if col < 0 or col >= self.col:
#             return
#         if self.grid[row][col] != 'x':
#             return
#         self.grid[row][col] = '.'
#         self.dfs(row+1, col)
#         self.dfs(row-1, col)
#         self.dfs(row, col+1)
#         self.dfs(row, col-1)

#     def print(self):
#         print(self.counter)

# app = CountLand(matrix)
# app.count_island()
# app.print()

# arr = [1, 2, 3, 4, 5, 2, 4, 5, 6, 7, 8, 9, 0, 2, 3]
# arrRange = len(arr)

# class CountIncrement:
#     def __init__(self, arr:list):
#         self.arr = arr
#         self.maxCounter = 0
#         self.counter = 0

#     def countIt(self):
#         isAfterFirst = False
#         lastElem = 0
#         for elem in self.arr:
#             if not isAfterFirst:
#                 isAfterFirst = True
#             else:
#                 if (elem - lastElem) == 1:
#                     self.counter += 1
#                     self.maxCounter = max(self.maxCounter, self.counter)
#                 else:
#                     self.counter = 0                
#             lastElem = elem

#     def run(self):
#         self.countIt()
#         print(self.maxCounter)

# app = CountIncrement(arr)
# app.run()


matrix:tuple = ('..........',
          'xx........',
          'xxxxxx....',
          'xx........',
          '..........',
          'xx..#....',
          'xx..#.....',
          '..........',
          '..........',
          '..........')

class LandDrop:
    def __init__(self, matrix:tuple):
        self.grid = []
        for row in matrix:
            self.grid.append([*row])
        self.row = len(self.grid)
        self.col = len(self.grid[0])

    def find_blocks(self, grid)->list:
        blocks = []
        for r in range(self.row-1):
            for c in range(self.col-1):
                if grid[r][c] == '#':
                    blocks.append({'r':r, 'c':c})
                    grid[r][c] = '.'
        return blocks
    
    def find_distance(self, grid, blocks) -> int:
        minDistance = len(grid) + 1
        for block in blocks:
            r = block['r']
            c = block['c']
            distance = 0
            while r > 0:
                if grid[r][c] == 'x':
                    minDistance = min(minDistance, distance)
                distance += 1
                r -= 1
        return minDistance-1

    def drop_land(self, grid:list, rows:int) -> list:
        for r in range(rows):
            grid.pop()
            grid.insert(0, ['.'] * self.col)
        return grid
    
    def add_blocks(self, grid:list, blockslist) -> list:
        for block in blockslist:
            grid[block['r']][block['c']] = '#'
        return grid
    
    def printMe(self, grid:list):
        for row in grid:
            print(''.join(row))
    
    def run(self):
        blocks = self.find_blocks(self.grid)
        distance = self.find_distance(self.grid, blocks)
        if distance > 0:
            self.grid = self.drop_land(self.grid, distance)
        self.grid = self.add_blocks(self.grid, blocks)
        self.printMe(self.grid)


lp = LandDrop(matrix)
lp.run()
