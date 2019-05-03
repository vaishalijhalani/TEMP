import argparse


def get_config():
    parser = argparse.ArgumentParser(description='Algorand Simulator')
    parser.add_argument('--node', type=int, default=50, metavar='N',
                        help="Number of nodes to use in a network")
    parser.add_argument('--blocks', type=int, default=1, metavar='B',
                        help="Number of blocks until simulation runs")
    parser.add_argument('--exp1', default=False, action='store_true')
    parser.add_argument('--exp2', default=False, action='store_true')
    # TODO: add every other parameters to be passed as command line argument

    args = parser.parse_args()

    return args
