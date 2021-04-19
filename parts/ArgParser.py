from argparse import ArgumentParser


class ArgsParser:
    @staticmethod
    def parse():
        parser = ArgumentParser()

        parser.add_argument('-t', '--threads', dest='threads_count', type=int, help='Number of parser threads')
        parser.add_argument('-r', '--rows', dest='rows_count', type=int, help='Number of rows to process')

        args = parser.parse_args()
        return args