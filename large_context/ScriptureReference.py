import re
import requests
from functools import cache

class ScriptureReference:
    verse_ones = [
    1, 1534, 2747, 3606, 4895, 5854, 6512, 7130, 7215, 8026, 8721, 9538, 10257, 11200, 12022, 12302, 12707, 12874, 13944,
    16471, 17386, 17608, 17725, 19016, 20380, 20534, 21807, 22164, 22361, 22434, 22580, 22601, 22649, 22754, 22801, 22857, 
    22910, 22948, 23159, 23214, 24285, 24963, 26114, 26993, 27999, 28432, 28869, 29125, 29274, 29429, 29533, 29628, 29717, 
    29764, 29877, 29960, 30006, 30031, 30334, 30442, 30547, 30608, 30713, 30726, 30741, 30766, 31171
    ]
    
    book_codes = {
        'GEN': {
            'codes': ['Gen', 'Gn', '1M'],
            'verses': [31, 25, 24, 26, 32, 22, 24, 22, 29, 32, 32, 20, 18, 24, 21, 16, 27, 33, 38, 18, 34, 24, 20, 67, 34, 
                       35, 46, 22, 35, 43, 55, 32, 20, 31, 29, 43, 36, 30, 23, 23, 57, 38, 34, 34, 28, 34, 31, 22, 33, 26]
        },
        'EXO': {
            'codes': ['Ex', '2M'],
            'verses': [22, 25, 22, 31, 23, 30, 25, 32, 35, 29, 10, 51, 22, 31, 27, 36, 16, 27, 25, 26, 36, 31, 33, 18, 40, 
                       37, 21, 43, 46, 38, 18, 35, 23, 35, 35, 38, 29, 31, 43, 38]
        },
        'LEV': {
            'codes': ['Lev', 'Lv', '3M'],
            'verses': [17, 16, 17, 35, 19, 30, 38, 36, 24, 20, 47, 8, 59, 57, 33, 34, 16, 30, 37, 27, 24, 33, 44, 23, 55, 
                       46, 34]
        },
        'NUM': {
            'codes': ['Nm', 'Nu', '4M'],
            'verses': [54, 34, 51, 49, 31, 27, 89, 26, 23, 36, 35, 16, 33, 45, 41, 50, 13, 32, 22, 29, 35, 41, 30, 25, 18, 
                       65, 23, 31, 40, 16, 54, 42, 56, 29, 34, 13]
        },
        'DEU': {
            'codes': ['Deut', 'Dt', '5M'],
            'verses': [46, 37, 29, 49, 33, 25, 26, 20, 29, 22, 32, 32, 18, 29, 23, 22, 20, 22, 21, 20, 23, 30, 25, 22, 19, 
                       19, 26, 68, 29, 20, 30, 52, 29, 12]
        },
        'JOS': {
            'codes': ['Josh', 'Jos'],
            'verses': [18, 24, 17, 24, 15, 27, 26, 35, 27, 43, 23, 24, 33, 15, 63, 10, 18, 28, 51, 9, 45, 34, 16, 33]
        },
        'JDG': {
            'codes': ['Jdg', 'Judg'],
            'verses': [36, 23, 31, 24, 31, 40, 25, 35, 57, 18, 40, 15, 25, 20, 20, 31, 13, 31, 30, 48, 25]
        },
        'RUT': {
            'codes': ['Ru', 'Rth'],
            'verses': [22, 23, 18, 22]
        },
        '1SA': {
            'codes': ['1Sam', '1Sm'],
            'verses': [28, 36, 21, 22, 12, 21, 17, 22, 27, 27, 15, 25, 23, 52, 35, 23, 58, 30, 24, 42, 15, 23, 29, 22, 44, 
                       25, 12, 25, 11, 31, 13]
        },
        '2SA': {
            'codes': ['2Sam', '2Sm'],
            'verses': [27, 32, 39, 12, 25, 23, 29, 18, 13, 19, 27, 31, 39, 33, 37, 23, 29, 33, 43, 26, 22, 51, 39, 25]
        },
        '1KI': {
            'codes': ['1Kg', '1K'],
            'verses': [53, 46, 28, 34, 18, 38, 51, 66, 28, 29, 43, 33, 34, 31, 34, 34, 24, 46, 21, 43, 29, 53]
        },
        '2KI': {
            'codes': ['2Kg', '2K'],
            'verses': [18, 25, 27, 44, 27, 33, 20, 29, 37, 36, 21, 21, 25, 29, 38, 20, 41, 37, 37, 21, 26, 20, 37, 20, 30]
        },
        '1CH': {
            'codes': ['1Ch'],
            'verses': [54, 55, 24, 43, 26, 81, 40, 40, 44, 14, 47, 40, 14, 17, 29, 43, 27, 17, 19, 8, 30, 19, 32, 31, 31, 
                       32, 34, 21, 30]
        },
        '2CH': {
            'codes': ['2Ch'],
            'verses': [17, 18, 17, 22, 14, 42, 22, 18, 31, 19, 23, 16, 22, 15, 19, 14, 19, 34, 11, 37, 20, 12, 21, 27, 28, 
                       23, 9, 27, 36, 27, 21, 33, 25, 33, 27, 23]
        },
        'EZR': {
            'codes': ['Ezr'],
            'verses': [11, 70, 13, 24, 17, 22, 28, 36, 15, 44]
        },
        'NEH': {
            'codes': ['Neh'],
            'verses': [11, 20, 32, 23, 19, 19, 73, 18, 38, 39, 36, 47, 31]
        },
        'EST': {
            'codes': ['Est'],
            'verses': [22, 23, 15, 17, 14, 14, 10, 17, 32, 3]
        },
        'JOB': {
            'codes': ['Jb', 'Job'],
            'verses': [22, 13, 26, 21, 27, 30, 21, 22, 35, 22, 20, 25, 28, 22, 35, 22, 16, 21, 29, 29, 34, 30, 17, 25, 6, 
                       14, 23, 28, 25, 31, 40, 22, 33, 37, 16, 33, 24, 41, 30, 24, 34, 17]
        },
        'PSA': {
            'codes': ['Ps'],
            'verses': [6, 12, 8, 8, 12, 10, 17, 9, 20, 18, 7, 8, 6, 7, 5, 11, 15, 50, 14, 9, 13, 31, 6, 10, 22, 12, 14, 9, 
                       11, 12, 24, 11, 22, 22, 28, 12, 40, 22, 13, 17, 13, 11, 5, 26, 17, 11, 9, 14, 20, 23, 19, 9, 6, 7, 
                       23, 13, 11, 11, 17, 12, 8, 12, 11, 10, 13, 20, 7, 35, 36, 5, 24, 20, 28, 23, 10, 12, 20, 72, 13, 19, 
                       16, 8, 18, 12, 13, 17, 7, 18, 52, 17, 16, 15, 5, 23, 11, 13, 12, 9, 9, 5, 8, 28, 22, 35, 45, 48, 43, 
                       13, 31, 7, 10, 10, 9, 8, 18, 19, 2, 29, 176, 7, 8, 9, 4, 8, 5, 6, 5, 6, 8, 8, 3, 18, 3, 3, 21, 26, 
                       9, 8, 24, 13, 10, 7, 12, 15, 21, 10, 20, 14, 9, 6]
        },
        'PRO': {
            'codes': ['Pr'],
            'verses': [33, 22, 35, 27, 23, 35, 27, 36, 18, 32, 31, 28, 25, 35, 33, 33, 28, 24, 29, 30, 31, 29, 35, 34, 28, 
                       28, 27, 28, 27, 33, 31]
        },
        'ECC': {
            'codes': ['Ec', 'Qoh'],
            'verses': [18, 26, 22, 16, 20, 12, 29, 17, 18, 20, 10, 14]
        },
        'SNG': {
            'codes': ['Sos', 'Song'],
            'verses': [17, 17, 11, 16, 16, 13, 13, 14]
        },
        'ISA': {
            'codes': ['Isa'],
            'verses': [31, 22, 26, 6, 30, 13, 25, 22, 21, 34, 16, 6, 22, 32, 9, 14, 14, 7, 25, 6, 17, 25, 18, 23, 12, 21, 
                       13, 29, 24, 33, 9, 20, 24, 17, 10, 22, 38, 22, 8, 31, 29, 25, 28, 28, 25, 13, 15, 22, 26, 11, 23, 
                       15, 12, 17, 13, 12, 21, 14, 21, 22, 11, 12, 19, 12, 25, 24]
        },
        'JER': {
            'codes': ['Jer', 'Jr'],
            'verses': [19, 37, 25, 31, 31, 30, 34, 22, 26, 25, 23, 17, 27, 22, 21, 21, 27, 23, 15, 18, 14, 30, 40, 10, 38, 
                       24, 22, 17, 32, 24, 40, 44, 26, 22, 19, 32, 21, 28, 18, 16, 18, 22, 13, 30, 5, 28, 7, 47, 39, 46, 64, 
                       34]
        },
        'LAM': {
            'codes': ['Lam', 'Lm'],
            'verses': [22, 22, 66, 22, 22]
        },
        'EZK': {
            'codes': ['Ezek', 'Ezk'],
            'verses': [28, 10, 27, 17, 17, 14, 27, 18, 11, 22, 25, 28, 23, 23, 8, 63, 24, 32, 14, 49, 32, 31, 49, 27, 17, 21, 
                       36, 26, 21, 26, 18, 32, 33, 31, 15, 38, 28, 23, 29, 49, 26, 20, 27, 31, 25, 24, 23, 35]
        },
        'DAN': {
            'codes': ['Dn', 'Dan'],
            'verses': [21, 49, 30, 37, 31, 28, 28, 27, 27, 21, 45, 13]
        },
        'HOS': {
            'codes': ['Hos', 'Hs'],
            'verses': [11, 23, 5, 19, 15, 11, 16, 14, 17, 15, 12, 10, 14, 9]
        },
        'JOL': {
            'codes': ['Joel', 'Jl'],
            'verses': [20, 32, 21]
        },
        'AMO': {
            'codes': ['Am'],
            'verses': [15, 16, 15, 13, 27, 14, 17, 14, 15]
        },
        'OBA': {
            'codes': ['Ob'],
            'verses': [21]
        },
        'JON': {
            'codes': ['Jon'],
            'verses': [17, 10, 10, 11]
        },
        'MIC': {
            'codes': ['Mi', 'Mc'],
            'verses': [16, 13, 12, 13, 15, 16, 20]
        },
        'NAM': {
            'codes': ['Na'],
            'verses': [15, 13, 19]
        },
        'HAB': {
            'codes': ['Hab'],
            'verses': [17, 20, 19]
        },
        'ZEP': {
            'codes': ['Zep', 'Zp'],
            'verses': [18, 15, 20]
        },
        'HAG': {
            'codes': ['Hag', 'Hg'],
            'verses': [15, 23]
        },
        'ZEC': {
            'codes': ['Zc', 'Zec'],
            'verses': [21, 13, 10, 14, 11, 15, 14, 20, 12, 21, 17, 14, 20, 9, 15, 21]
        },
        'MAL': {
            'codes': ['Mal', 'Ml'],
            'verses': [14, 17, 18, 6]
        },
        'MAT': {
            'codes': ['Mt', 'Mat'],
            'verses': [25, 23, 17, 25, 48, 34, 29, 34, 38, 42, 30, 50, 58, 36, 39, 28, 30, 34, 34, 46, 30, 46, 39, 28, 34, 
                       31, 46, 46, 38, 71, 66, 20]
        },
        'MRK': {
            'codes': ['Mk', 'Mar'],
            'verses': [45, 28, 35, 41, 43, 56, 29, 38, 50, 52, 33, 44, 37, 72, 47, 20]
        },
        'LUK': {
            'codes': ['Lk', 'Lu'],
            'verses': [80, 52, 38, 44, 39, 49, 50, 56, 62, 42, 54, 59, 35, 35, 32, 31, 37, 43, 48, 47, 38, 71, 56, 39, 49, 
                       57, 80, 55, 28, 35, 32, 31, 37, 50, 26, 46, 51, 66, 53, 59, 37, 35, 50, 40, 46, 51, 69, 53, 56, 20]
        },
        'JHN': {
            'codes': ['Jn', 'Joh', 'Jhn'],
            'verses': [51, 25, 36, 54, 47, 71, 53, 59, 41, 42, 57, 50, 38, 31, 27, 33, 26, 40, 42, 31, 25]
        },
        'ACT': {
            'codes': ['Ac'],
            'verses': [26, 47, 26, 37, 42, 15, 60, 40, 43, 48, 30, 25, 52, 28, 41, 40, 34, 28, 40, 38, 40, 30, 35, 27, 27, 
                       32, 44, 31]
        },
        'ROM': {
            'codes': ['Ro', 'Rm'],
            'verses': [32, 29, 31, 25, 21, 23, 25, 39, 33, 21, 36, 21, 14, 23, 33, 27]
        },
        '1CO': {
            'codes': ['1Co'],
            'verses': [31, 16, 23, 21, 13, 20, 40, 13, 27, 33, 34, 31, 13, 40, 58, 24]
        },
        '2CO': {
            'codes': ['2Co'],
            'verses': [24, 17, 18, 18, 21, 18, 16, 24, 15, 18, 33, 21, 14]
        },
        'GAL': {
            'codes': ['Gal', 'Gl'],
            'verses': [24, 21, 29, 31, 26, 18]
        },
        'EPH': {
            'codes': ['Ep'],
            'verses': [23, 22, 21, 32, 33, 24]
        },
        'PHP': {
            'codes': ['Php', 'Philip'],
            'verses': [30, 30, 21, 23]
        },
        'COL': {
            'codes': ['Col'],
            'verses': [29, 23, 25, 18]
        },
        '1TH': {
            'codes': ['1Th'],
            'verses': [10, 20, 13, 18, 28]
        },
        '2TH': {
            'codes': ['2Th'],
            'verses': [12, 17, 18]
        },
        '1TI': {
            'codes': ['1Ti', '1Tm'],
            'verses': [20, 15, 16, 16, 25, 21, 25]
        },
        '2TI': {
            'codes': ['2Ti', '2Tm'],
            'verses': [18, 26, 17, 22]
        },
        'TIT': {
            'codes': ['Tit'],
            'verses': [16, 15, 15]
        },
        'PHM': {
            'codes': ['Phile', 'Phm'],
            'verses': [25]
        },
        'HEB': {
            'codes': ['Hb', 'Heb'],
            'verses': [14, 18, 19, 16, 14, 20, 28, 13, 28, 39, 40, 29, 25]
        },
        'JAS': {
            'codes': ['Ja', 'Jm'],
            'verses': [27, 26, 18, 17, 20]
        },
        '1PE': {
            'codes': ['1Pe', '2Pt'],
            'verses': [25, 25, 22, 19, 14]
        },
        '2PE': {
            'codes': ['2Pe', '2Pt'],
            'verses': [21, 22, 18]
        },
        '1JN': {
            'codes': ['1Jn', '1Jo', '1Jh'],
            'verses': [10, 29, 24, 21, 21]
        },
        '2JN': {
            'codes': ['2Jn', '2Jo', '2Jh'],
            'verses': [13]
        },
        '3JN': {
            'codes': ['3Jn', '3Jo', '3Jh'],
            'verses': [14]
        },
        'JUD': {
            'codes': ['Ju', 'Jd'],
            'verses': [25]
        },
        'REV': {
            'codes': ['Rev', 'Rv'],
            'verses': [20, 29, 22, 18, 14, 20, 17, 18, 20, 15, 23, 19, 21, 18, 18, 24, 22, 21, 21, 15, 27, 21]
        }
    }
    

    def __init__(self, start_ref, end_ref=None, bible_filename='eng-engwmbb'):
        self.start_ref = self.parse_scripture_reference(start_ref)
        self.end_ref = self.parse_scripture_reference(end_ref) if end_ref else self.start_ref
        self.bible_url = f"https://raw.githubusercontent.com/BibleNLP/ebible/main/corpus/{bible_filename}.txt"
        self.verses = self.get_verse_range() if self.start_ref and self.end_ref else []

    @classmethod
    def parse_scripture_reference(cls, input_ref):
        normalized_input = re.sub(r"\s+", "", input_ref).upper()
        regex = re.compile(r"^(\d)?(\D+)(\d+)?(?::(\d+))?(?:-(\d+)?(?::(\d+))?)?$")
        match = regex.match(normalized_input)
        if not match:
            return None

        bookPrefix, bookName, startChapter, startVerse, endChapter, endVerse = match.groups()
        fullBookName = f"{bookPrefix or ''}{bookName}".upper()

        bookCode = next((code for code, details in cls.book_codes.items() if any(fullBookName.startswith(name.upper()) for name in details['codes'])), None)
        if not bookCode:
            return None

        chapters = cls.book_codes[bookCode]['verses']
        startChapter = int(startChapter) if startChapter else 1
        endChapter = int(endChapter) if endChapter else startChapter
        startVerse = int(startVerse) if startVerse else 1
        endVerse = int(endVerse) if endVerse else chapters[startChapter - 1]

        return {
            'bookCode': bookCode,
            'startChapter': startChapter,
            'startVerse': startVerse,
            'endChapter': endChapter,
            'endVerse': endVerse
        }

    @cache
    def get_verse_range(self):
        bible_text = self.load_bible(self.bible_url)
        if not bible_text:
            print("Failed to load Bible text")
            return []

        book_index = list(self.book_codes.keys()).index(self.start_ref['bookCode'])
        print(f'book_index: {book_index}')
        start_line_index = self.verse_ones[book_index] - 1
        print(f'start_line_index: {start_line_index}')

        # Calculate the starting index of the range
        start_index = start_line_index + \
                    sum(self.book_codes[self.start_ref['bookCode']]['verses'][:self.start_ref['startChapter'] - 1]) + \
                    self.start_ref['startVerse'] - 1
        # Sum finds location of book, chapter, and verse in the Bible text
        print(f'start_index: {start_index}')

        # Calculate the ending index of the range
        book_index = list(self.book_codes.keys()).index(self.end_ref['bookCode'])
        print(f'book_index: {book_index}')
        start_line_index = self.verse_ones[book_index] - 1
        print(f'start_line_index: {start_line_index}')

        # Calculate the starting index of the range
        end_index = start_line_index + \
                    sum(self.book_codes[self.end_ref['bookCode']]['verses'][:self.end_ref['startChapter'] - 1]) + \
                    self.end_ref['startVerse'] - 1

        return bible_text[start_index:end_index + 1]

    def load_bible(self, url):
        response = requests.get(url)
        return response.text.splitlines() if response.status_code == 200 else []

# Example usage:
# scripture_ref = ScriptureReference("gen 50:25", "exo 1:5")
# [print(verse) for verse in scripture_ref.verses]
