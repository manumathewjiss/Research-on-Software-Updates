from pathlib import Path
import re,json
p=Path(__file__).resolve().parent
b=p/'build_submission.py';s=b.read_text().replace('ylim=(0,3)','ylim=(-.12,2.87)');b.write_text(s)
