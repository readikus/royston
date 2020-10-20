import unittest
from datetime import datetime as dt
import dateutil.relativedelta
import Royston from '../'


testDoc = { 'id': '123', 'body': 'Random text string', 'date': dt.now() }
testDoc2 = { 'id': '456', 'body': 'Antoher random string', 'date': dt.now() }
noIdTestDoc = { 'body': 'Another random string', 'date': dt.now() }
noDateTestDoc = { 'id': '123', 'body': 'Another random string' }


now = dt.now()


usedPhrases = [
  'antoh',
  'antoh,random',
  'antoh,random,string',
  'random',
  'random,string',
  'random,text',
  'random,text,string',
  'string',
  'text',
  'text,string']

findDocOptions = {
  'start': now - dateutil.relativedelta.relativedelta(months = 1),
  'end': dt.now()
}

print('findDocOptions')
print(findDocOptions)

pastHistoryOptions = {
  'start': now - dateutil.relativedelta.relativedelta(years = 2), #moment().subtract(2, 'year'),
  'end': now - dateutil.relativedelta.relativedelta(years = 1) #moment().subtract(1, 'year')
}

print('pastHistoryOptions')
print(pastHistoryOptions)





"""




test('Set intersection code snippet test - to be refactored into a function test', () => {
  const a = [1, 2, 3]
  const b = [4, 3, 2]
  expect(util.intersection(a, b)).toEqual([2, 3])
})

"""
class TestRoyston(unittest.TestCase):

    def test_normalise(self):

        # normalise: normalise a string
        r = new Ramekin()
  expect(r.normalise('My name is Ian')).toEqual('name ian')
})



        self.assertEqual('foo'.upper(), 'FOO')

    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)

if __name__ == '__main__':
    unittest.main()
