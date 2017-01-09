function experiment()
% run the whole experiment
    diary '../result/run.log'
    tic;
    global TRIALS;
    global max_iteration;
    global step_size_gd;
    global epsilon_sigma;
    global epsilon_y;
    global epsilon_loss_function;
    global debug;
   
    debug = 0;
    TRIALS = 1;
    max_iteration = 200;
    step_size_gd = 1;
    epsilon_sigma = 0.05;
    epsilon_y = 0.001;
    epsilon_loss_function = 0.05;
    
    data_file = 'usps1_3_150.mat';
    %data_file = 'usps1_3_all.mat';
    [steps, accuracy] = deal(0);
    alpha = 0.99;
    sigma_init = 4.25;
    
    for num = 3:5:100
        [s1, a1,s2,a2, sigma] = compare(data_file, num, alpha, sigma_init);
        fprintf('labeled = %d, s1 = %d, a1 = %f, s2 = %d, a2 = %f \n',num,s1, a1,s2,a2);
    end
    
    toc;
    diary off 

function [avg_steps, avg_accuracy,avg_steps2,avg_accuracy2, sigma] = compare(data_file, labeled,  alpha, sigma_init)
    global TRIALS;
    [x,labels,m,dim,count,c] = loadData(data_file);
    sigma = ones(1,dim)*sigma_init;
    avg_steps = 0;
    avg_accuracy = 0;
    avg_steps2 = 0;
    avg_accuracy2 = 0;
    w = getAdjacentMatrix(x, m, ones(1,dim)*1.25);
    S = getNormalizedMatrixByRow(w,m);
    for k = 1:TRIALS
        [train, Y0] = divideDataSet(count, labeled, labels, m, c);
        [p,q] = LGC_GD( x,m,dim,c, Y0, alpha, labels, train, sigma);
        [p2,q2] = LGC(m,S, Y0, alpha, labels, train);       
        avg_steps =  avg_steps+p;
        avg_accuracy = avg_accuracy+q;     
        avg_steps2 =  avg_steps2+p2;
        avg_accuracy2 = avg_accuracy2+q2;
    end
    avg_steps = avg_steps/TRIALS;
    avg_accuracy = avg_accuracy/TRIALS;        
    avg_steps2 = avg_steps2/TRIALS;
    avg_accuracy2 = avg_accuracy2/TRIALS;       
    
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
    
 
function [avg_steps, avg_accuracy, sigma] = randomWalk_gd(data_file, labeled,  alpha, sigma_init)
    global TRIALS;
    [x,labels,m,dim,count,c] = loadData(data_file);
    sigma = ones(1,dim)*sigma_init;
    avg_steps = 0;
    avg_accuracy = 0;
    for k = 1:TRIALS
        [train, Y0] = divideDataSet(count, labeled, labels, m, c);
        [p,q] = LGC(m,S, Y0, alpha, labels, train);       
        [p,q] = LGC_GD( x,m,dim,c, Y0, alpha, labels, train, sigma);
        avg_steps =  avg_steps+p;
        avg_accuracy = avg_accuracy+q;
    end
    avg_steps = avg_steps/TRIALS;
    avg_accuracy = avg_accuracy/TRIALS;    
    
    