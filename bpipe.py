def main():
    for i in range(1000):
        print 'line', i
    #raise SystemExit('foo')
    #raise IOError(1, 'foo')
    return 0

if __name__ == '__main__':
    from start import start
    start(main)
