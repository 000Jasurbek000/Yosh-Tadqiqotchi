"""settings.py ichidagi git conflict belgilarini olib tashlaydi. Server (lokal) tomonini qoldiradi."""
from pathlib import Path


def clean(text: str) -> str:
    lines = text.splitlines(True)
    out = []
    mode = 'keep'  # keep | drop
    stash_style = 'Updated upstream' in text
    for line in lines:
        if line.startswith('<<<<<<<'):
            # stash: Updated upstream = GitHub, tashlanadi
            # merge: HEAD = server, saqlanadi
            if stash_style or 'Updated upstream' in line:
                mode = 'drop'
            else:
                mode = 'keep'
            continue
        if line.startswith('======='):
            mode = 'keep' if mode == 'drop' else 'drop'
            continue
        if line.startswith('>>>>>>>'):
            mode = 'keep'
            continue
        if mode == 'keep':
            out.append(line)
    return ''.join(out)


def main():
    path = Path('xalikova_project/settings.py')
    raw = path.read_text(encoding='utf-8')
    if '<<<<<<<' not in raw:
        print('Conflict yoq — settings.py allaqachon toza.')
        return
    path.write_text(clean(raw), encoding='utf-8')
    print('settings.py tozalandi. GitHub tomoni tashlandi, server tomoni qoldi.')


if __name__ == '__main__':
    main()
