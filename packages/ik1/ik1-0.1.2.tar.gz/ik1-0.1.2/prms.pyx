def primes(int nb_primes):
    cdef int N_MX = 10000
    cdef int n, i, p_idx
    cdef int p[10000]
    
    if nb_primes > N_MX:
        nb_primes = N_MX
        
    p_idx = 0  # The current number of elements in p.
    n = 2
    while p_idx < nb_primes:
        # Is n prime?
        for i in p[:p_idx]:
            if n % i == 0:
                break

        # If no break occurred in the loop, we have a prime.
        else:
            p[p_idx] = n
            p_idx += 1
        n += 1

    # Let's return the result in a python list:
    result_as_list  = [prime for prime in p[:p_idx]]
    return result_as_list
