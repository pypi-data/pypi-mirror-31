# STA-663-final-project

STA 663 final project, python realization of paper "Biclustering via Singular Value Decomposition" by Mihee Lee, Haipeng Shen, Jianhua Z. Huang, and J. S. Marron.

The package can be used to perform rank 1 approximation on high-dimension low sample size data, to detect sparse structure, select vairables, and identify possible groups/subgroups. 

The package includes two functions, `SSVD_python` and `plotCluster`.

## SSVD_python
`SSVD_python` is used to conduct first layer Singular Value Decomposition on sparse n by p matrix, especially when n<<p.

inputs:

  1. X = 2 dimensional data matrix
  2. gamma1 = weight parameter for updating u, default set to 2
  3. gamma2 = weight parameter for updating v, default set to 2
  4. tol = tolerance for convergence, default set to 1e-4
  5. max_iter = maximum number of iterations, default set to 100
    
If converged, return:

  1. u = u vector of Sparse SVD
  2. s = largest singular value from SVD
  3. v = v vector of Sparse SVD
  4. niter = number of iteration until convergence

If not converged, print:

  "Fail to converge! Increase the max_iter!"

## plotClusters
`plotClusters` is used to plot the biclustering using rank 1 approximation result from `SSVD_python` function.

inputs:
    
  1. u, s, v = return values of SSVD function
  2. group = vector of known groups, length equal to that of u. Provide all 1's if no grouping is informed.
  3. tresh = number of insignificant rows to dicard.
    
return:

  Heatmap of rank 1 approximated clusters