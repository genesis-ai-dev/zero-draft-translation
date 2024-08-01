import os
import itertools
from collections import defaultdict
import re
import tiktoken

# dictionary that can be used by other script importing this script
passages = {
    'historical': [
        'acts 2:1',
        'acts 2:8',
    ],
    'prophetic': [
        'rev 6:1',
        'rev 6:8',
    ],
    'poetic': [
        'psa 23:1',
        'psa 23:6',
    ],
    'wisdom': [
        'jas 3:13',
        'jas 3:18',
    ],
    'gospel': [
        'luk 15:11',
        'luk 15:18',
    ],
    'epistle': [
        '1co 13:1',
        '1co 13:8',
    ],
    'apocalyptic': [
        'rev 21:1',
        'rev 21:8',
    ],
    'law': [
        'mat 5:17',
        'mat 5:24',
    ],
}

waha_curriculum = [
  [
    "gen 1:1",
    "gen 2:3"
  ],
  [
    "gen 2:4",
    "gen 2:9"
  ],
  [
    "gen 2:14",
    "gen 2:25"
  ],
  [
    "gen 3:1",
    "gen 3:24"
  ],
  [
    "gen 4:1",
    "gen 4:16"
  ],
  [
    "gen 6:5",
    "gen 9:17"
  ],
  [
    "gen 11:1",
    "gen 11:9"
  ],
  [
    "gen 12:1",
    "gen 12:9"
  ],
  [
    "gen 15:1",
    "gen 15:6"
  ],
  [
    "gen 17:1",
    "gen 17:7"
  ],
  [
    "gen 22:1",
    "gen 22:19"
  ],
  [
    "exo 2:23",
    "exo 3:14"
  ],
  [
    "exo 7:1",
    "exo 7:5"
  ],
  [
    "exo 12:1",
    "exo 12:32"
  ],
  [
    "exo 12:40",
    "exo 12:42"
  ],
  [
    "exo 16:1",
    "exo 16:20"
  ],
  [
    "exo 18:13",
    "exo 18:27"
  ],
  [
    "exo 20:1",
    "exo 20:21"
  ],
  [
    "lev 4:1",
    "lev 4:35"
  ],
  [
    "lev 6:1",
    "lev 6:7"
  ],
  [
    "deu 4:1",
    "deu 4:2"
  ],
  [
    "deu 4:23",
    "deu 4:24"
  ],
  [
    "deu 6:4",
    "deu 6:9"
  ],
  [
    "deu 11:26",
    "deu 11:28"
  ],
  [
    "deu 18:9",
    "deu 18:14"
  ],
  [
    "jdg 2:10",
    "jdg 2:23"
  ],
  [
    "1sa 17:4",
    "1sa 17:11"
  ],
  [
    "1sa 17:32",
    "1sa 17:33"
  ],
  [
    "1sa 17:38",
    "1sa 17:50"
  ],
  [
    "1ch 16:8",
    "1ch 16:36"
  ],
  [
    "neh 1:1",
    "neh 1:11"
  ],
  [
    "neh 4:15",
    "neh 4:16"
  ],
  [
    "est 4:15",
    "est 4:16"
  ],
  [
    "psa 18:3",
    "psa 18:6"
  ],
  [
    "psa 18:16",
    "psa 18:19"
  ],
  [
    "psa 19:7",
    "psa 19:14"
  ],
  [
    "psa 23:1",
    "psa 23:6"
  ],
  [
    "psa 32:1",
    "psa 32:7"
  ],
  [
    "psa 51:1",
    "psa 51:19"
  ],
  [
    "psa 63:1",
    "psa 63:11"
  ],
  [
    "psa 67:1",
    "psa 67:7"
  ],
  [
    "psa 68:3",
    "psa 68:4"
  ],
  [
    "psa 71:19",
    "psa 71:24"
  ],
  [
    "psa 103:1",
    "psa 103:22"
  ],
  [
    "psa 107:1",
    "psa 107:32"
  ],
  [
    "psa 116:1",
    "psa 116:2"
  ],
  [
    "psa 139:1",
    "psa 139:18"
  ],
  [
    "psa 145:1",
    "psa 145:21"
  ],
  [
    "psa 150:1",
    "psa 150:6"
  ],
  [
    "isa 9:1",
    "isa 9:7"
  ],
  [
    "isa 40:26",
    "isa 40:31"
  ],
  [
    "isa 52:13",
    "isa 53:12"
  ],
  [
    "isa 55:10",
    "isa 55:11"
  ],
  [
    "lam 3:19",
    "lam 3:26"
  ],
  [
    "ezk 34:1",
    "ezk 34:16"
  ],
  [
    "dan 3:1",
    "dan 3:30"
  ],
  [
    "jon 1:1",
    "jon 1:3"
  ],
  [
    "jon 3:1",
    "jon 3:10"
  ],
  [
    "mat 1:1",
    "mat 1:25"
  ],
  [
    "mat 2:1",
    "mat 2:23"
  ],
  [
    "mat 3:1",
    "mat 3:17"
  ],
  [
    "mat 4:1",
    "mat 4:11"
  ],
  [
    "mat 4:12",
    "mat 4:22"
  ],
  [
    "mat 4:23",
    "mat 5:32"
  ],
  [
    "mat 5:33",
    "mat 5:48"
  ],
  [
    "mat 6:1",
    "mat 6:18"
  ],
  [
    "mat 6:19",
    "mat 6:34"
  ],
  [
    "mat 7:1",
    "mat 7:14"
  ],
  [
    "mat 7:15",
    "mat 7:29"
  ],
  [
    "mat 8:1",
    "mat 8:13"
  ],
  [
    "mat 8:14",
    "mat 8:27"
  ],
  [
    "mat 8:28",
    "mat 8:34"
  ],
  [
    "mat 9:1",
    "mat 9:17"
  ],
  [
    "mat 9:18",
    "mat 9:34"
  ],
  [
    "mat 9:35",
    "mat 10:42"
  ],
  [
    "mat 11:1",
    "mat 11:19"
  ],
  [
    "mat 11:20",
    "mat 11:30"
  ],
  [
    "mat 12:1",
    "mat 12:14"
  ],
  [
    "mat 12:15",
    "mat 12:21"
  ],
  [
    "mat 12:22",
    "mat 12:37"
  ],
  [
    "mat 12:38",
    "mat 12:50"
  ],
  [
    "mat 13:1",
    "mat 13:23"
  ],
  [
    "mat 13:24",
    "mat 13:35"
  ],
  [
    "mat 13:36",
    "mat 13:52"
  ],
  [
    "mat 13:53",
    "mat 13:58"
  ],
  [
    "mat 14:1",
    "mat 14:21"
  ],
  [
    "mat 14:22",
    "mat 14:36"
  ],
  [
    "mat 15:1",
    "mat 15:20"
  ],
  [
    "mat 15:21",
    "mat 15:31"
  ],
  [
    "mat 15:32",
    "mat 15:39"
  ],
  [
    "mat 16:1",
    "mat 16:12"
  ],
  [
    "mat 16:13",
    "mat 16:20"
  ],
  [
    "mat 16:21",
    "mat 16:28"
  ],
  [
    "mat 17:1",
    "mat 17:13"
  ],
  [
    "mat 17:14",
    "mat 17:21"
  ],
  [
    "mat 17:22",
    "mat 17:27"
  ],
  [
    "mat 18:1",
    "mat 18:14"
  ],
  [
    "mat 18:15",
    "mat 18:35"
  ],
  [
    "mat 19:1",
    "mat 19:15"
  ],
  [
    "mat 19:16",
    "mat 19:30"
  ],
  [
    "mat 20:1",
    "mat 20:16"
  ],
  [
    "mat 20:17",
    "mat 20:34"
  ],
  [
    "mat 21:1",
    "mat 21:17"
  ],
  [
    "mat 21:18",
    "mat 21:27"
  ],
  [
    "mat 21:28",
    "mat 21:46"
  ],
  [
    "mat 22:1",
    "mat 22:14"
  ],
  [
    "mat 22:15",
    "mat 22:22"
  ],
  [
    "mat 22:23",
    "mat 22:33"
  ],
  [
    "mat 22:34",
    "mat 22:46"
  ],
  [
    "mat 23:1",
    "mat 23:15"
  ],
  [
    "mat 23:16",
    "mat 23:39"
  ],
  [
    "mat 24:1",
    "mat 24:51"
  ],
  [
    "mat 25:1",
    "mat 25:13"
  ],
  [
    "mat 25:14",
    "mat 25:30"
  ],
  [
    "mat 25:31",
    "mat 25:46"
  ],
  [
    "mat 26:1",
    "mat 26:16"
  ],
  [
    "mat 26:17",
    "mat 26:30"
  ],
  [
    "mat 26:31",
    "mat 26:56"
  ],
  [
    "mat 26:57",
    "mat 26:75"
  ],
  [
    "mat 27:1",
    "mat 27:10"
  ],
  [
    "mat 27:11",
    "mat 27:26"
  ],
  [
    "mat 27:27",
    "mat 27:44"
  ],
  [
    "mat 27:45",
    "mat 27:66"
  ],
  [
    "mat 28:1",
    "mat 28:15"
  ],
  [
    "mat 28:16",
    "mat 28:20"
  ],
  [
    "mrk 1:1",
    "mrk 1:8"
  ],
  [
    "mrk 1:14",
    "mrk 1:15"
  ],
  [
    "mrk 1:16",
    "mrk 1:18"
  ],
  [
    "mrk 1:35",
    "mrk 1:39"
  ],
  [
    "mrk 2:13",
    "mrk 2:15"
  ],
  [
    "mrk 4:1",
    "mrk 4:9"
  ],
  [
    "mrk 4:35",
    "mrk 5:20"
  ],
  [
    "mrk 6:30",
    "mrk 6:44"
  ],
  [
    "mrk 8:34",
    "mrk 8:38"
  ],
  [
    "mrk 10:42",
    "mrk 10:45"
  ],
  [
    "mrk 10:46",
    "mrk 10:52"
  ],
  [
    "mrk 11:20",
    "mrk 11:26"
  ],
  [
    "mrk 12:28",
    "mrk 12:34"
  ],
  [
    "mrk 13:10",
    "mrk 13:11"
  ],
  [
    "mrk 14:32",
    "mrk 14:38"
  ],
  [
    "mrk 14:53",
    "mrk 14:65"
  ],
  [
    "luk 1:26",
    "luk 1:38"
  ],
  [
    "luk 2:1",
    "luk 2:21"
  ],
  [
    "luk 4:1",
    "luk 4:22"
  ],
  [
    "luk 5:1",
    "luk 5:11"
  ],
  [
    "luk 5:17",
    "luk 5:32"
  ],
  [
    "luk 6:12",
    "luk 6:13"
  ],
  [
    "luk 6:27",
    "luk 6:38"
  ],
  [
    "luk 7:36",
    "luk 7:50"
  ],
  [
    "luk 8:38",
    "luk 8:39"
  ],
  [
    "luk 9:1",
    "luk 9:6"
  ],
  [
    "luk 9:23",
    "luk 9:26"
  ],
  [
    "luk 9:57",
    "luk 9:62"
  ],
  [
    "luk 10:1",
    "luk 10:17"
  ],
  [
    "luk 10:25",
    "luk 10:37"
  ],
  [
    "luk 10:38",
    "luk 10:42"
  ],
  [
    "luk 11:1",
    "luk 11:13"
  ],
  [
    "luk 12:1",
    "luk 12:3"
  ],
  [
    "luk 12:13",
    "luk 12:34"
  ],
  [
    "luk 13:6",
    "luk 13:9"
  ],
  [
    "luk 14:25",
    "luk 14:33"
  ],
  [
    "luk 15:1",
    "luk 15:32"
  ],
  [
    "luk 18:1",
    "luk 18:8"
  ],
  [
    "luk 18:9",
    "luk 18:30"
  ],
  [
    "luk 22:7",
    "luk 22:20"
  ],
  [
    "luk 22:39",
    "luk 22:62"
  ],
  [
    "luk 23:1",
    "luk 23:25"
  ],
  [
    "luk 23:32",
    "luk 24:53"
  ],
  [
    "jhn 1:1",
    "jhn 1:18"
  ],
  [
    "jhn 1:19",
    "jhn 1:37"
  ],
  [
    "jhn 1:43",
    "jhn 1:46"
  ],
  [
    "jhn 3:1",
    "jhn 3:21"
  ],
  [
    "jhn 3:26",
    "jhn 3:30"
  ],
  [
    "jhn 4:1",
    "jhn 4:30"
  ],
  [
    "jhn 4:39",
    "jhn 4:42"
  ],
  [
    "jhn 6:43",
    "jhn 6:45"
  ],
  [
    "jhn 7:37",
    "jhn 7:39"
  ],
  [
    "jhn 8:31",
    "jhn 8:32"
  ],
  [
    "jhn 10:1",
    "jhn 10:18"
  ],
  [
    "jhn 11:1",
    "jhn 11:44"
  ],
  [
    "jhn 13:1",
    "jhn 13:20"
  ],
  [
    "jhn 13:31",
    "jhn 13:35"
  ],
  [
    "jhn 14:1",
    "jhn 14:7"
  ],
  [
    "jhn 14:12",
    "jhn 14:27"
  ],
  [
    "jhn 15:1",
    "jhn 15:17"
  ],
  [
    "jhn 15:18",
    "jhn 15:27"
  ],
  [
    "jhn 16:1",
    "jhn 16:4"
  ],
  [
    "jhn 16:5",
    "jhn 16:15"
  ],
  [
    "jhn 16:32",
    "jhn 16:33"
  ],
  [
    "jhn 17:9",
    "jhn 17:26"
  ],
  [
    "jhn 18:1",
    "jhn 19:16"
  ],
  [
    "jhn 19:28",
    "jhn 19:42"
  ],
  [
    "jhn 20:11",
    "jhn 20:31"
  ],
  [
    "jhn 21:13",
    "jhn 21:17"
  ],
  [
    "act 1:1",
    "act 1:11"
  ],
  [
    "act 2:1",
    "act 2:13"
  ],
  [
    "act 2:36",
    "act 2:47"
  ],
  [
    "act 3:1",
    "act 3:10"
  ],
  [
    "act 4:1",
    "act 4:31"
  ],
  [
    "act 4:32",
    "act 4:37"
  ],
  [
    "act 5:1",
    "act 5:11"
  ],
  [
    "act 5:12",
    "act 5:42"
  ],
  [
    "act 6:1",
    "act 6:7"
  ],
  [
    "act 7:54",
    "act 7:60"
  ],
  [
    "act 8:1",
    "act 8:8"
  ],
  [
    "act 8:14",
    "act 8:17"
  ],
  [
    "act 8:26",
    "act 8:40"
  ],
  [
    "act 9:1",
    "act 9:22"
  ],
  [
    "act 9:26",
    "act 9:28"
  ],
  [
    "act 9:32",
    "act 9:42"
  ],
  [
    "act 10:1",
    "act 10:48"
  ],
  [
    "act 11:25",
    "act 11:26"
  ],
  [
    "act 12:1",
    "act 12:16"
  ],
  [
    "act 12:25",
    "act 13:12"
  ],
  [
    "act 13:42",
    "act 14:11"
  ],
  [
    "act 14:19",
    "act 14:20"
  ],
  [
    "act 14:21",
    "act 14:23"
  ],
  [
    "act 16:6",
    "act 16:10"
  ],
  [
    "act 16:11",
    "act 16:15"
  ],
  [
    "act 16:25",
    "act 16:34"
  ],
  [
    "act 17:16",
    "act 17:34"
  ],
  [
    "act 18:1",
    "act 18:3"
  ],
  [
    "act 18:24",
    "act 18:28"
  ],
  [
    "act 19:13",
    "act 19:20"
  ],
  [
    "act 20:17",
    "act 20:38"
  ],
  [
    "act 21:40",
    "act 22:2"
  ],
  [
    "rom 5:1",
    "rom 5:5"
  ],
  [
    "rom 5:8",
    "rom 5:11"
  ],
  [
    "rom 6:1",
    "rom 6:19"
  ],
  [
    "rom 8:1",
    "rom 8:18"
  ],
  [
    "rom 8:26",
    "rom 8:39"
  ],
  [
    "rom 10:9",
    "rom 10:10"
  ],
  [
    "rom 10:12",
    "rom 10:17"
  ],
  [
    "rom 12:1",
    "rom 12:21"
  ],
  [
    "rom 13:1",
    "rom 13:5"
  ],
  [
    "rom 13:8",
    "rom 13:10"
  ],
  [
    "rom 14:10",
    "rom 14:12"
  ],
  [
    "rom 15:5",
    "rom 15:7"
  ],
  [
    "rom 15:15",
    "rom 15:21"
  ],
  [
    "rom 16:17",
    "rom 16:18"
  ],
  [
    "1co 1:10",
    "1co 1:13"
  ],
  [
    "1co 1:18",
    "1co 1:31"
  ],
  [
    "1co 2:1",
    "1co 2:5"
  ],
  [
    "1co 3:1",
    "1co 3:15"
  ],
  [
    "1co 3:21",
    "1co 3:23"
  ],
  [
    "1co 5:1",
    "1co 5:13"
  ],
  [
    "1co 6:1",
    "1co 6:8"
  ],
  [
    "1co 7:17",
    "1co 7:24"
  ],
  [
    "1co 8:1",
    "1co 8:13"
  ],
  [
    "1co 9:16",
    "1co 9:27"
  ],
  [
    "1co 11:17",
    "1co 11:32"
  ],
  [
    "1co 12:1",
    "1co 12:11"
  ],
  [
    "1co 12:12",
    "1co 12:31"
  ],
  [
    "1co 13:1",
    "1co 13:13"
  ],
  [
    "1co 14:1",
    "1co 14:5"
  ],
  [
    "1co 14:12",
    "1co 14:19"
  ],
  [
    "1co 16:1",
    "1co 16:4"
  ],
  [
    "1co 16:5",
    "1co 16:9"
  ],
  [
    "2co 5:14",
    "2co 5:21"
  ],
  [
    "2co 8:1",
    "2co 8:15"
  ],
  [
    "2co 9:6",
    "2co 9:15"
  ],
  [
    "gal 2:1",
    "gal 2:2"
  ],
  [
    "gal 3:23",
    "gal 4:7"
  ],
  [
    "gal 5:13",
    "gal 5:15"
  ],
  [
    "gal 5:16",
    "gal 5:25"
  ],
  [
    "gal 6:1",
    "gal 6:10"
  ],
  [
    "eph 1:3",
    "eph 1:10"
  ],
  [
    "eph 1:15",
    "eph 1:23"
  ],
  [
    "eph 2:1",
    "eph 2:10"
  ],
  [
    "eph 2:11",
    "eph 2:22"
  ],
  [
    "eph 3:14",
    "eph 3:21"
  ],
  [
    "eph 4:1",
    "eph 4:7"
  ],
  [
    "eph 4:11",
    "eph 4:16"
  ],
  [
    "eph 4:30",
    "eph 4:32"
  ],
  [
    "eph 5:1",
    "eph 5:14"
  ],
  [
    "eph 5:18",
    "eph 5:33"
  ],
  [
    "eph 6:1",
    "eph 6:4"
  ],
  [
    "eph 6:10",
    "eph 6:20"
  ],
  [
    "php 1:1",
    "php 1:6"
  ],
  [
    "php 2:1",
    "php 2:11"
  ],
  [
    "php 3:7",
    "php 3:14"
  ],
  [
    "php 4:6",
    "php 4:7"
  ],
  [
    "php 4:10",
    "php 4:13"
  ],
  [
    "col 1:19",
    "col 1:22"
  ],
  [
    "col 3:1",
    "col 3:17"
  ],
  [
    "col 3:18",
    "col 3:25"
  ],
  [
    "col 4:2",
    "col 4:6"
  ],
  [
    "1th 1:4",
    "1th 1:7"
  ],
  [
    "1th 2:1",
    "1th 2:12"
  ],
  [
    "1th 5:11",
    "1th 5:15"
  ],
  [
    "1ti 4:1",
    "1ti 4:16"
  ],
  [
    "1ti 6:6",
    "1ti 6:10"
  ],
  [
    "2ti 2:1",
    "2ti 2:7"
  ],
  [
    "2ti 2:22",
    "2ti 2:25"
  ],
  [
    "2ti 3:14",
    "2ti 3:17"
  ],
  [
    "tit 1:5",
    "tit 1:9"
  ],
  [
    "heb 2:1",
    "heb 2:4"
  ],
  [
    "heb 4:12",
    "heb 4:13"
  ],
  [
    "heb 10:19",
    "heb 10:22"
  ],
  [
    "heb 10:23",
    "heb 10:25"
  ],
  [
    "heb 11:1",
    "heb 11:40"
  ],
  [
    "heb 12:1",
    "heb 12:2"
  ],
  [
    "jas 1:2",
    "jas 1:18"
  ],
  [
    "jas 1:22",
    "jas 1:27"
  ],
  [
    "jas 2:1",
    "jas 2:9"
  ],
  [
    "jas 2:14",
    "jas 2:26"
  ],
  [
    "jas 3:3",
    "jas 3:12"
  ],
  [
    "jas 4:10",
    "jas 4:12"
  ],
  [
    "jas 5:13",
    "jas 5:20"
  ],
  [
    "1pe 1:3",
    "1pe 1:9"
  ],
  [
    "1pe 2:4",
    "1pe 2:10"
  ],
  [
    "1pe 3:1",
    "1pe 3:9"
  ],
  [
    "1pe 3:12",
    "1pe 3:17"
  ],
  [
    "1pe 4:10",
    "1pe 4:11"
  ],
  [
    "1pe 5:1",
    "1pe 5:11"
  ],
  [
    "1jn 1:5",
    "1jn 2:2"
  ],
  [
    "1jn 2:3",
    "1jn 2:6"
  ],
  [
    "1jn 3:1",
    "1jn 3:3"
  ],
  [
    "rev 5:1",
    "rev 5:14"
  ],
  [
    "rev 7:9",
    "rev 7:17"
  ],
  [
    "rev 19:6",
    "rev 19:9"
  ]
]

lang = {
    'Arabic': {
        'code': 'ara',
        'ebible': 'arb-arbnav',
        'target_file': {
            'Tamazight': 'resources/tmz/arb_tmz_verses.txt',
        },
    },
    'Tamazight': {
        'code': 'tmz',
        'ebible': '',
        'target_file': '',
    },
    'English': {
        'code': 'eng',
        'ebible': 'eng-eng-asv',
        'target_file': {
            'Tamazight': 'resources/tmz/eng_tmz_verses.txt',
        },
    },
}


def get_ngrams(text, n):
    words = text.split()
    return [' '.join(ngram) for ngram in itertools.chain(*[zip(*[words[i:] for i in range(j)]) for j in range(1, n+1)])]

def find_unique_ngrams(text, max_n):
    return set(get_ngrams(text, max_n))

def get_character_ngrams(text, n):
    return [''.join(ngram) for ngram in zip(*[text[i:] for i in range(n)])]

# def find_unique_ngrams(text, max_n):
#     ngrams = set()
#     for n in range(1, max_n + 1):
#         ngrams.update(get_character_ngrams(text, n))
#     return ngrams

def preprocess_text(text):
    # Remove punctuation and normalize whitespace
    return re.sub(r'\s+', ' ', re.sub(r'[^\w\s]', '', text)).strip()
    # For Arabic, we'll just normalize whitespace and remove diacritics
    # text = re.sub(r'\s+', ' ', text).strip()
    # return ''.join(char for char in text if not unicodedata.combining(char))

# def extract_lang_text(line, lang):
#     parts = line.split('__')
#     for part in parts:
#         if f'_{lang}‬' in part:
#             return part.split('‬', 1)[1].strip()
#     return ''  # Return empty string if language not found

def extract_lang_text(line, lang):
    # print(f"Extracting {lang} text from line: {line}")
    parts = line.split('__')
    for part in parts:
        if f'_{lang}' in part:
            # Split on the first occurrence of space after the language tag
            return part.split(' ', 1)[1].strip() if ' ' in part else ''
    return ''  # Return empty string if language not found



def find_relevant_context(all_lines, verse_to_translate, lang, max_n=4, max_number_closest_verses=100):
    verse_to_translate = preprocess_text(verse_to_translate)
    verse_ngrams = find_unique_ngrams(verse_to_translate, max_n)
    
    line_ngrams = []
    scores = [0] * len(all_lines)

    # Process all lines to get ngrams and calculate initial scores
    print(f"For verse: {verse_to_translate}")
    for i, line in enumerate(all_lines):
        lang_text = extract_lang_text(line, lang)
        processed_line = preprocess_text(lang_text)
        line_unique_ngrams = find_unique_ngrams(processed_line, max_n)
        line_ngrams.append(line_unique_ngrams)
        for ngram in line_unique_ngrams:
            if ngram in verse_ngrams:
                scores[i] += 1 / len(processed_line)
    
    # Print top 10 scores
    print("Top 10 scores:")
    for i, score in sorted(enumerate(scores), key=lambda x: x[1], reverse=True)[:10]:
        print(f"Line {i+1}: {all_lines[i].strip()[:100]}... with score {score}")
    
    relevant_lines = []
    relevant_scores = []
    known_ngrams = set()
    selected_indices = set()
    scores_reset = False
    
    while len(relevant_lines) < max_number_closest_verses:
        top_score_index = scores.index(max(scores))
        relevant_lines.append(all_lines[top_score_index])
        relevant_scores.append(scores[top_score_index])
        selected_indices.add(top_score_index)
        
        # Update known ngrams
        new_ngrams = line_ngrams[top_score_index] - known_ngrams
        known_ngrams.update(new_ngrams)
        
        # Print the ngrams contributed by the selected line which exist in the verse
        print(f"Line {len(relevant_lines)} ngrams: {line_ngrams[top_score_index] & verse_ngrams}")
        # Print the score of the selected line
        print(f"Line {len(relevant_lines)} score: {scores[top_score_index]}")
        
        # Set the score of the selected line to 0 to avoid reselection
        scores[top_score_index] = 0
        
        if not scores_reset:
            # Recalculate scores for all remaining lines
            for i, line_unique_ngrams in enumerate(line_ngrams):
                if i not in selected_indices:
                    new_score = sum(1 / len(extract_lang_text(all_lines[i], lang)) 
                                    for ngram in line_unique_ngrams 
                                    if ngram in verse_ngrams and ngram not in known_ngrams)
                    scores[i] = new_score
            
            # If all scores are zero, reset them to their initial values
            if all(score == 0 for score in scores):
                print("Resetting scores...")
                for i, unique_ngrams in enumerate(line_ngrams):
                    if i not in selected_indices:
                        score = sum(1 / len(extract_lang_text(all_lines[i], lang)) 
                                    for ngram in unique_ngrams 
                                    if ngram in verse_ngrams)
                        scores[i] = score
                scores_reset = True

    print(f"Found {len(relevant_lines)} relevant context lines.")
    print("Top 5 matching lines:")
    for i, line in enumerate(relevant_lines[:5], 1):
        print(f"{i}. {line.strip()[:100]}...")

    return '\n'.join(relevant_lines), relevant_scores




def read_files_to_string(path, file_extension='.txt', restricted_list=None):
    if restricted_list is None:
        restricted_list = []
    all_lines = []
    if os.path.isdir(path):
        for filename in os.listdir(path):
            if filename.endswith(file_extension):
                file_path = os.path.join(path, filename)
                with open(file_path, 'r', encoding='utf-8') as file:
                    for line in file:
                        if not any(restricted in line for restricted in restricted_list):
                            all_lines.append(line)
    elif os.path.isfile(path) and path.endswith(file_extension):
        with open(path, 'r', encoding='utf-8') as file:
            for line in file:
                if not any(restricted in line for restricted in restricted_list):
                    all_lines.append(line)
    return all_lines

def count_tokens(string):
    """Returns the number of tokens in a text string using tiktoken's specified encoding."""
    encoding = tiktoken.get_encoding("cl100k_base")
    num_tokens = len(encoding.encode(string))
    return num_tokens