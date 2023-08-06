"""
Plasma control system

Use constraints to adjust coil currents
"""

from numpy import dot, transpose, eye, array
from numpy.linalg import inv

class constrain(object):
    """
    Adjust coil currents using constraints. To use this class,
    first create an instance by specifying the constraints

    >>> controlsystem = constrain(xpoints = [(1.0, 1.1), (1.0,-1.0)])

    controlsystem will now attempt to create x-points at
    (R,Z) = (1.0, 1.1) and (1.0, -1.1) in any Equilibrium

    >>> controlsystem(eq)

    where eq is an Equilibrium object which is modified by
    the call.
    
    The constraints which can be set are:

    xpoints - A list of X-point (R,Z) locations
    
    isoflux - A list of tuples (R1,Z1, R2,Z2) 
    
    psivals - A list of (R,Z,psi) values

    At least one constraint must be included
    
    gamma - A scalar, minimises the magnitude of the coil currents
    """
    def __init__(self, xpoints=[], gamma=1e-12, isoflux=[], psivals=[]):
        """
        Create an instance, specifying the constraints to apply
        """
        self.xpoints = xpoints
        self.gamma = gamma
        self.isoflux = isoflux
        self.psivals = psivals
        
    def __call__(self, eq):
        """
        Apply constraints to Equilibrium eq
        """
    
        tokamak = eq.getMachine()
    
        constraint_matrix = []
        constraint_rhs = []
        for xpt in self.xpoints:
            # Each x-point introduces two constraints
            # 1) Br = 0

            Br = eq.Br(xpt[0], xpt[1])
        
            # Add currents to cancel out this field
            constraint_rhs.append(-Br)
            constraint_matrix.append(
                tokamak.controlBr(xpt[0], xpt[1]))
            
            # 2) Bz = 0
            
            Bz = eq.Bz(xpt[0], xpt[1])
            
            # Add currents to cancel out this field
            constraint_rhs.append(-Bz)
            constraint_matrix.append(
                tokamak.controlBz(xpt[0], xpt[1]))

        # Constrain points to have the same flux
        for r1,z1, r2,z2 in self.isoflux:
            # Get Psi at (r1,z1) and (r2,z2)
            p1 = eq.psiRZ(r1,z1)
            p2 = eq.psiRZ(r2,z2)
            constraint_rhs.append(p2 - p1)
        
            # Coil responses
            c1 = tokamak.controlPsi(r1,z1)
            c2 = tokamak.controlPsi(r2,z2)
            # Control for the difference between p1 and p2
            c = [ c1val - c2val for c1val, c2val in zip(c1,c2)]
            constraint_matrix.append( c )
    
        # Constrain the value of psi
        for r,z,psi in self.psivals:
            p1 = eq.psiRZ(r,z)
            constraint_rhs.append(psi - p1)

            # Coil responses
            c = tokamak.controlPsi(r,z)
            constraint_matrix.append( c )
            
        if not constraint_rhs:
            raise ValueError("No constraints given")

        # Constraint matrix
        A = array(constraint_matrix)
        b = array(constraint_rhs)
    
        # Solve by Tikhonov regularisation
        # minimise || Ax - b ||^2 + ||gamma x ||^2
        #
        # x = (A^T A + gamma^2 I)^{-1}A^T b
        
        # Number of controls (length of x)
        ncontrols = A.shape[1]
        
        # Calculate the change in coil current
        current_change =  dot( inv(dot(transpose(A), A) + self.gamma**2 * eye(ncontrols)), 
                               dot(transpose(A),b))
        print("Current changes: " + str(current_change))
        tokamak.controlAdjust(current_change)

    def plot(self, axis=None, show=True):
        """
        Plots constraints used for coil current control
        
        axis     - Specify the axis on which to plot
        show     - Call matplotlib.pyplot.show() before returning
        
        """
        from .plotting import plotConstraints
        return plotConstraints(self, axis=axis, show=show)
    

def flux_surface(R0, Z0, a, elongation=0.0, triangularity=0.0, indentation=0.0, n=20):
    """
    Generate a set of up-down symmetric isoflux points for a flux
    surface of given shape. Uses the parametrisation given in
      
    J. Manickam, Nucl. Fusion 24 595 (1984)
    
    R0 - Major radius of axis
    Z0 - Height of axis
    a  - Minor radius
    
    elongation - ellipticity-1 = 0 for a circle
    triangularity - 'D' shape
    indentation - Produces a bean shape

    n - Number of points
    
    """
    
    def pos(theta):
        """
        Returns R,Z at given theta
        """
        R = R0 - indentation + (a + indentation*cos(theta))*cos(theta + triangularity*sin(theta))
        Z = Z0 + (1. + elongation) * a * sin(theta)
        return R,Z

    # Poloidal angle values
    thetavals = linspace(0.0, 2*pi, n, endpoint=False)
    
    # Generate the first point, used as a reference for all others
    p0 = pos(0.0)
    
    # All other points are the same flux as p0
    isoflux = [ p0 + pos(theta) for theta in thetavals[1:] ]
    
    return isoflux
