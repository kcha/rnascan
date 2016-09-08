# Copyright 2013 by Michiel de Hoon.  All rights reserved.
# This code is part of the Biopython distribution and governed by its
# license.  Please see the LICENSE file that should have been included
# as part of this package.
# Modified by Copyright 2016 by Kevin Ha
"""This new class inherits Bio.motifs.matrix.PositionSpecificScoringMatrix.
It has been modified to support any kind of Alphabet. This allows us to
perform motif scans on RNA sequence as well as RNA secondary structure.

The main change is the fact that the 'ACGT' hard-coding has been replaced
with whatever letters are in the Alphabet of the matrix. This seems to be
sufficient enough for our purposes.
"""
from Bio.motifs import matrix

# Hack for Python 2.5, isnan and isinf were new in Python 2.6
try:
    from math import isnan as _isnan
except ImportError:
    def _isnan(value):
        # This is tricky due to cross platform float differences
        if str(value).lower() == "nan":
            return True
        return value != value
try:
    from math import isinf as _isinf
except ImportError:
    def _isinf(value):
        # This is tricky due to cross platform float differences
        if str(value).lower().endswith("inf"):
            return True
        return False
# Hack for Python 2.5 on Windows:
try:
    _nan = float("nan")
except ValueError:
    _nan = 1e1000 / 1e1000


class ExtendedPositionSpecificScoringMatrix(matrix.PositionSpecificScoringMatrix):

    def calculate(self, sequence):
        """Add support for other alphabets other than DNA sequence

        Returns the PWM score for a given sequence for all positions.

        Notes:

         - the sequence can only be a DNA sequence // not anymore!
         - the search is performed only on one strand
         - if the sequence and the motif have the same length, a single
           number is returned
         - otherwise, the result is a one-dimensional list or numpy array
        """
        # TODO - Code itself tolerates ambiguous bases (as NaN).
        #if not isinstance(self.alphabet, IUPAC.IUPACUnambiguousDNA):
            #raise ValueError("PSSM has wrong alphabet: %s - Use only with DNA motifs"
                                 #% self.alphabet)
        #if not isinstance(sequence.alphabet, IUPAC.IUPACUnambiguousDNA):
            #raise ValueError("Sequence has wrong alphabet: %r - Use only with DNA sequences"
                                 #% sequence.alphabet)

        # TODO - Force uppercase here and optimise switch statement in C
        # by assuming upper case?
        sequence = str(sequence)
        m = self.length
        n = len(sequence)

        scores = []
        # check if the fast C code can be used
        try:
            import _pwm
        except ImportError:
            # use the slower Python code otherwise
            # The C code handles mixed case so Python version must too:
            sequence = sequence.upper()
            for i in range(n - m + 1):
                score = 0.0
                for position in range(m):
                    letter = sequence[i + position]
                    try:
                        score += self[letter][position]
                    except KeyError:
                        score = _nan
                        break
                scores.append(score)
        else:
            # get the log-odds matrix into a proper shape
            # (each row contains sorted (ACGT) log-odds values)
            logodds = [[self[letter][i] for letter in
                        self.alphabet().letters] for i in range(m)]
            scores = _pwm.calculate(sequence, logodds)
        if len(scores) == 1:
            return scores[0]
        else:
            return scores
