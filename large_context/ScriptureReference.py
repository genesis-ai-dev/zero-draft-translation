import requests
from functools import cache
import re
import os

book_codes = {
    'GEN': {
        'codes': ['Gen', 'Gn', '1M'],
        'number': 1
    },
    'EXO': {
        'codes': ['Ex', '2M'],
        'number': 2
    },
    'LEV': {
        'codes': ['Lev', 'Lv', '3M'],
        'number': 3
    },
    'NUM': {
        'codes': ['Nm', 'Nu', '4M'],
        'number': 4
    },
    'DEU': {
        'codes': ['Deu', 'Dt', '5M'],
        'number': 5
    },
    'JOS': {
        'codes': ['Jsh', 'Jos'],
        'number': 6
    },
    'JDG': {
        'codes': ['Jdg', 'Judg'],
        'number': 7
    },
    'RUT': {
        'codes': ['Ru', 'Rt'],
        'number': 8
    },
    '1SA': {
        'codes': ['1Sa', '1Sm'],
        'number': 9
    },
    '2SA': {
        'codes': ['2Sa', '2Sm'],
        'number': 10
    },
    '1KI': {
        'codes': ['1K'],
        'number': 11
    },
    '2KI': {
        'codes': ['2K'],
        'number': 12
    },
    '1CH': {
        'codes': ['1Ch'],
        'number': 13
    },
    '2CH': {
        'codes': ['2Ch'],
        'number': 14
    },
    'EZR': {
        'codes': ['Ezr'],
        'number': 15
    },
    'NEH': {
        'codes': ['Neh'],
        'number': 16
    },
    'EST': {
        'codes': ['Est'],
        'number': 17
    },
    'JOB': {
        'codes': ['Jb', 'Job'],
        'number': 18
    },
    'PSA': {
        'codes': ['Ps'],
        'number': 19
    },
    'PRO': {
        'codes': ['Pr'],
        'number': 20
    },
    'ECC': {
        'codes': ['Ec', 'Qoh'],
        'number': 21
    },
    'SNG': {
        'codes': ['Sos', 'Son', 'Sng'],
        'number': 22
    },
    'ISA': {
        'codes': ['Isa'],
        'number': 23
    },
    'JER': {
        'codes': ['Jer', 'Jr'],
        'number': 24
    },
    'LAM': {
        'codes': ['Lam', 'Lm'],
        'number': 25
    },
    'EZK': {
        'codes': ['Ezek', 'Ezk'],
        'number': 26
    },
    'DAN': {
        'codes': ['Dn', 'Dan'],
        'number': 27
    },
    'HOS': {
        'codes': ['Hos', 'Hs'],
        'number': 28
    },
    'JOL': {
        'codes': ['Joel', 'Jl', 'Jol'],
        'number': 29
    },
    'AMO': {
        'codes': ['Am'],
        'number': 30
    },
    'OBA': {
        'codes': ['Ob'],
        'number': 31
    },
    'JON': {
        'codes': ['Jon'],
        'number': 32
    },
    'MIC': {
        'codes': ['Mi', 'Mc'],
        'number': 33
    },
    'NAM': {
        'codes': ['Na'],
        'number': 34
    },
    'HAB': {
        'codes': ['Hab'],
        'number': 35
    },
    'ZEP': {
        'codes': ['Zep', 'Zp'],
        'number': 36
    },
    'HAG': {
        'codes': ['Hag', 'Hg'],
        'number': 37
    },
    'ZEC': {
        'codes': ['Zc', 'Zec'],
        'number': 38
    },
    'MAL': {
        'codes': ['Mal', 'Ml'],
        'number': 39
    },
    'MAT': {
        'codes': ['Mt', 'Mat'],
        'number': 40
    },
    'MRK': {
        'codes': ['Mk', 'Mar', 'Mrk'],
        'number': 41
    },
    'LUK': {
        'codes': ['Lk', 'Lu'],
        'number': 42
    },
    'JHN': {
        'codes': ['Jn', 'Joh', 'Jhn'],
        'number': 43
    },
    'ACT': {
        'codes': ['Ac'],
        'number': 44
    },
    'ROM': {
        'codes': ['Ro', 'Rm'],
        'number': 45
    },
    '1CO': {
        'codes': ['1Co'],
        'number': 46
    },
    '2CO': {
        'codes': ['2Co'],
        'number': 47
    },
    'GAL': {
        'codes': ['Gal', 'Gl'],
        'number': 48
    },
    'EPH': {
        'codes': ['Ep'],
        'number': 49
    },
    'PHP': {
        'codes': ['Php', 'Philip'],
        'number': 50
    },
    'COL': {
        'codes': ['Col'],
        'number': 51
    },
    '1TH': {
        'codes': ['1Th'],
        'number': 52
    },
    '2TH': {
        'codes': ['2Th'],
        'number': 53
    },
    '1TI': {
        'codes': ['1Ti', '1Tm'],
        'number': 54
    },
    '2TI': {
        'codes': ['2Ti', '2Tm'],
        'number': 55
    },
    'TIT': {
        'codes': ['Tit'],
        'number': 56
    },
    'PHM': {
        'codes': ['Phile', 'Phm'],
        'number': 57
    },
    'HEB': {
        'codes': ['Hb', 'Heb'],
        'number': 58
    },
    'JAS': {
        'codes': ['Ja', 'Jm'],
        'number': 59
    },
    '1PE': {
        'codes': ['1Pe', '1Pt'],
        'number': 60
    },
    '2PE': {
        'codes': ['2Pe', '2Pt'],
        'number': 61
    },
    '1JN': {
        'codes': ['1Jn', '1Jo', '1Jh'],
        'number': 62
    },
    '2JN': {
        'codes': ['2Jn', '2Jo', '2Jh'],
        'number': 63
    },
    '3JN': {
        'codes': ['3Jn', '3Jo', '3Jh'],
        'number': 64
    },
    'JUD': {
        'codes': ['Ju', 'Jd'],
        'number': 65
    },
    'REV': {
        'codes': ['Rev', 'Rv'],
        'number': 66
    }
}


class ScriptureReference:
    # def __init__(self, start_ref, end_ref=None, bible_filename='eng-engwmbb'):
    #     self.start_ref = self.parse_scripture_reference(start_ref)
    #     self.end_ref = self.parse_scripture_reference(end_ref) if end_ref else self.start_ref
    #     self.bible_url = f"https://raw.githubusercontent.com/BibleNLP/ebible/main/corpus/{bible_filename}.txt"
    #     self.verses = self.get_verses_between_refs()
    def __init__(self, start_ref, end_ref=None, bible_filename='eng-engwmbb', source_type='ebible', versification='eng'):
        self.start_ref = self.parse_scripture_reference(start_ref)
        self.end_ref = self.parse_scripture_reference(end_ref) if end_ref else self.start_ref
        self.bible_filename = bible_filename
        self.source_type = source_type
        self.versification = versification
        if source_type == 'ebible':
            self.bible_url = f"https://raw.githubusercontent.com/BibleNLP/ebible/main/corpus/{bible_filename}.txt"
            self.verses = self.get_verses_between_refs()
        elif source_type == 'usfm':
            self.verses = self.extract_verses_from_usfm()

    @staticmethod
    def get_book_number(book_code):
        return book_codes.get(book_code, {}).get('number', 0)

    @classmethod
    def parse_scripture_reference(cls, input_ref):
        normalized_input = re.sub(r"\s+", "", input_ref).upper()
        regex = re.compile(r"^(\d)?(\D+)(\d+)?(?::(\d+))?(?:-(\d+)?(?::(\d+))?)?$")
        match = regex.match(normalized_input)
        if not match:
            return None

        bookPrefix, bookName, startChapter, startVerse, endChapter, endVerse = match.groups()
        fullBookName = f"{bookPrefix or ''}{bookName}".upper()

        bookCode = next((code for code, details in book_codes.items() if any(fullBookName.startswith(name.upper()) for name in details['codes'])), None)
        if not bookCode:
            return None

        # Validate chapter and verse numbers by checking against the vref.txt data
        startChapter = int(startChapter) if startChapter else 1
        startVerse = int(startVerse) if startVerse else 1
        endChapter = int(endChapter) if endChapter else startChapter
        endVerse = int(endVerse) if endVerse else startVerse  # Default to the same verse if not specified

        return {
            'bookCode': bookCode,
            'startChapter': startChapter,
            'startVerse': startVerse,
            'endChapter': endChapter,
            'endVerse': endVerse
        }


    @cache
    def load_verses(self):
        # read vref lines from vref_eng.txt local file, load into verses list
        with open(os.path.join(os.path.dirname(__file__), 'vref_eng.txt'), 'r') as file:
            lines = file.readlines()
            verses = [line.strip() for line in lines]


        # The commented code below is an attempt to obtain alternate versification by interpreting .vrs files from ebible repo
        # The attempt was unsuccessful, so the code was commented out and the vref_eng.txt file was used instead
        # response = requests.get(f'https://raw.githubusercontent.com/BibleNLP/ebible/main/metadata/{self.versification}.vrs')
        # if response.status_code == 200:
            # lines = response.text.splitlines()
            # verses = []
            # start_processing = False
            
            # for line in lines:
            #     if line.startswith('#') or not line.strip():
            #         continue
            #     if line.startswith('GEN'):
            #         start_processing = True
            #     if start_processing:
            #         parts = line.split()
            #         book = parts[0]
            #         chapters = parts[1:]
            #         for chapter in chapters:
            #             chapter_verses = chapter.split(':')
            #             if len(chapter_verses) != 2:
            #                 continue
            #             chapter_number, verse_count = chapter_verses
            #             try:
            #                 verse_count = int(verse_count)
            #             except ValueError:
            #                 continue
            #             for verse in range(1, verse_count + 1):
            #                 verses.append(f"{book} {chapter_number}:{verse}")
            #         if line.startswith('REV'):
            #             break
           
            return verses
        # else:
        #     return []

    def load_bible_text(self):
        response = requests.get(self.bible_url)
        if response.status_code == 200:
            return response.text.splitlines()
        else:
            return []

    
    def get_verses_between_refs(self):
        verses = self.load_verses()
        bible_text = self.load_bible_text()
        
        def find_index(ref):
            for i, verse in enumerate(verses):
                if ref in verse.split('-'):
                    return i
            return -1
        
        start_ref_str = f"{self.start_ref['bookCode']} {self.start_ref['startChapter']}:{self.start_ref['startVerse']}"
        end_ref_str = f"{self.end_ref['bookCode']} {self.end_ref['endChapter']}:{self.end_ref['endVerse']}"
        
        start_index = find_index(start_ref_str)
        end_index = find_index(end_ref_str)
        
        if start_index == -1 or end_index == -1:
            return []
        
        return [[verses[i].replace(' ', '_'), bible_text[i]] for i in range(start_index, end_index + 1)]

    def extract_verses_from_usfm(self):
        input_directory = self.bible_filename
        verses = []
        files = [f for f in os.listdir(input_directory) if f.endswith('.SFM')]
        
        start_book = self.start_ref['bookCode']
        start_chapter = self.start_ref['startChapter']
        start_verse = self.start_ref['startVerse']
        end_book = self.end_ref['bookCode']
        end_chapter = self.end_ref['endChapter']
        end_verse = self.end_ref['endVerse']

        for file in files:
            input_path = os.path.join(input_directory, file)
            with open(input_path, 'r', encoding='utf-8') as infile:
                book = None
                chapter = None
                for line in infile:
                    if re.match(r'\\id (\w+)', line):
                        book = line.split()[1]
                    if re.match(r'\\c (\d+)', line):
                        chapter = int(line.split()[1])
                    if re.match(r'\\v (\d+)', line):
                        verse_number = int(line.split()[1])
                        
                        # Check if we're within the desired range
                        if (book == start_book and chapter == start_chapter and verse_number >= start_verse) or \
                           (book == start_book and chapter > start_chapter) or \
                           (book_codes[book]['number'] > book_codes[start_book]['number']):
                            if (book == end_book and chapter == end_chapter and verse_number <= end_verse) or \
                               (book == end_book and chapter < end_chapter) or \
                               (book_codes[book]['number'] < book_codes[end_book]['number']):
                                verse_text = re.sub(r'^\\v \d+ ', '', line)
                                verse_text = re.sub(r'\\(\w+) .*?\\\1\*', '', verse_text)
                                verse_text = re.sub(r'[a-zA-Z\\]+', '', verse_text)
                                verse_text = verse_text.strip()
                                if verse_text == 'عفاون سغدات ئي واوال اد':
                                    verse_text = ''
                                formatted_verse = [f"{book}_{chapter}:{verse_number}", verse_text]
                                verses.append(formatted_verse)
                        
                        # Stop if we've reached the end of the desired range
                        if book == end_book and chapter == end_chapter and verse_number >= end_verse:
                            return verses

        return verses

# ebible example usage:

# scripture_ref = ScriptureReference('lev 5:20', 'lev 5:26', "eng-engkjvcpb")
# print("Verses between references:")
# for verse in scripture_ref.verses:
#     print(verse)

# ----------------------------------------------------------

# usfm example usage:

# scripture_ref = ScriptureReference('psa 32:3', bible_filename='folder/containing/SFM/book/files', source_type='usfm').verses

# print(scripture_ref)
