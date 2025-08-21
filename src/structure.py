
import pytesseract


def scan_n_structure(img):

    tsv = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)

    words = []
    n = len(tsv['text'])
    for i in range(n):
        txt = tsv['text'][i].strip()
        if not txt:
            continue
        x, y, w, h = tsv['left'][i], tsv['top'][i], tsv['width'][i], tsv['height'][i]
        words.append({"text": txt, "x": x, "y": y, "w": w, "h": h})

    lines = []
    y_tolerance = 10
    for w in sorted(words, key=lambda r: (r['y'], r['x'])):
        placed = False
        for line in lines:
            if abs((w['y'] + w['h']/2) - line['y_center']) <= y_tolerance:
                line['words'].append(w)
                all_centers = [(u['y']+u['h']/2) for u in line['words']]
                line['y_center'] = sum(all_centers)/len(all_centers)
                placed = True
                break
        if not placed:
            lines.append({"words":[w], "y_center": w['y']+w['h']/2})

    lines = sorted(lines, key=lambda line: line['y_center'])
    paragraphs = []
    cur_para = []
    last_y = None
    para_gap = 20   # may require adjustment
    for ln in lines:
        text_line = " ".join([w['text'] for w in sorted(ln['words'], key=lambda r: r['x'])])
        if last_y is None:
            cur_para.append(text_line)
        elif (ln['y_center'] - last_y) > para_gap:
            paragraphs.append("\n".join(cur_para))
            cur_para = [text_line]
        else:
            cur_para.append(text_line)
        last_y = ln['y_center']
    if cur_para:
        paragraphs.append("\n".join(cur_para))

    # not actual md, just padded txt
    md = "\n\n".join(paragraphs)
    print(md)
