#!/usr/bin/python
import PolyUsers as poly
from PolyParams import PolynomialParam
import MatrixRoutines as matrix
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib import rc
import matplotlib as mp
import numpy as np
import numpy.ma as ma
"""
    Optimal Quadrature Subsampling
    1D Example

    Pranay Seshadri
    University of Cambridge
    ps583 <at> cam.ac.uk

"""
# Simple analytical function -- feel free to change
def fun(x, derivative_flag):

    if derivative_flag == 0:
        return np.exp(x[:]) # No derivative
    else:
        return np.exp(x[:]) , np.exp(x[:]) # Function and its derivative



def main():

    #--------------------------------------------------------------------------------------
    #
    #  USER'S NOTES:
    #        1. With the derivative flag on we recommend using 2X basis terms
    #        2. Input maximum number of permissible model evaluations
    #        3. Input number of points on the "full grid" (3x5 times number in line above)
    #
    #--------------------------------------------------------------------------------------
    highest_order = 50 # more for visualization
    derivative_flag = 0 # derivative flag on=1; off=0


    full_grid_points = 100# full tensor grid
    min_value, max_value = -1, 1 # range of uncertainty --> assuming Legendre
    alpha_parameter, beta_parameter = 0, 0 # Jacobi polynomial values for Legendre
    uq_parameter1 = PolynomialParam("Jacobi", min_value, max_value, alpha_parameter, beta_parameter, derivative_flag, full_grid_points) # Setup uq_parameter


    # Pick select columns. This amounts using either a total order or hyperbolic cross
    # basis set in nD
    store_error = np.zeros((highest_order, highest_order)) + np.NaN

    # Check whether derivative flag is on or off!
    if derivative_flag == 0:


        # Compute A and C matrices and solve the full least squares problem
        A, C, gaussPoints = PolynomialParam.getAmatrix(uq_parameter1)
        b = fun(gaussPoints, derivative_flag)

        # Normalize these!
        A_norms = np.sqrt(np.sum(A**2, axis=1)/(1.0 * full_grid_points))
        Normalization = np.diag(1.0/A_norms)
        Aweighted = np.dot(Normalization, A)
        bweighted = np.dot(Normalization, b)

        # "REAL" solution
        x_true = matrix.solveLeastSquares(Aweighted, bweighted)

        # Get the function values at ALL points!
        function_values = fun(gaussPoints, derivative_flag)

        for basis_subsamples in range(2,highest_order):
            for quadrature_subsamples in range(2,highest_order):

                # Now compute the "optimal" subsamples from this grid!
                P = matrix.QRColumnPivoting( A[:, 0 : quadrature_subsamples] )
                optimal = P[ 0 : quadrature_subsamples]

                # Now take the first "evaluations_user_can_afford" rows from P
                Asquare = A[optimal, 0 : basis_subsamples]
                bsquare = b[optimal]
                rows, cols = Asquare.shape

                # Solve least squares problem only if rank is not degenrate!
                if(np.linalg.matrix_rank(Asquare) == cols):
                    # Solve the least squares problem
                    x = matrix.solveLeastSquares(Asquare, bsquare)
                    store_error[basis_subsamples,quadrature_subsamples] = np.linalg.norm( x - x_true[0:basis_subsamples])

    # If the derivative flag is switched on!
    else:

        # Compute A and C matrices and solve the full least squares problem
        A, C, gaussPoints = PolynomialParam.getAmatrix(uq_parameter1)
        b, d = fun(gaussPoints, derivative_flag)

        # Full least squares!
        x_true = matrix.solveLeastSquares(A, b)

        # Get the function and gradient values
        function_values, grad_values = fun(gaussPoints, derivative_flag)

        for quadrature_subsamples in range(2,highest_order):
            for basis_subsamples in range(2,highest_order):


                # Now compute the "optimal" subsamples from this grid!
                P = matrix.QRColumnPivoting( A[:, 0 : quadrature_subsamples] )
                optimal = P[ 0 : quadrature_subsamples]

                # Now take the first "evaluations_user_can_afford" rows from P
                Asquare = A[optimal, 0 : basis_subsamples]
                Csquare = C[optimal, 0 : basis_subsamples]
                bsquare = b[optimal]
                dsquare = d[optimal]

                # Stack the matrices & vectors
                Matrices_stacked = np.vstack((Asquare, Csquare))
                Vectors_stacked = np.vstack((bsquare, dsquare))
                rows, cols = Matrices_stacked.shape


                # Solve least squares problem only if rank is not degenrate!
                if(np.linalg.matrix_rank(Matrices_stacked) == cols):
                    # Solve the least squares problem
                    x = matrix.solveLeastSquares(Matrices_stacked, Vectors_stacked)
                    store_error[basis_subsamples,quadrature_subsamples] = np.linalg.norm( x - x_true[0:basis_subsamples])


    #--------------------------------------------------------------------------------------
    #
    #                               PLOTS BELOW!
    #
    #--------------------------------------------------------------------------------------
    # Plot!
    rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})
    rc('text', usetex=True)

    Zm = ma.masked_where(np.isnan(store_error),store_error)
    yy, xx = np.mgrid[0:highest_order, 0: highest_order]
    plt.pcolor(yy, xx, np.log10(np.abs(Zm)), cmap='jet', vmin=-15, vmax=0)
    cb = plt.colorbar()
    ax = cb.ax
    text = ax.yaxis.label
    font = mp.font_manager.FontProperties(family='times new roman', style='italic', size=16)
    text.set_font_properties(font)
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)
    plt.ylabel(r'Quadrature subsamples',fontsize=16)
    plt.xlabel(r'Basis subsamples',fontsize=16)
    plt.xlim(2, highest_order-1)
    plt.ylim(2, highest_order-1)
    plt.show()


main()
