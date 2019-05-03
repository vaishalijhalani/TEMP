import random


def get_normal_random(mu, sigma):
    return max(0, int(random.gauss(mu, sigma)))


def get_uniform_random(a, b):
    return random.randint(a, b)


def pseudo_random_generator(seed=None, k=256):
    prev_state = random.getstate()
    if seed is not None:
        random.seed(seed)
    n = random.getrandbits(k)
    random.setstate(prev_state)
    return n
