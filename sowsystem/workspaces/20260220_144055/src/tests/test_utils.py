```python
import unittest
from src.utils.file_utils import get_file_path

class TestUtils(unittest.TestCase):
    def test_get_file_path(self):
        path = get_file_path('relative/path')
        self.assertTrue(os.path.exists(path))

if __name__ == "__main__":
    unittest.main()
```