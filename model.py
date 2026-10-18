"""Service-step illustrations, not a cycle-accurate WiNoC simulator."""

def waiting_times(n, forwarding, holding, occupancy, alpha):
    if n < 2 or forwarding < 0 or holding < 0:
        raise ValueError('Use at least two hubs and nonnegative cycle times.')
    if not 0 <= occupancy <= 1 or not 0 <= alpha <= 1:
        raise ValueError('Occupancy and alpha must be between zero and one.')
    step = forwarding + occupancy * holding
    baseline = (n - 1) / 2 * step
    ideal_hops = n / 4 if n % 2 == 0 else (n * n - 1) / (4 * n)
    ideal = ideal_hops * step
    return dict(step=step, baseline=baseline, ideal=ideal,
                mixture=alpha * ideal + (1-alpha) * baseline,
                worst_baseline=(n-1)*step, worst_ideal=(n//2)*step)


def traversal(n, start, target, policy):
    if n < 2 or not 0 <= start < n or not 0 <= target < n:
        raise ValueError('Hub identifiers must be inside the ring.')
    forward = (target-start) % n
    direction = -1 if policy == 'Ideal shorter direction' and n-forward < forward else 1
    hops = min(forward,n-forward) if policy == 'Ideal shorter direction' else forward
    return [(start + direction*i) % n for i in range(hops+1)]
