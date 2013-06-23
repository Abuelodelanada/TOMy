# Copyright 2007-2013 Facundo Batista
# Code adapted from original after post
#   http://www.taniquetil.com.ar/plog/post/1/310
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 3, as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranties of
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# For further info, check  https://launchpad.net/ftrie

"""A Fucked Trie, or Fluorescent Trie as it's more polite. A Word Tree."""


class WordTree(object):
    """A "trie" of words that carry a payload.

    It's loaded at init, must receive a dict where the 'words' are
    keys, and the 'payloads' the values.

    The words must be unicode (this is validated at building time).
    """

    def __init__(self, wordsdata):
        self.data = self._fill(sorted(wordsdata.iteritems()))

    def _fill(self, wordsdata):
        """Fill the tree."""
        data = {}

        # first filter the one that ends here (if any)
        for i, (word, payload) in enumerate(wordsdata):
            if word == u"":
                data[None] = payload
                del wordsdata[i]   # change what iterating, don't care
                break              # because we exit the loop

        firstword, firstpayload = wordsdata[0]
        assert isinstance(firstword, unicode), "All words must be unicode"
        prvprim = firstword[0]
        all_rests = [(firstword[1:], firstpayload)]
        morethanone = False
        for word, payload in wordsdata[1:]:
            assert isinstance(word, unicode), "All words must be unicode"
            prim, rest = word[0], word[1:]
            if prim == prvprim:
                all_rests.append((rest, payload))
                morethanone = True
                continue

            if morethanone:
                data[prvprim] = self._fill(all_rests)
            else:
                data[prvprim] = all_rests[0]  # end of branch, a tuple
            prvprim = prim
            all_rests = [(rest, payload)]
            morethanone = False

        if morethanone:
            data[prvprim] = self._fill(all_rests)
        else:
            data[prvprim] = all_rests[0]  # end of branch, a tuple
        return data

    def search(self, tosearch):
        """Search the tree.

        It returns a list of (word, payload) where is word has as prefix the
        searched token.
        """
        partial = []
        dic = self.data
        for char in tosearch:
            # dic is string in some "raw branches at the end"
            if isinstance(dic, tuple):
                wordend, payload = dic
                r = u"".join(partial) + wordend
                if r == tosearch:
                    return [(r, payload)]
                else:
                    return []
            try:
                dic = dic[char]
            except KeyError:
                # failed to find the next character in the search, so the
                # search is not prefix of anything stored
                return []

            # go on! store the found character
            partial.append(char)

        if isinstance(dic, tuple):
            # the remaining stuff is a raw branch, we're done
            wordend, payload = dic
            r = u"".join(partial) + wordend
            return [(r, payload)]

        # at this point we know that the searched token is a prefix of
        # several stuff, let's build the result
        result = []

        def build(dic, base):
            """Build the different result alternatives."""
            for char, nextdic in dic.items():
                if char is None:
                    result.append((base, nextdic))
                    continue

                if isinstance(nextdic, tuple):
                    wordend, payload = nextdic
                    result.append((base + char + wordend, payload))
                else:
                    build(nextdic, base + char)

        build(dic, tosearch)
        return result
