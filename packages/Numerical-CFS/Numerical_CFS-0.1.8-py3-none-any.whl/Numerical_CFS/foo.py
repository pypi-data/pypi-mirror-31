from symengine import I 
import sympy as si
r =si.symbols('r')

b = (r + 1)**-2*(r -1)**-2*si.diff((r +1)**3*(r -1)**(3),r, 1) 
bl = si.lambdify(r,b)
#print(bl(1))
c = si.simplify((r + 1)**-2*(r -1)**-2*(3*(r +1)**2*(r -1)**(3) + 3*(r +1)**3*(r -1)**(2))) 
cl = si.lambdify(r,c)
print(cl(1))



