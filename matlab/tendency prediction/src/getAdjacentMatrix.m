function [w] = getAdjacentMatrix(x, m, sigma)
    %get the Adjacent Matrix
    sigma_matrix = repmat(sigma,m,1);
    x = x./sigma_matrix;
    w = pdist2(x, x,'euclidean');
    w = exp(-(w.^2)./2);