import time
def main():
    print 'press ^C now'
    time.sleep(5)

if __name__ == '__main__':
    from start import start
    start(main)
