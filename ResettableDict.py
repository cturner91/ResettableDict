import unittest


class ResettableDict:

  def __init__(self):
    self._uncommitted = {}
    self._committed = {}
    self._deleting = set()

  def get(self, key):
    if key in self._uncommitted:
      return self._uncommitted[key]
    elif key in self._committed:
      return self._committed[key]
    else:
      raise KeyError(f'Key {key} not present')

  def set(self, key, value):
    self._uncommitted[key] = value
    if key in self._deleting:
      self._deleting.remove(key)

  def delete(self, key):
    self._deleting.add(key)
    if key in self._uncommitted:
      self._uncommitted.pop(key)
    
  def commit(self):
    self._committed.update({**self._uncommitted})
    for key in self._deleting:
      if key in self._committed:
        self._committed.pop(key)
    self._uncommitted = {}
    self._deleting = set()

  def __len__(self):
    # everything in committed + deduplicated from uncomitted
    keys = (
        set(self._committed.keys())
        .union(self._uncommitted.keys())
        .difference(self._deleting)
    )
    return len(keys)

  def reset(self):
    self._uncommitted = {}
    self._deleting = set()


class TestResettableDict(unittest.TestCase):

  def setUp(self):
    self.rd = ResettableDict()

  def test_set(self):
    self.rd.set('key1', 'value1')
    self.assertIn('key1', self.rd._uncommitted)
    self.assertEqual('value1', self.rd._uncommitted['key1'])
    self.assertNotIn('key1', self.rd._committed)

  def test_get_from_uncommited(self):
    self.rd.set('key1', 'value1')
    result = self.rd.get('key1')
    self.assertEqual('value1', result)

  def test_commit(self):
    self.rd.set('key1', 'value1')
    self.rd.commit()
    self.assertIn('key1', self.rd._committed)
    self.assertNotIn('key1', self.rd._uncommitted)

  def test_get_from_committed(self):
    self.rd.set('key1', 'value1')
    self.rd.commit()
    result = self.rd.get('key1')
    self.assertEqual(len(self.rd._uncommitted), 0)
    self.assertEqual('value1', result)

  def test_get_from_committed_after_second_commit(self):
    self.rd.set('key1', 'value1')
    self.rd.commit()
    self.rd.set('key1', 'valueA')
    result = self.rd.get('key1')
    self.rd.commit()
    self.assertEqual(len(self.rd._uncommitted), 0)
    self.assertEqual('valueA', result)

  def test_from_uncommitted_has_priority(self):
    self.rd.set('key1', 'value1')
    self.rd.commit()
    self.rd.set('key1', 'valueA')
    result = self.rd.get('key1')
    self.assertEqual('valueA', result)

  def test_get_key_not_present(self):
    with self.assertRaises(KeyError):
      self.rd.get('bad key')

  def test_len(self):
    self.rd.set('key1', 'value1')
    self.assertEqual(len(self.rd), 1)
    self.rd.commit()
    self.assertEqual(len(self.rd), 1)

    self.rd.set('key2', 'value2')
    self.assertEqual(len(self.rd), 2)
    self.rd.commit()
    self.assertEqual(len(self.rd), 2)
    
    self.rd.set('key1', 'valueA')
    self.assertEqual(len(self.rd), 2)

  def test_deletes(self):
    self.rd.set('key1', 'value1')
    self.rd.delete('key1')
    self.assertEqual(len(self.rd), 0)

  def test_len_after_reset(self):
    self.rd.set('key1', 'value1')
    self.rd.commit()
    self.rd.delete('key1')
    self.rd.reset()
    self.assertEqual(len(self.rd), 1)

  def test_len_after_delete_no_commit(self):
    self.rd.set('key1', 'value1')
    self.rd.commit()
    self.rd.set('key1', 'valueA')
    self.rd.delete('key1')
    self.assertEqual(len(self.rd), 0)

  def test_reset_no_commits(self):
    self.rd.set('key1', 'value1')
    self.rd.reset()
    self.assertEqual(len(self.rd), 0)

  def test_reset_post_commit(self):
    self.rd.set('key1', 'value1')
    self.rd.commit()
    self.rd.set('key1', 'valueA')
    self.rd.delete('key1')
    self.rd.reset()
    self.assertEqual(len(self.rd), 1)
    result = self.rd.get('key1')
    self.assertEqual('value1', result)

  def test_delete_from_uncommitted_before_commit(self):
    self.rd.set('key1', 'a')
    self.rd.delete('key1')
    self.rd.commit()
    with self.assertRaises(KeyError):
      self.rd.get('key1')
    
  def test_set_after_delete(self):
    self.rd.set('key1', 'a')
    self.rd.delete('key1')
    with self.assertRaises(KeyError):
      self.rd.get('key1')
    self.rd.set('key1', 'b')
    self.assertEqual('b', self.rd.get('key1'))
    self.assertEqual(len(self.rd), 1)


if __name__ == '__main__':
  unittest.main()
