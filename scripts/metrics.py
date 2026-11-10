"""Two-by-two log likelihood; descriptive exploration, no population inference."""
import math

def keyness(f_lk, f_lc, n_lk, n_lc):
    """2x2 likelihood ratio and direction from relative frequencies, not raw counts."""
    values = (f_lk, f_lc, n_lk, n_lc)
    if any(not isinstance(v, int) or v < 0 for v in values):
        raise ValueError('Nonnegative integer counts required')
    if n_lk == 0 or n_lc == 0 or f_lk > n_lk or f_lc > n_lc:
        raise ValueError('Positive corpus totals and valid frequencies required')
    total = n_lk + n_lc
    freq = f_lk + f_lc
    observed = (f_lk, f_lc, n_lk-f_lk, n_lc-f_lc)
    expected = (n_lk*freq/total, n_lc*freq/total,
                n_lk*(total-freq)/total, n_lc*(total-freq)/total)
    g2 = max(0.0, 2*sum(o*math.log(o/e) for o, e in zip(observed, expected) if o and e))
    # Cross multiplication avoids floating point equality issues.
    diff = f_lk*n_lc - f_lc*n_lk
    direction = 'lk' if diff > 0 else 'lc' if diff < 0 else 'equal'
    return {'g2': g2, 'direction': direction,
            'per_10000_lk': f_lk/n_lk*10000, 'per_10000_lc': f_lc/n_lc*10000}
