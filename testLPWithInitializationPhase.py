import sys
import re
import numpy as np
from Dictionary import *
from Optimizer import *
import mpmath as mp

mp.dps = 100

DEBUG = False

r = re.compile('\s{2,}')

def parseLine(vec):
  return np.array([elem.replace('\n','') for elem in vec]) # remove \n

def toInt(vec):
  return np.array([int(elem) for elem in vec]) # cast to int

def toFloat(vec):
  return np.array([mp.mpf(str(elem)) for elem in vec]) # cast to float using mpmath library

def readLine(bufferedLine, separator):
  line = bufferedLine.readline()
  line = line.strip()
  line = r.sub(' ', line)
  line = line.split(separator)
  
  return parseLine(line)

def main(argv):
  
  separator = ' '
  
  # read m(# of constraints) and n(# of variables)
  m, n = toInt(readLine(sys.stdin, separator))
  
  if DEBUG:
    sys.stderr.write(str(m)+"\n")
    sys.stderr.write(str(n)+"\n")
  
  # read the list of basic indices
  basicIdx = toInt(readLine(sys.stdin, separator))
  
  if DEBUG:
    sys.stderr.write(str(basicIdx)+"\n")
  
  # read the list of non-basic indices
  nonBasicIdx = toInt(readLine(sys.stdin, separator))
  
  if DEBUG:
    sys.stderr.write(str(nonBasicIdx)+"\n")
  
  # read the list of values for the basic indices (at the same order they are declared)
  # remember: Ax <= b, b is the list being read
  basicValues = toFloat(readLine(sys.stdin, separator))
  
  if DEBUG:
    sys.stderr.write(str(basicValues)+"\n")
  
  # read the matrix A (from problem Ax <= b)
  coeffMatrix = []
  for i in range(m):
    row = toFloat(readLine(sys.stdin, separator))
    coeffMatrix.append(row)
  
  coeffMatrix = np.array(coeffMatrix)
  
  if DEBUG:
    sys.stderr.write(str(coeffMatrix)+"\n")
  
  # read the current objective value and the current objective row coefficients
  coeffObjs = toFloat(readLine(sys.stdin, separator))
  z = coeffObjs[0]
  coeffObj = coeffObjs[1:]
  
  dictionary = Dictionary(m, n, basicIdx, nonBasicIdx, basicValues, coeffMatrix, coeffObj, z, mp.power(10,-100))

  if DEBUG:
    sys.stderr.write("Original Dictionary\n")
    sys.stderr.write(str(dictionary)+"\n")
  
  # Initialization Phase
  newDictionary = dictionary.initialDictionary()

  if DEBUG:
    sys.stderr.write("Dictionary After Initialization Phase\n")
    sys.stderr.write(newDictionary+"\n")

  sys.stdout.flush()

  if newDictionary.statuscode == Dictionary.INFEASIBLECODE:
    sys.stdout.write(newDictionary.status)
    return

  opt = Optimizer(newDictionary)
  cuts, optmizedDict, status = opt.solveLinearProgrammingRelaxation()

  if DEBUG:
    sys.stderr.write("Ootimized Dictionary\n")
    sys.stderr.write(str(optmizedDict)+"\n")
  
  if optmizedDict.statuscode < 0:
    sys.stdout.write(status)
  else:
    print "%.6f" % optmizedDict.z

if __name__ == "__main__":
    main(sys.argv)
