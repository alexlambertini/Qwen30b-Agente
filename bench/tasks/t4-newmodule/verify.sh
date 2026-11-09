python3 -m unittest -q && python3 -c "
from slugify import slugify as s
assert s('Olá Mundo!')=='ola-mundo', s('Olá Mundo!')
assert s('  --Ação  & Reação--')=='acao-reacao'
assert s('a___b')=='a-b' and s('')==''
import re; assert len(re.findall(r'def test', open('test_slugify.py').read()))>=4
"
