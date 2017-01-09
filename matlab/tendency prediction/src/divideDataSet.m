function [train, Y0] = divideDataSet(count, labeled, labels, m, c)
    train = zeros(1,labeled);
    index = 1:m;
    
    num = 0; % record the number of each type
    selected = 0;
    % The following loop achieves that one instance of every type is selected at least.
    for k = 1:c
        selected = selected+1;
        t = num+unidrnd(count(2,k));
        train(selected) = t;
        index(find(index==t)) = []; % remove the selected element in index
        num = num + count(2,k);
    end
    
    for k = 1:(labeled-c)
         selected = selected+1;
         t = unidrnd(length(index));
         train(selected) = index(t);
         index(t) = [];
    end
    
    Y0 = zeros(m,c);
    global map_class_index;
    global map_index_class;
    map_class_index = zeros(1,max(labels));
    map_index_class = zeros(1,c);
    for k = 1:c 
        map_class_index(count(1,k)) = k;
        map_index_class(k) = count(1,k);
    end
    for k = train
        Y0(k,map_class_index(labels(k)))=1;
    end
    