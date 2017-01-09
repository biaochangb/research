function [avg_steps, avg_accuracy, sigma] = randomWalk(data_file, labeled,  alpha, sigma_init)
    global TRIALS;
    [x,labels,m,dim,count,c] = loadData(data_file);
    sigma = ones(1,dim)*sigma_init;
    w = getAdjacentMatrix(x, m, sigma);
    S = getNormalizedMatrixByRow(w,m);
    avg_steps = 0;
    avg_accuracy = 0;
    for k = 1:TRIALS
        [train, Y0] = divideDataSet(count, labeled, labels, m, c);
        [p,q] = LGC(m,S, Y0, alpha, labels, train);
        avg_steps =  avg_steps+p;
        avg_accuracy = avg_accuracy+q;
    end
    avg_steps = avg_steps/TRIALS;
    avg_accuracy = avg_accuracy/TRIALS;