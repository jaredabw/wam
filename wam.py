import bs4
import re
import tkinter as tk
from tkinter import filedialog

class Row():
    def __init__(self, grade: float = None, max_grade: float = None, weight: float = None, row: bs4.element.Tag = None):
        if row is None:
            if grade is None or max_grade is None or weight is None:
                raise ValueError('Invalid input. No row or grade, max grade, and weight found.')
            self.grade = grade
            self.max_grade = max_grade
            self.weight = weight
            self.title = 'Custom'
        else:
            self.row = row

            self.title = row.find('div', {'class': 'rowtitle'})
            if self.title is None:
                raise ValueError('Invalid row. No title found.')
            self.title = self.title.text

            self.weight = re.search(r'(\d+\.\d+|\d+)%', self.title)
            if self.weight is None:
                raise ValueError('Invalid row. No weight found.') # allow manual entry input()
            self.weight = float(self.weight.group(1))/100
            
            tds = row.find_all('td')

            if tds[0].find('i') is not None:
                tds[0].find('i').decompose()
                tds[0].find('span').decompose()

            self.grade = tds[0].text
            if self.grade == '-':
                raise ValueError('Invalid row. No grade found (–).')
            self.grade = float(self.grade)

            try:
                self.max_grade = tds[1].text
            except IndexError:
                raise ValueError('Invalid row. No max grade found.')
            self.max_grade = float(re.search(r'.(\d+)', self.max_grade).group(1))

            self.title = self.title.split('(')[0].strip()
            self.title = self.title.split('[')[0].strip()

        self.mark = self.grade/self.max_grade
        self.weighted_mark = self.mark*self.weight

    def __str__(self):
        return f'{self.title}: {self.grade}/{self.max_grade} | {round(self.weight,4)} | {round(self.weighted_mark,4)}'
    
    def __repr__(self):
        return self.__str__()
    
    def __lt__(self, other: 'Row'):
        return self.title < other.title
    
    def __gt__(self, other: 'Row'):
        return self.title > other.title
    
    def __eq__(self, other: 'Row'):
        return self.title == other.title
    
class GradesTable():
    def __init__(self, html_rows):
        self.rows: list[Row] = []

        for row in html_rows:
            try:
                self.add_row(Row(row=row))
            except ValueError as e:
                pass

    def add_row(self, row: Row):
        self.rows.append(row)

    def verify_weights(self):
        total_weight = round(sum([row.weight for row in self.rows]), 4)
        if total_weight < 1:
            print(f'\nTotal weight is under 100%. Total weight: {total_weight*100}%.')\
        
            input_ = 'x'
            while input_.lower() != 'y' and input_.lower() != 'n':
                input_ = input('Do you want to add another grade? (y/n): ')
                if input_ == 'y':
                    new_grade = float(input('Enter the mark of the new grade: '))
                    new_max_grade = float(input('Enter the max mark of the new grade: '))
                    new_weight = float(input('Enter the weight (%) of the new grade: '))/100
                    self.add_row(Row(new_grade, new_max_grade, new_weight))
                elif input_ == 'n':
                    self.recalculate()
            
            self.verify_weights()

        elif total_weight > 1:
            print(f'\nTotal weight is over 100%. Total weight: {total_weight*100}%.')

            self.recalculate()

    def recalculate(self):
        print('Recalculating as if total weight is 100%.\n')
        total_weight = round(sum([row.weight for row in self.rows]),6)
        for row in self.rows:
            row.weight /= total_weight
            row.weighted_mark = row.mark*row.weight

    def __str__(self) -> str:
        self.rows.sort()
        self.verify_weights()
        name_length = max([len(row.title) for row in self.rows]) + 1
        NAME = 'NAME:'
        MARK = 'MARK'
        MAX = 'MAX'
        WEIGHT = 'WEIGHT'
        WEIGHTED_MARK = 'WEIGHTED MARK'
        s = f'\n{NAME:<{name_length}} {MARK:>5} / {MAX:<4} | {WEIGHT:<6} | {WEIGHTED_MARK}\n'
        for row in self.rows:
            ttitle = row.title + ':'
            s += f'{ttitle:<{name_length}} {row.grade:>5} / {round(row.max_grade):<4} | {round(row.weight,4):<6} | {round(row.weighted_mark,4)}\n'

        total_weighted_mark = sum([row.weighted_mark for row in self.rows])
        s += f'\nTotal weighted mark: {round(total_weighted_mark*100,2)}%\n'
        
        return s

def main():
    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename(defaultextension='.html',
                                           filetypes=[('HTML files', '*.html')],
                                           initialdir='.')
    if file_path == '':
        print('No file selected.')
        return

    soup = bs4.BeautifulSoup(open(file_path), 'html.parser')

    table = soup.find('table', {'class': 'generaltable boxaligncenter user-grade'})
    if table is None:
        print('There should be exactly one grade report.')
        return

    html_rows = table.find('tbody').find_all('tr')

    grades = GradesTable(html_rows)
    print(grades)

if __name__ == '__main__':
    main()
