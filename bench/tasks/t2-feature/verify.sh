python3 -m unittest -q && python3 -c "
from store import Store
s=Store(); s.add('a',1.5,'x'); s.add('b',2,'x'); s.add('c',4,'y')
assert s.total_by_category()=={'x':3.5,'y':4}, s.total_by_category()
assert Store().total_by_category()=={}
import re; assert len(re.findall(r'def test', open('test_store.py').read()))>=2
"
