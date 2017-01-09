function [steps, accuracy] = LGC_GD( x,m,dim,c, Y0, alpha, labels, train, sigma)
% LGC learning hype-parameters with gradient descent

    global max_iteration;
    global epsilon_loss_function;
    global epsilon_sigma;
    global step_size_gd;
    global debug;
    
    mu = 1/alpha-1;
    change = 10;
    loss_function = -1;
    loss_d = zeros(1,dim);  % differentiation
    steps = 0;
    Y = [];
    
    while (change>epsilon_loss_function) && (steps<max_iteration)
        % fix sigma
        if debug > 0
            fprintf('fix sigma\n');
        end
        w = getAdjacentMatrix(x, m, sigma);
        S = getNormalizedMatrixByRow(w,m);
        Y = (eye(m)-alpha*S)\Y0;
        row_sum = sum(Y,2);   %sum of each row
        Y = Y./repmat(row_sum,1,c);
        evaluate(train, labels, Y);
        
        % fix Y
        if debug > 0
            fprintf('fix Y\n');
        end
        normal = -1;
        term_change = 10;
        
        while term_change > epsilon_sigma
            if debug > 0
                fprintf('\t %f,%f,%f,%f\n',term_change,normal,sum(sigma),max(abs(loss_d)));
            end      
            row_sum_w = sum(w,2);   %sum of each row
            row_sum_w_inverse = row_sum_w.^(-0.5);
            D = diag(row_sum_w_inverse);
            Y_D = D*Y;
            similarty_y_d = pdist2(Y_D, Y_D,'euclidean').^2;
            % calculate the differentiation for each dimensionality
            for d = 1:dim 
                column = x(:,d);
                kernel = pdist2(column, column,'euclidean').^2;
                wij_d = w.*kernel./(sigma(d)^3);
                row_sum_wij_d = sum(wij_d,2);
                loss_d(d) = sum(sum(wij_d.*similarty_y_d));
                
                for k = 1:c 
                    column = Y_D(:,k);
                    column_squared = column.^2;
                    normalized = row_sum_wij_d./row_sum_w;
                    normalized_2 = column_squared.*row_sum_wij_d./row_sum_w;
                    w1 = repmat(normalized_2,1,m);
                    w2 = repmat(normalized_2',m,1);  
                    w3 = column*column'.*( repmat(normalized,1,m)+repmat(normalized',m,1));
                    loss_d(d) = loss_d(d) + sum(sum(w.*(-w1-w2+w3)));
                    
                    %y_d_k_distance = pdist2(column, column,'euclidean');
                    %column = column.*row_sum_wij_d./row_sum_w;
                    %y_d_k_distance_normalized = -pdist2(column, column,'euclidean');
                    %loss_d(d) = loss_d(d) + sum(sum(w.*y_d_k_distance.*y_d_k_distance_normalized));
                end
                %loss_d(d);
            end
            sigma = sigma - step_size_gd*loss_d;
            w = getAdjacentMatrix(x, m, sigma);
            term = sum(sum(w.*similarty_y_d));
            term_change = abs(normal-term);
            normal = term;
            sigma;
            %toc;
        end
        
            if debug > 0
                fprintf('\t %f,%f,%f\n',term_change,normal,sum(sigma));
            end
        
        new_loss = mu/2*(norm(Y-Y0,'fro')^2) + normal;
        change = abs(new_loss-loss_function);
        loss_function = new_loss;
        steps = steps+1;
        if debug > 0
            fprintf('%f,%f,%f\n',change,loss_function,sum(loss_d));
        end
        
        %w = getAdjacentMatrix(x, m, sigma);
        %S = getNormalizedMatrixByRow(w,m);
        %Y = (eye(m)-alpha*S)\Y0;
        %evaluate(train, labels, Y)
        %break;
    end
    accuracy = evaluate(train, labels, Y);
    