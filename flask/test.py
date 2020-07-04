from tsadf.main import detect
from multiprocessing import Process

if __name__ == '__main__':
    p = Process(target=detect, args=('tsadf/sample_data.csv', 96, 'interactive', 0, 100000,))
    p.start()
    p.join()
