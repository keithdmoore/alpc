

class ACompleter(object):
   '''
      class to maintain and access a  list of autocomplete words 
      for the A&L Programming Challenge.
   '''

   def __init__(self, words=None):
      '''
         @param words is one of:
            - a list of words to remember
            - a file object that contains words 
            - the name of a file that contains words
      '''
      # store the words as lists of strings inside a dict keyed by the
      # first letter of the words in that list, like:
      # { 'a': ['aardvark', academy'], 'b': ['baal', 'buxtehude'] }
      self.data = {}
      try:
         words = open(words, "rt")
      except TypeError:
         # 'words' wasn't a filename. Ignore the exception and keep trying.
         pass
      try:
         # maybe it's an open file object.
         for line in words.readlines():
            # accept files with multiple words per line and as many lines as 
            # there are.
            lineWords = line.split()
            self.Add(lineWords, False)
         self.Sort()
      except AttributeError:
         # maybe it's a list of words.
         self.Add(words)

   def Sort(self):
      '''
         sort each of the word lists.
      '''
      for letter in self.data.keys():
         self.data[letter].sort()

   def Add(self, word, sort=True):
      '''
         @param word A single word or list of words to add to our data.
         @param sort boolean, should we re-sort the list of words after 
            adding this one?
         >>> c = ACompleter()
         >>> c.Add('banana')
         >>> c.data
         {'b': ['banana']}

         Make sure that multiple adds don't create duplicate data
         >>> c.Add('banana')
         >>> c.data
         {'b': ['banana']}

         Check the sorting
         >>> c.Add('bag')
         >>> c.data
         {'b': ['bag', 'banana']}

         We also force everything to lowercase on addition
         >>> c.Add('barnacle')
         >>> c.data
         {'b': ['bag', 'banana', 'barnacle']}

         Add words from a list
         >>> l = ['alpha', 'aardvark', 'zoetrope']
         >>> c.Add(l)
         >>> c.data['a']
         ['aardvark', 'alpha']
         >>> c.data['z']
         ['zoetrope']
         >>> c.data['y']
         Traceback (most recent call last):
            ...
         KeyError: 'y'
      '''
      if hasattr(word, 'append'):
         # this is a list of words -- add each one in turn.
         for w in word:
            self.Add(w, False)
         self.Sort()
      else:
         if word:
            word = str(word).lower()
            initial = word[0]
            words = set(self.data.setdefault(initial, []))
            words.add(word)
            self.data[initial] = list(words)
            if sort:
               self.Sort()

   def Complete(self, partial):
      '''
         @param partial The root/prefix string we're looking for.
         @returns a list of words, possibly empty.

         >>> c = ACompleter(['art', 'artistic', 'artist', 'artisan'])
         >>> c.Add(['arthur', 'arthritis', 'armature'])
         >>> c.Complete('b')
         []
         >>> l = c.Complete('a')
         >>> len(l)
         7
         >>> l = c.Complete('art')
         >>> len(l)
         6
         >>> l = c.Complete('arti')
         >>> len(l)
         3
         >>> l
         ['artisan', 'artist', 'artistic']
      '''
      matches = []
      partial = str(partial).lower()
      if partial:
         initial = partial[0]
         try:
            words = self.data[initial]
            # yes, in a real system, we'd use a more clever data structure
            # than a sorted list and linear search...
            matches = [word for word in words if word.startswith(partial)]
         except KeyError:
            # no words starting with that letter!
            pass
      return matches







if __name__ == "__main__":
   import doctest
   doctest.testmod()


