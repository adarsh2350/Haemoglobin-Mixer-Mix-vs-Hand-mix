from collections import Counter


# Calculating mod avg.
def mod_avg(numbers):
    frequency = Counter(numbers)
    max_frequency = max(frequency.values())
    modes = [num for num, freq in frequency.items() if freq == max_frequency]
    average_mode = sum(modes) / len(modes)
    return int(average_mode)