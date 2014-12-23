import sys
import numpy as np
import mpmath as mp

mp.dps = 100

from Optimizer import *

DEBUG = False

class Dictionary:
  UNBOUNDEDCODE = -1
  INFEASIBLECODE = -2
  FINALCODE = 0
  STANDARDCODE = 1
  
  UNBOUNDED = "UNBOUNDED"
  INFEASIBLE = "INFEASIBLE"
  FINAL = "FINAL"
  STANDARD = "STANDARD"
  
  def __init__(self, m, n, basicIdx, nonBasicIdx, b, A, c, z, tolerance = mp.power(10,-10)):
    self.m = m
    self.n = n
    self.basicIdx = basicIdx
    self.nonBasicIdx = nonBasicIdx
    self.b = b
    self.A = A
    self.c = c
    self.z = z
    self.statuscode = Dictionary.STANDARDCODE
    self.status = Dictionary.STANDARD
    #self.tolerance = mp.mpf(str(tolerance))
    self.tolerance = tolerance

  def __str__(self):
    strRet = "m: " + str(self.m) + ", n: " + str(self.n) + "\n" \
     + "Basic Indexes: " + str(self.basicIdx) + "\n" \
     + "Non-basic Indexes: " + str(self.nonBasicIdx) + "\n" \
     + "A: " + str(self.A) + "\n" \
     + "b: " + str(self.b) + "\n" \
     + "c: " + str(self.c) + "\n" \
     + "z: " + str(self.z) + "\n" \
     + "status: " + str(self.statuscode) + " - " + str(self.status) + "\n"
    
    return strRet
  
  @staticmethod
  def _distance(num):
    return mp.fabs(mp.fsub(num, mp.nint(num)))

  # check if a given vector has a negative value (considering the tolerance)
  def _hasNegative(self, vec):
    for i in range(len(vec)):
      if vec[i] <= mp.fneg(self.tolerance):
        return True
    
    return False
  
  # return the upper bound for the increase of the entering variable
  # given a specific basic variable (row: basic value + coefficient for the entering variable)
  def _getUpperBound(self, basic_value, coeff):
    if coeff >= mp.fneg(self.tolerance):
      return mp.inf
    else:
      return mp.fneg(mp.fdiv(basic_value, coeff))
  
  # find the entering variable using the Bland's rule
  # returns the index of the entering variable and its position on the vector of non-basic indexes
  def _findEntering(self):
    idx = mp.inf
    pos = -1
    
    for i in range(self.n):
      col = self.A[:,i]
      hasNegastive = self._hasNegative(col)
      # if UNBOUNDED: an entering variable has no leaving variable associated
      if self.c[i] >= self.tolerance and not hasNegastive:
        return Dictionary.UNBOUNDEDCODE, Dictionary.UNBOUNDED
      # if the entering variable has at least one leaving variable associated and
      # has a lower index than the current entering variable selected (Bland's rule)
      elif self.c[i] >= self.tolerance and hasNegastive and self.nonBasicIdx[i] < idx:
        idx = self.nonBasicIdx[i]
        pos = i
    
    if pos >= 0:
      return idx, pos
    else:
      return Dictionary.FINALCODE, Dictionary.FINAL
  
  # find the leaving variable using the Bland's rule
  # returns the index of the leaving variable and its position on the vector of basic indexes
  def _findLeaving(self, enteringPos):
    increase = mp.fsub(mp.inf,'1')
    idx = mp.inf
    pos = -1
    
    # find the variable with the smaller upper bound to the increase in the entering variable
    # if there are multiple choices, set the one with the smaller index on the list of basic indexes
    for i in range(self.m):
      upperBound = self._getUpperBound(self.b[i], self.A[i, enteringPos])
      
      # if this variable impose more constraint on the increase of the entering variable
      # than the current leaving variable, then this is the new leaving variable
      if upperBound <= mp.fsub(increase, self.tolerance):
        idx = self.basicIdx[i]
        pos = i
        increase = upperBound
      # if this variable impose the same constraint on the increase of the entering variable
      # than the current leaving variable  (considering the tolerance) but has a lower index, 
      # then this is the new leaving variable
      elif mp.almosteq(upperBound, increase, self.tolerance) and self.basicIdx[i] < idx:
        idx = self.basicIdx[i]
        pos = i
    
    if pos >= 0:
      return idx, pos
    else:
      return Dictionary.UNBOUNDEDCODE, Dictionary.UNBOUNDED
  
  # get the vector used to compute the new Z and c values
  def _getAuxOjectiveVector(self):
    return np.append(self.z, self.c)
  
  # get the matrix used to compute the new b and A values
  def _getAuxMatrix(self):
    nRows = len(self.b)
    A_aux = []
    
    for i in range(nRows):
      row_aux = np.append(self.b[i], self.A[i,:])
      A_aux.append(row_aux)
    
    return np.array(A_aux)
  
  # rearrange the dictionary given the entering and leaving variables
  # returns the new dictionary
  def _rearrangeDictionary(self, enteringIdx, enteringPos, leavingIdx, leavingPos):
    
    newNonBasicIdx = self.nonBasicIdx
    newNonBasicIdx[enteringPos] = leavingIdx
    
    newBasicIdx = self.basicIdx
    newBasicIdx[leavingPos] = enteringIdx
    
    A_aux = self._getAuxMatrix()
    
    enteringPos = enteringPos+1
    coeffEnteringVar = mp.fmul(A_aux[leavingPos, enteringPos], mp.mpf('-1.0'))
    A_aux[leavingPos, enteringPos] = mp.mpf('-1.0')
    A_aux[leavingPos, :] = A_aux[leavingPos, :] / coeffEnteringVar
    
    # compute the new coefficients of the A matrix according to the new value of the entering variable
    for i in range(self.m):
      if i != leavingPos:
        coeff = A_aux[i, enteringPos]
        A_aux[i, enteringPos] = mp.mpf('0')
        A_aux[i, :] += coeff*A_aux[leavingPos, :]
    
    C_aux = self._getAuxOjectiveVector()
    coeffEntering = C_aux[enteringPos]
    C_aux[enteringPos] = 0
    
    # compute the new value of the C vector according to the new value of the entering variable
    C_aux += coeffEntering*A_aux[leavingPos, :]
    
    newb = A_aux[:,0]
    newA = A_aux[:,1:self.n+1]
    
    newz = C_aux[0]
    newc = C_aux[1:self.n+1]
    
    # returns the new dictionary generated by the pivoting process
    return Dictionary(self.m, self.n, newBasicIdx, newNonBasicIdx, newb, newA, newc, newz, self.tolerance)
  
  # execute the pivoting of a dictionary
  # returns the entering and leaving variable indexes and the 
  # new dictionary generated by the pivoting process
  def pivot(self):
    enteringIdx, enteringPos = self._findEntering()
    
    if enteringIdx <= 0:
      self.statuscode = enteringIdx
      self.status = enteringPos
      return enteringIdx, enteringPos, self
    
    leavingIdx, leavingPos = self._findLeaving(enteringPos)
    
    if leavingIdx <= 0:
      self.statuscode = leavingIdx
      self.status = leavingPos
      return enteringIdx, leavingPos, self
    
    # rearrange the dictionary and return the new one resulted
    return enteringIdx, leavingIdx, self._rearrangeDictionary(enteringIdx, enteringPos, leavingIdx, leavingPos)
  
  # return the dual of this dictionary
  def dual(self):
    return Dictionary(self.n, self.m, np.copy(self.nonBasicIdx), np.copy(self.basicIdx), -np.copy(self.c), -np.transpose(np.copy(self.A)), -np.copy(self.b), -self.z, self.tolerance)
  
  # return new dictionary with the objective function changed to the initialization phase
  def newObjectiveForInitializationPhase(self):
    return Dictionary(self.m, self.n, np.copy(self.basicIdx), np.copy(self.nonBasicIdx), np.copy(self.b), np.copy(self.A), map(lambda x: mp.mpf(str(x)), np.ones(len(self.c))*(-1)), self.z, self.tolerance)
  
  # Return the dictionary generated by the initialization phase
  # Initialization Phase done using the dual method
  def initialDictionary(self):
    # if there is not a single negative value in the basic coefficients, then it is not necessary to
    # run the initialization phase
    if all(i >= 0 for i in self.b):
      return self
    else:
      if DEBUG:
        print("Original Dictionary")
        print(self)

      # get the dictionary with the objective function changed
      newObjDict = self.newObjectiveForInitializationPhase()

      if DEBUG:
        print("Dictionary with New Objective Function")
        print(newObjDict)

      # get the dual of the new dictionary
      dualDict = newObjDict.dual()

      if DEBUG:
        print("Dual Dictionary with Objective Changed")
        print(dualDict)
      
      # optimize the dual of the new dictionary
      opt = Optimizer(dualDict)
      steps, dualOptmized, status = opt.solveLinearProgrammingRelaxation()
      
      # if the optimization phase results in an Unbounded dictionary, 
      # then the original dictionary is Infeasible
      if status == Dictionary.UNBOUNDED:
        self.statuscode = Dictionary.INFEASIBLECODE
        self.status = Dictionary.INFEASIBLE
        return self
      else:
        # mount the primal dictionary from the optmized dual
        if DEBUG:
          print("Dual After Initialization Phase")
          print(dualOptmized)

        # first, get the raw primal
        primalDictionary = dualOptmized.dual()

        if DEBUG:
          print("Primal Dictionary After Initialization")
          print(primalDictionary)
        
        # second, change the objective function to the original objective
        A_aux = primalDictionary._getAuxMatrix()
        C_aux = map(lambda x: mp.mpf(str(x)), np.zeros(len(self.c)+1))
        
        # compute the new value of the C vector according to the original objective function (original c vector)
        for i in range(len(self.nonBasicIdx)):
          idx_aux = np.nonzero(primalDictionary.basicIdx == self.nonBasicIdx[i])[0]
          
          # if the variable is one of the basic variables of the primal, 
          # then add the associated row times the coefficient in the original dictionary
          if len(idx_aux) > 0:
            idx_aux = idx_aux[0]
            C_aux += self.c[i]*A_aux[idx_aux, :]
          else:
            # if the variable is one of the non basic variables of the primal, 
            # then add the coefficient in the original dictionary to the related column in the primal
            idx_aux = np.nonzero(primalDictionary.nonBasicIdx == self.nonBasicIdx[i])[0]
            
            if len(idx_aux) > 0:
              idx_aux = idx_aux[0]
              C_aux[idx_aux+1] += self.c[i] # index shifted by +1 because of the Z value
        
        primalDictionary.z = C_aux[0]
        primalDictionary.c = C_aux[1:primalDictionary.n+1]
        primalDictionary.status = Dictionary.STANDARD
        
        if DEBUG:
          print("Primal Dictionary After Initialization with Original Objective")
          print(primalDictionary)
        
        return primalDictionary
