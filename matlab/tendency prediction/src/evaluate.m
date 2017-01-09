function [accuracy] = evaluate(train, labels, Y)
    accuracy = 0;
    [m,c] = size(Y);
    global map_index_class;
    for k = 1:m 
        if any(train==k) 
            continue;
        else
            [probability, index] = sort(Y(k,:));
            classified = index(c);
            if map_index_class(classified)==labels(k)
                accuracy = accuracy+1;
            end
        end
    end
    accuracy = accuracy *1.0/(m-length(train));