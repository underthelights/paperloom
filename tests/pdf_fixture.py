from pathlib import Path
from pypdf import PdfWriter
from pypdf.generic import DictionaryObject, NameObject, DecodedStreamObject

Path('work').mkdir(exist_ok=True)
writer = PdfWriter()
for number in range(2):
    page = writer.add_blank_page(612, 792)
    font = DictionaryObject({NameObject('/Type'): NameObject('/Font'), NameObject('/Subtype'): NameObject('/Type1'), NameObject('/BaseFont'): NameObject('/Helvetica')})
    page[NameObject('/Resources')] = DictionaryObject({NameObject('/Font'): DictionaryObject({NameObject('/F1'): writer._add_object(font)})})
    content = DecodedStreamObject()
    content.set_data(f'BT /F1 16 Tf 60 700 Td (Selectable research text - page {number+1}) Tj ET'.encode())
    page[NameObject('/Contents')] = writer._add_object(content)
writer.write('work/test-reader.pdf')
