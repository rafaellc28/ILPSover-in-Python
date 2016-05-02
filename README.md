ILPSover-in-Python
==================

ILPSover developed in Python for the course
https://www.coursera.org/course/linearprogramming.

This solver contains an Integer Linear Programming Solver that implements the Cutting Plane Method and 
a Linear Programming Solver that implements the Simplex Algorithm.

The input is a dictionary in the Standard Form:

<table border="0">
  <tr><td>maximize</td><td>c<sup>T</sup>x</td><td></td></tr>
  <tr><td></td><td>Ax</td><td>&le; b</td></tr>
  <tr><td></td><td>&nbsp;&nbsp;x</td><td>&ge; 0</td></tr>
</table>

The input files must be in the following format:

[Line 1] m n [m is the number of constraints and n is the number of variables]<br>
[Line 2] B1 B2 ... Bm [m integers corresponding to the list of basic indices] <br>
[Line 3] N1 N2 ... Nn [n integers corresponding to the list of non-basic indices] <br>
[Line 4] b1 .. bm [m floating point numbers corresponding to the basic values: the vector b] <br>
[Line 5] a11 ... a1n [first row coefficients for matrix A.] <br>
.... <br>
[Line m+4] am1 ... amn [mth row coefficients for matrix A.] <br>
[Line m+5] z0 c1 .. cn [n+1 floating point numbers corresponding to the objective coefficients: solution value plus vector c]<br>
