import pdfplumber, json, os
 
os.makedirs('data/processed', exist_ok=True)
 
print('Extracting WEF Future of Jobs 2025 PDF...')
chunks = []
 
with pdfplumber.open('data/raw/wef_2025.pdf') as pdf:
    print(f'Total pages: {len(pdf.pages)}')
    all_pages = []
    for i, page in enumerate(pdf.pages):
        text = page.extract_text(x_tolerance=3, y_tolerance=3)
        if text and len(text.strip()) > 150:
            all_pages.append((i+1, text.strip()))
    print(f'Pages with extractable text: {len(all_pages)}')
 
if len(all_pages) < 10:
    print('WARNING: Too few pages extracted - PDF may be image-based')
    print('Creating empty wef_chunks.json and continuing...')
    with open('data/processed/wef_chunks.json', 'w') as f:
        json.dump([], f)
else:
    for i in range(0, len(all_pages), 3):
        batch = all_pages[i:i+3]
        page_nums = [str(p[0]) for p in batch]
        combined = chr(10).join(p[1] for p in batch)
        first_line = combined.split(chr(10))[0][:80].strip()
        title = first_line if len(first_line) > 5 else f'Pages {page_nums[0]}'
        content = (f'Source: WEF Future of Jobs Report 2025\n'
                   f'Organization: World Economic Forum (weforum.org)\n'
                   f'Coverage: 55 economies, 22 industry sectors, 14M+ workers\n'
                   f'Section: {title}\n\n{combined[:2500]}')
        chunks.append({'id': f'wef_p{page_nums[0]}', 'source': 'wef_2025',
                       'section': title, 'content': content})
    with open('data/processed/wef_chunks.json', 'w') as f:
        json.dump(chunks, f, indent=2)
    print(f'Done: {len(chunks)} WEF chunks')
