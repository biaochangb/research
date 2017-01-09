__author__ = 'bchang'
import Data
import time

if __name__ == '__main__':
    print 'start'
    start_time = time.time()
    data = Data.Data()
    data.preprocessing()
    # {8: 1168, 9: 962, 10: 17723, 6: 1796, 7: 1535} 23184
    # Topics: 3608
    end_time = time.time()
    print 'Running time: %f h.\r\n'%((end_time-start_time)/3600)