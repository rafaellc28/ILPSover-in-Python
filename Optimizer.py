import sys
import numpy as np
import mpmath as mp

mp.dps = 100

DEBUG = False

# Encapsulate the execution of the pivot steps of a dictionary
class Optimizer:
  INFEASIBLECODE = -2
  INFEASIBLE = "INFEASIBLE"

  @staticmethod
  def _frac(num):
    return mp.frac(num)
  
  @staticmethod
  def _distance(num):
    return mp.fabs(mp.fsub(num, mp.nint(num)))

  @staticmethod
  def _isInteger(num, tolerance = mp.power(10,-6)):
    return mp.almosteq(num, mp.nint(num), tolerance)
  
  # Solve the Linear Programming Relaxation Problem, e.g., all decision variables are real
  # Return the final dictionary with the status: FINAL, UNBOUNDED or INFEASIBLE
  @staticmethod
  def solveLinearProgrammingRelaxation(dictionary):
    
    # initial pivoting
    entering, leaving, newDictionary = dictionary.pivot()
    steps = 0

    if DEBUG:
      sys.stderr.write("New Dictionary After Pivot Step " + str(steps) + "\n")
      sys.stderr.write(newDictionary+"\n")
    
    # while the new dictionary is not FINAL or UNBOUNDED
    while newDictionary.statuscode > 0:
      
      steps += 1
      entering, leaving, newDictionary = newDictionary.pivot()

      if DEBUG:
        sys.stderr.write("New Dictionary After Pivot Step " + str(steps) + "\n")
        sys.stderr.write(newDictionary+"\n")

    return steps, newDictionary, newDictionary.status
  
  # Solve the Integer Linear Programming Problem, e.g., all decision variables are positive integers
  # Return the final dictionary with the status: FINAL, UNBOUNDED or INFEASIBLE
  # Use the Cutting Plane Method
  @staticmethod
  def solveIntegerLinearProgrammingWithCuttingPlane(dictionary, tolerance = mp.power(10,-6)):
    
    # cuts added
    cutsAdded = 0

    # Initialization Phase
    dictionary = dictionary.initialDictionary()

    if DEBUG:
      sys.stderr.write("Dictionary After Initialization Phase\n")
      sys.stderr.write(dictionary+"\n")
    
    # If the dictionary is INFEASIBLE, return
    if dictionary.statuscode < 0:
      return 0, dictionary, dictionary.status
    
    # Solve the relaxed problem
    steps, newDictionary, status = Optimizer.solveLinearProgrammingRelaxation(dictionary)

    if DEBUG:
      sys.stderr.write("Primal Dictionary After First LP Relaxation Solve\n")
      sys.stderr.write(newDictionary+"\n")
    
    if newDictionary.statuscode < 0:
      dictionary = newDictionary
      return 0, newDictionary, status
    
    # get the basic variables with "non-integer values" (considering the tolerance)
    varFractional = np.array( filter( (lambda (i,x): not Optimizer._isInteger(x, tolerance)), zip( range(len(newDictionary.b)), newDictionary.b) ) )

    if len(varFractional) > 0:
      varFractional = varFractional[:,0]
    
    # while there are non-integer basic values, keep optmizing
    while len(varFractional) > 0:
      
      # add a new cut plane for each non-integer basic value
      for i in range(len(varFractional)):
        newDictionary.b = np.append(newDictionary.b, -Optimizer._frac(newDictionary.b[varFractional[i]]))
        newRow = map((lambda x: Optimizer._frac(-x)), newDictionary.A[varFractional[i],:])
        newDictionary.A = np.concatenate((newDictionary.A,np.array([newRow])), axis=0)
        newDictionary.m += 1
        newVar = max(np.append(newDictionary.basicIdx, newDictionary.nonBasicIdx))+1
        newDictionary.basicIdx = np.append(newDictionary.basicIdx, newVar)
        
        cutsAdded += 1

      if DEBUG:
        sys.stderr.write("Dictionary After New Cutting Planes Added\n")
        sys.stderr.write(newDictionary+"\n")

      # the result primal from adding the cut planes is INFEASIBLE, but the dual is FEASIBLE
      dictionary = newDictionary.dual()
      
      steps, newDictionary, status = Optimizer.solveLinearProgrammingRelaxation(dictionary)

      if newDictionary.statuscode < 0:
        newDictionary.statuscode = Optimizer.INFEASIBLECODE
        newDictionary.status = Optimizer.INFEASIBLE
        return 0, newDictionary, newDictionary.status

      # return to the original primal dictionary
      newDictionary = newDictionary.dual()

      if DEBUG:
        sys.stderr.write("Dictionary After LP Relaxation Solve\n")
        sys.stderr.write(newDictionary+"\n")

      # get the basic variables with "non-integer values" (considering the tolerance)
      #varFractional = np.array(filter((lambda (i,x): Optimizer._distance(x) > tolerance), zip(range(len(newDictionary.b)), newDictionary.b)))
      varFractional = np.array(filter((lambda (i,x): not Optimizer._isInteger(x, tolerance)), zip(range(len(newDictionary.b)), newDictionary.b)))
      
      if len(varFractional) > 0:
        varFractional = varFractional[:,0]
    
    return cutsAdded, newDictionary, newDictionary.status
