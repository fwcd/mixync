import mixync
import sys

if sys.version_info < (3, 9):
    print('Python 3.9+ is required!')
    sys.exit(1)

if __name__ == '__main__':
    mixync.main()
