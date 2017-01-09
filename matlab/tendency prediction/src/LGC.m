function [steps, accuracy] = LGC(m, S, Y0, alpha, labels, train)
% NIPS2004_Learning with local and global consistency
    steps = 0;
    Y = (eye(m)-alpha*S)\Y0;
    accuracy = evaluate(train, labels, Y);