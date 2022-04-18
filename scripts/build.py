#!/usr/bin/env python

import csv
from typing import Mapping


COLS = [
    # 「|」前為 MDB 內備註，後為 TXT 說明
    # 1. 舊版總序號(漏四小韻) | 舊版(unicode3.1字符集第一版)小韻總序號。缺錄:丑戾切、no=2381，烏懈切、no=2455，他德切、no=3728，盧合、no=3784四小韻。
    "no''",
    'no',  # 2. 小韻總序號 | 刊正小韻總序號
    'cet',   # 3. 反切 | 反切
    'glyphs',  # 4. 小韻收字 | 小韻内辭目（headwords）
    'sum',  # 5. 小韻字數 | 小韻所收辭目數
    'validation',  # 6. 校驗標記 | 校驗表記
    'miuk',  # 7. 廣韻標目 | 韻目。阿拉伯數碼「X.XX」，小數點前一位爲卷號，小數點後兩位爲韻目。如「4.11暮」意爲「第四卷去聲、十一暮韻」。
    'sievhiunnNO',  # 8. 小韻分韻序號 | 小韻在韻中的序號。如「『德紅切』『東』爲『東』韻第一小韻，『薄紅切』『蓬』爲『東』韻第三十一小韻。」古書向無頁碼，兼且版本紛紜卷帙雜沓難於取捨，故此僅錄標目序號不記頁碼。
    'sjeng',  # 9. 聲紐 | 聲紐
    'xu',  # 10. 呼(開合口) | 呼（開合口）
    'tonk',  # 11. 四等 | 等
    'hiunnbuu',  # 12. 韻部，四聲劃一 | 韻部（四聲劃一）
    'dew',  # 13. 四聲 | 聲調
    'romA',  # 14. Polyhedron羅馬字 | Polyhedron擬羅馬字
    'romB',  # 15. 有女同車羅馬字 | 有女同車擬羅馬字
    'note',  # 16. 備註1 | 舊版備註
    'note2',  # 17. 備註2 | 本次復校備註
    'miuknote',  # 18. 特殊小韻的標目說明 | 特殊小韻韻目歸屬說明
    "v'n'others",  # 19. 變體、非辭目（headword）「又作」字、集韻補字、常用新字備考 | 見於廣韻辭條中的辭目重文、取自集韻的增補和異體字、等價異形字、備考新字等
    '代用',  # 20. Unicode闋錄字 | unicode3.1未收字的準IDS（Ideographic Desciption Characters）描述：H=⿰、Z=⿱、P=⿸、E=⿳、V=某字unicode缺載之變體
]


def compare(mstr: str, tstr: str) -> bool:
    return mstr == ''.join('??' if ord(c) > 0xffff
                           else c
                           for c in tstr.replace('\ufffd', '?'))


mdb_rows: dict[str, Mapping[str, str]] = {}

with open('scripts/mdbdump.csv') as fin:
    for trow in csv.DictReader(fin):
        key = trow['no']
        assert key not in mdb_rows
        mdb_rows[key] = trow


SENTINEL = object()

header: str
data: list[list[str]] = []

with open('original/Kuankhiunn0704.txt', errors='replace') as fin:
    header_lines = []
    for i in range(27):
        header_lines.append(next(fin))
    header = ''.join(header_lines)

    keys = set()
    for line in fin:
        trow = line.rstrip('\n').replace('\ufffd' * 3, '\ufffd').split('|')

        key = trow[1]
        assert key not in keys
        assert key in mdb_rows
        keys.add(key)

        mrow = mdb_rows[key]
        assert sum(v.count('|') for v in mrow.values()) == len(trow) - 20

        row = []
        it = iter(trow)
        for col in COLS:
            mfield = mrow[col]
            parts = [next(it)]
            for i in range(mfield.count('|')):
                parts.append(next(it))
            field = '|'.join(parts)
            assert compare(mfield, field), (mrow, trow, mfield, parts)
            row.append(field)
        assert next(it, SENTINEL) is SENTINEL
        assert len(row) == 20
        data.append(row)

    assert len(keys) == len(mdb_rows)

with open('Kuankhiunn0704-semicolon.txt', 'w', newline='') as fout:
    print(header.replace('|', ';'), end='', file=fout)
    for row in data:
        assert not any(';' in x for x in row)
        print(';'.join(row), file=fout)
