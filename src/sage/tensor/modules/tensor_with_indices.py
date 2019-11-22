r"""
Index notation for tensors

AUTHORS:

- Eric Gourgoulhon, Michal Bejger (2014-2015): initial version

"""
#******************************************************************************
#       Copyright (C) 2015 Eric Gourgoulhon <eric.gourgoulhon@obspm.fr>
#       Copyright (C) 2015 Michal Bejger <bejger@camk.edu.pl>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#  as published by the Free Software Foundation; either version 2 of
#  the License, or (at your option) any later version.
#                  http://www.gnu.org/licenses/
#******************************************************************************

from sage.structure.sage_object import SageObject
import re

class TensorWithIndices(SageObject):
    r"""
    Index notation for tensors.

    This is a technical class to allow one to write some tensor operations
    (contractions and symmetrizations) in index notation.

    INPUT:

    - ``tensor`` -- a tensor (or a tensor field)
    - ``indices`` -- string containing the indices, as single letters; the
      contravariant indices must be stated first and separated from the
      covariant indices by the character ``_``

    EXAMPLES:

    Index representation of tensors on a rank-3 free module::

        sage: M = FiniteRankFreeModule(QQ, 3, name='M')
        sage: e = M.basis('e')
        sage: a = M.tensor((2,0), name='a')
        sage: a[:] = [[1,2,3], [4,5,6], [7,8,9]]
        sage: b = M.tensor((0,2), name='b')
        sage: b[:] = [[-1,2,-3], [-4,5,6], [7,-8,9]]
        sage: t = a*b ; t.set_name('t') ; t
        Type-(2,2) tensor t on the 3-dimensional vector space M over the
         Rational Field
        sage: from sage.tensor.modules.tensor_with_indices import TensorWithIndices
        sage: T = TensorWithIndices(t, '^ij_kl') ; T
        t^ij_kl

    The :class:`TensorWithIndices` object is returned by the square
    bracket operator acting on the tensor and fed with the string specifying
    the indices::

        sage: a['^ij']
        a^ij
        sage: type(a['^ij'])
        <class 'sage.tensor.modules.tensor_with_indices.TensorWithIndices'>
        sage: b['_ef']
        b_ef
        sage: t['^ij_kl']
        t^ij_kl

    The symbol '^' may be omitted, since the distinction between covariant
    and contravariant indices is performed by the index position relative to
    the symbol '_'::

        sage: t['ij_kl']
        t^ij_kl

    Also, LaTeX notation may be used::

        sage: t['^{ij}_{kl}']
        t^ij_kl

    If some operation is asked in the index notation, the resulting tensor
    is returned, not a :class:`TensorWithIndices` object; for instance, for
    a symmetrization::

        sage: s = t['^(ij)_kl'] ; s  # the symmetrization on i,j is indicated by parentheses
        Type-(2,2) tensor on the 3-dimensional vector space M over the
         Rational Field
        sage: s.symmetries()
        symmetry: (0, 1);  no antisymmetry
        sage: s == t.symmetrize(0,1)
        True

    The letters denoting the indices can be chosen freely; since they carry no
    information, they can even be replaced by dots::

        sage: t['^(..)_..'] == t.symmetrize(0,1)
        True

    Similarly, for an antisymmetrization::

        sage: s = t['^ij_[kl]'] ; s # the symmetrization on k,l is indicated by square brackets
        Type-(2,2) tensor on the 3-dimensional vector space M over the Rational
         Field
        sage: s.symmetries()
        no symmetry;  antisymmetry: (2, 3)
        sage: s == t.antisymmetrize(2,3)
        True
        
    On can also perform multiple symetrization-antisymetrizations 
    
        sage: aa = a*a
        sage: aa["(..)(..)"] == aa.symmetrize(0,1).symmetrize(2,3)
        True
        sage: aa == aa["(..)(..)"]+aa["[..][..]"]+aa["(..)[..]"]+aa["[..](..)"]
        True
        
    Another example of an operation indicated by indices is a contraction::

        sage: s = t['^ki_kj'] ; s  # contraction on the repeated index k
        Type-(1,1) tensor on the 3-dimensional vector space M over the Rational
         Field
        sage: s == t.trace(0,2)
        True

    Indices not involved in the contraction may be replaced by dots::

        sage: s == t['^k._k.']
        True

    The contraction of two tensors is indicated by repeated indices and
    the ``*`` operator::

        sage: s = a['^ik'] * b['_kj'] ; s
        Type-(1,1) tensor on the 3-dimensional vector space M over the Rational
         Field
        sage: s == a.contract(1, b, 0)
        True
        sage: s = t['^.k_..'] * b['_.k'] ; s
        Type-(1,3) tensor on the 3-dimensional vector space M over the Rational
         Field
        sage: s == t.contract(1, b, 1)
        True
        sage: t['^{ik}_{jl}']*b['_{mk}'] == s # LaTeX notation
        True

    Contraction on two indices::

        sage: s = a['^kl'] * b['_kl'] ; s
        105
        sage: s == (a*b)['^kl_kl']
        True
        sage: s == (a*b)['_kl^kl']
        True
        sage: s == a.contract(0,1, b, 0,1)
        True

    Some minimal arithmetics::

        sage: 2*a['^ij']
        X^ij
        sage: (2*a['^ij'])._tensor == 2*a
        True
        sage: 2*t['ij_kl']
        X^ij_kl
        sage: +a['^ij']
        +a^ij
        sage: +t['ij_kl']
        +t^ij_kl
        sage: -a['^ij']
        -a^ij
        sage: -t['ij_kl']
        -t^ij_kl
        
        Conventions are checked and non acceptable indices raise 
        ValueError, for instance :

        sage: try: 
        ....:     a["([..])"] # Nested symmetries  
        ....: except ValueError as e:
        ....:     print(e)
        Index conventions not satisfied
        
        sage: try: 
        ....:     a["(.."] # Unbalanced parenthis 
        ....: except ValueError as e:
        ....:     print(e)
        Index conventions not satisfied

        sage: try: 
        ....:     a["ii"] # Repeated indices of the same type
        ....: except ValueError as e:
        ....:     print(e)
        Index conventions not satisfied : repeated indices of same type

        sage: try: 
        ....:     (a*a)["^(ij)^(kl)"] # Multiple indices group of the same type
        ....: except ValueError as e:
        ....:     print(e)
        Index conventions not satisfied
        
        sage: try: 
        ....:     a["^éa"] # accentuated index name
        ....: except ValueError as e:
        ....:     print(e)
        Index conventions not satisfied
        
    """
    def __init__(self, tensor, indices):
        r"""
        TESTS::

            sage: from sage.tensor.modules.tensor_with_indices import TensorWithIndices
            sage: M = FiniteRankFreeModule(QQ, 3, name='M')
            sage: t = M.tensor((2,1), name='t')
            sage: ti = TensorWithIndices(t, 'ab_c')

        We need to skip the pickling test because we can't check equality
        unless the tensor was defined w.r.t. a basis::

            sage: TestSuite(ti).run(skip="_test_pickling")

            sage: e = M.basis('e')
            sage: t[:] = [[[1,2,3], [-4,5,6], [7,8,-9]],
            ....:         [[10,-11,12], [13,14,-15], [16,17,18]],
            ....:         [[19,-20,-21], [-22,23,24], [25,26,-27]]]
            sage: ti = TensorWithIndices(t, 'ab_c')
            sage: TestSuite(ti).run()

        """
        self._tensor = tensor # may be changed below
        self._changed = False # indicates whether self contains an altered
                              # version of the original tensor (True if
                              # symmetries or contractions are indicated in the
                              # indices)
                              
        # Check wether the usual convention for indices, symetries and 
        # contractions are respected. This includes restrictions on the 
        # indices symbols used, non nested (anti)symmetries, 
        # (co/contra)variant  identification of repeated indices, as well  
        # as checking the number of covariant and contravariant indices.
        # Latex notations '{' and '}' are totally ignored.
        # "^{ijkl}_{ib(cd)}"
        # For now authorized symbol list only includes a-z and A-Z
        
        # Suppress all '{' and '}' coming from LaTeX notations:
        indices = indices.replace('{','').replace('}','')
        
        # Check index notation conventions and parse indices
        allowed_pattern = r"(\([a-zA-Z.]{2,}\)|\[[a-zA-Z.]{2,}\]|[a-zA-Z.]+)*"
        con_then_cov = r"^(\^|)" + allowed_pattern + r"(\_"+allowed_pattern + r"|)$"
        cov_then_con = r"^\_" + allowed_pattern + r"(\^"+allowed_pattern + r"|)$"
        if re.match(con_then_cov,indices) is None and re.match(cov_then_con,indices) is None:
            raise ValueError("Index conventions not satisfied")
        elif re.match(con_then_cov,indices):
            try:
                con,cov = indices.replace("^","").split("_")
            except ValueError:
                con = indices.replace("^","")
                cov = ""
        else:
            try:
                cov,con = indices[1:].split("^")
            except ValueError:
                cov = indices[1:]
                con = ""
                
        con_without_sym = (con.replace("(","").replace(")","").replace("[","").replace("]",""))
        cov_without_sym = (cov.replace("(","").replace(")","").replace("[","").replace("]",""))
        if len(con_without_sym) != len(set(con_without_sym))+max(con_without_sym.count(".")-1,0):
            raise ValueError("Index conventions not satisfied : repeated indices of same type")
        if len(cov_without_sym) != len(set(cov_without_sym))+max(cov_without_sym.count(".")-1,0):
            raise ValueError("Index conventions not satisfied : repeated indices of same type")
        
        # Check number of (co/contra)variant indices
        if len(con_without_sym)!=tensor._tensor_type[0]:
            raise IndexError("number of contravariant indices not compatible " +
                             "with the tensor type")
        if len(cov_without_sym)!=tensor._tensor_type[1]:
            raise IndexError("number of covavariant indices not compatible " +
                             "with the tensor type")
        
        #Apply (anti)symmetrizations on contravariant indices
        first_sym_regex = r"(\(|\[)[a-zA-Z.]*[)\]]"
        while re.search(first_sym_regex,con):
            first_sym = re.search(first_sym_regex,con)
            sym1 = first_sym.span()[0]
            sym2 = first_sym.span()[1]-1
            if first_sym.groups()[0] == "(":
                self._tensor = self._tensor.symmetrize(*range(
                    sym1,
                    sym2-1
                ))
            else:
                self._tensor = self._tensor.antisymmetrize(*range(
                    sym1,
                    sym2-1
                ))
            self._changed = True # self does no longer contain the original tensor
            con = con[:sym1]+con[sym1+1:sym2]+con[sym2+1:]     
        self._con = con
        
        #Apply (anti)symmetrizations on contravariant indices
        while re.search(first_sym_regex,cov):
            first_sym = re.search(first_sym_regex,cov)
            sym1 = first_sym.span()[0]
            sym2 = first_sym.span()[1]-1
            if first_sym.groups()[0] == "(":
                self._tensor = self._tensor.symmetrize(*range(
                    self._tensor._tensor_type[0] + sym1,
                    self._tensor._tensor_type[0] + sym2-1
                ))
            else:
                self._tensor = self._tensor.antisymmetrize(*range(
                    self._tensor._tensor_type[0] + sym1,
                    self._tensor._tensor_type[0] + sym2-1
                ))
            self._changed = True # self does no longer contain the original tensor
            cov = cov[:sym1]+cov[sym1+1:sym2]+cov[sym2+1:]     
        self._cov = cov

        # Treatment of possible self-contractions:
        # ---------------------------------------
        contraction_pair_list = []
        for ind in self._con:
            if ind != '.' and ind in self._cov:
                pos1 = self._con.index(ind)
                pos2 = self._tensor._tensor_type[0] + self._cov.index(ind)
                contraction_pair_list.append([pos1, pos2])
        while contraction_pair_list:
            pos1, pos2 = contraction_pair_list.pop()
            self._tensor = self._tensor.trace(pos1, pos2)
            for contraction_pair in contraction_pair_list:
                if contraction_pair[0]> pos1:
                    contraction_pair[0]=contraction_pair[0]-1
                if contraction_pair[1]> pos2:
                    contraction_pair[1]=contraction_pair[1]-1
                contraction_pair[1]=contraction_pair[1]-1
            self._changed = True # self does no longer contain the original
                                 # tensor
            ind = self._con[pos1]
            self._con = self._con.replace(ind, '')
            self._cov = self._cov.replace(ind, '')

    def _repr_(self):
        r"""
        Return a string representation of ``self``.

        EXAMPLES::

            sage: from sage.tensor.modules.tensor_with_indices import TensorWithIndices
            sage: M = FiniteRankFreeModule(QQ, 3, name='M')
            sage: t = M.tensor((2,1), name='t')
            sage: ti = TensorWithIndices(t, 'ab_c')
            sage: ti._repr_()
            't^ab_c'
            sage: t = M.tensor((0,2), name='t')
            sage: ti = TensorWithIndices(t, '_{ij}')
            sage: ti._repr_()
            't_ij'

        """
        name = 'X'
        if hasattr(self._tensor, '_name'):
            if self._tensor._name is not None:
                name = self._tensor._name
        if self._con == '':
            if self._cov == '':
                return 'scalar'
            else:
                return name + '_' + self._cov
        elif self._cov == '':
            return name + '^' + self._con
        else:
            return name + '^' + self._con + '_' + self._cov

    def update(self):
        r"""
        Return the tensor contains in ``self`` if it differs from that used
        for creating ``self``, otherwise return ``self``.

        EXAMPLES::

            sage: from sage.tensor.modules.tensor_with_indices import TensorWithIndices
            sage: M = FiniteRankFreeModule(QQ, 3, name='M')
            sage: e = M.basis('e')
            sage: a = M.tensor((1,1),  name='a')
            sage: a[:] = [[1,-2,3], [-4,5,-6], [7,-8,9]]
            sage: a_ind = TensorWithIndices(a, 'i_j') ; a_ind
            a^i_j
            sage: a_ind.update()
            a^i_j
            sage: a_ind.update() is a_ind
            True
            sage: a_ind = TensorWithIndices(a, 'k_k') ; a_ind
            scalar
            sage: a_ind.update()
            15

        """
        if self._changed:
            return self._tensor
        else:
            return self

    def __eq__(self, other):
        """
        Check equality.

        TESTS::

            sage: from sage.tensor.modules.tensor_with_indices import TensorWithIndices
            sage: M = FiniteRankFreeModule(QQ, 3, name='M')
            sage: t = M.tensor((2,1), name='t')
            sage: ti = TensorWithIndices(t, 'ab_c')
            sage: ti == TensorWithIndices(t, '^{ab}_c')
            True
            sage: ti == TensorWithIndices(t, 'ac_b')
            False
            sage: tp = M.tensor((2,1))
            sage: ti == TensorWithIndices(tp, 'ab_c')
            Traceback (most recent call last):
            ...
            ValueError: no common basis for the comparison
        """
        if not isinstance(other, TensorWithIndices):
            return False
        return (self._tensor == other._tensor
                and self._con == other._con
                and self._cov == other._cov)

    def __ne__(self, other):
        """
        Check not equals.

        TESTS::

            sage: from sage.tensor.modules.tensor_with_indices import TensorWithIndices
            sage: M = FiniteRankFreeModule(QQ, 3, name='M')
            sage: t = M.tensor((2,1), name='t')
            sage: ti = TensorWithIndices(t, 'ab_c')
            sage: ti != TensorWithIndices(t, '^{ab}_c')
            False
            sage: ti != TensorWithIndices(t, 'ac_b')
            True
        """
        return not self == other

    def __mul__(self, other):
        r"""
        Tensor product or contraction on specified indices.

        EXAMPLES::

            sage: from sage.tensor.modules.tensor_with_indices import TensorWithIndices
            sage: M = FiniteRankFreeModule(QQ, 3, name='M')
            sage: e = M.basis('e')
            sage: a = M.tensor((2,0), name='a')
            sage: a[:] = [[1,-2,3], [-4,5,-6], [7,-8,9]]
            sage: b = M.linear_form(name='b')
            sage: b[:] = [4,2,1]
            sage: ai = TensorWithIndices(a, '^ij')
            sage: bi = TensorWithIndices(b, '_k')
            sage: s = ai.__mul__(bi) ; s  # no repeated indices ==> tensor product
            Type-(2,1) tensor a*b on the 3-dimensional vector space M over the
             Rational Field
            sage: s == a*b
            True
            sage: s[:]
            [[[4, 2, 1], [-8, -4, -2], [12, 6, 3]],
             [[-16, -8, -4], [20, 10, 5], [-24, -12, -6]],
             [[28, 14, 7], [-32, -16, -8], [36, 18, 9]]]
            sage: ai = TensorWithIndices(a, '^kj')
            sage: s = ai.__mul__(bi) ; s  # repeated index k ==> contraction
            Element of the 3-dimensional vector space M over the Rational Field
            sage: s == a.contract(0, b)
            True
            sage: s[:]
            [3, -6, 9]

        """
        if not isinstance(other, TensorWithIndices):
            raise TypeError("the second item of * must be a tensor with " +
                            "specified indices")
        contraction_pairs = []
        for ind in self._con:
            if ind != '.':
                if  ind in other._cov:
                    pos1 = self._con.index(ind)
                    pos2 = other._tensor._tensor_type[0] + other._cov.index(ind)
                    contraction_pairs.append((pos1, pos2))
                if ind in other._con:
                    raise IndexError("the index {} appears twice ".format(ind)
                                     + "in a contravariant position")
        for ind in self._cov:
            if ind != '.':
                if ind in other._con:
                    pos1 = self._tensor._tensor_type[0] + self._cov.index(ind)
                    pos2 = other._con.index(ind)
                    contraction_pairs.append((pos1, pos2))
                if ind in other._cov:
                    raise IndexError("the index {} appears twice ".format(ind)
                                     + "in a covariant position")
        if not contraction_pairs:
            # No contraction is performed: the tensor product is returned
            return self._tensor * other._tensor
        ncontr = len(contraction_pairs)
        pos1 = [contraction_pairs[i][0] for i in range(ncontr)]
        pos2 = [contraction_pairs[i][1] for i in range(ncontr)]
        args = pos1 + [other._tensor] + pos2
        return self._tensor.contract(*args)

    def __rmul__(self, other):
        r"""
        Multiplication on the left by ``other``.

        EXAMPLES::

            sage: from sage.tensor.modules.tensor_with_indices import TensorWithIndices
            sage: M = FiniteRankFreeModule(QQ, 3, name='M')
            sage: e = M.basis('e')
            sage: a = M.tensor((2,1), name='a')
            sage: a[0,2,1], a[1,2,0] = 7, -4
            sage: ai = TensorWithIndices(a, 'ij_k')
            sage: s = ai.__rmul__(3) ; s
            X^ij_k
            sage: s._tensor == 3*a
            True

        """
        return TensorWithIndices(other*self._tensor,
                                 self._con + '_' + self._cov)

    def __pos__(self):
        r"""
        Unary plus operator.

        OUTPUT:

        - an exact copy of ``self``

        EXAMPLES::

            sage: from sage.tensor.modules.tensor_with_indices import TensorWithIndices
            sage: M = FiniteRankFreeModule(QQ, 3, name='M')
            sage: e = M.basis('e')
            sage: a = M.tensor((2,1), name='a')
            sage: a[0,2,1], a[1,2,0] = 7, -4
            sage: ai = TensorWithIndices(a, 'ij_k')
            sage: s = ai.__pos__() ; s
            +a^ij_k
            sage: s._tensor == a
            True

        """
        return TensorWithIndices(+self._tensor,
                                 self._con + '_' + self._cov)

    def __neg__(self):
        r"""
        Unary minus operator.

        OUTPUT:

        - negative of ``self``

        EXAMPLES::

            sage: from sage.tensor.modules.tensor_with_indices import TensorWithIndices
            sage: M = FiniteRankFreeModule(QQ, 3, name='M')
            sage: e = M.basis('e')
            sage: a = M.tensor((2,1), name='a')
            sage: a[0,2,1], a[1,2,0] = 7, -4
            sage: ai = TensorWithIndices(a, 'ij_k')
            sage: s = ai.__neg__() ; s
            -a^ij_k
            sage: s._tensor == -a
            True

        """
        return TensorWithIndices(-self._tensor,
                                 self._con + '_' + self._cov)
