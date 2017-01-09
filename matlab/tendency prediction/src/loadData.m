function [x,labels,m,dim,count,c] = loadData(file)
%load data

% x: input instances
% labels: class of each instance
% m: the number of instances
% dim: dimensionality of instances
% count: size of each class
% c : class number

    load(file);
    dataset = [];
    if strcmp(file, 'usps1_3_150.mat')
        dataset = usps1_3_150;
    elseif strcmp(file, 'usps1_3_all.mat')
        dataset = usps1_3_all;
    end
    labels = dataset(:,1);
    x = dataset(:,2:end);
    [m,dim] = size(x);
    count(1,:)  = unique(labels);
    count(2,:) = hist(labels,count(1,:));
    c = length(count(1,:) );
