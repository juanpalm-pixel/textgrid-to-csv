import textgrid
from config import INPUT_FILE, OUTPUT_DIR

tgrid = textgrid.read_textgrid(str(INPUT_FILE), fileEncoding="utf-16")
print(tgrid[:3])