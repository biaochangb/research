function [S] = getNormalizedMatrixByRow(w,m)
    row_sum_w = sum(w,2);   %sum of each row
    row_sum_w = row_sum_w.^(-0.5);
    D = diag(row_sum_w);
    S = D*w*D;
    