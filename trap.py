def main():
    foo()
    return 0

def foo():
    return 1/0

if __name__ == '__main__':
    from start import start
    start(main)
