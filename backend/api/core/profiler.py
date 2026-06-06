import threading
import time
import psutil


def measure(fn, *args, **kwargs) -> tuple:
    """
    Run fn(*args, **kwargs) in the current thread while a background thread
    samples CPU and RAM every 0.5s.

    Returns (result, stats) where stats is a dict with:
        duration_s    – wall-clock seconds
        ram_before_mb – RSS before the call
        ram_peak_mb   – peak RSS during the call
        ram_delta_mb  – peak - before
        cpu_mean_pct  – average CPU% across all samples (system-wide)
        cpu_peak_pct  – highest CPU% sample
    """
    process = psutil.Process()

    samples_cpu: list[float] = []
    samples_ram: list[float] = []
    stop_event = threading.Event()

    def _sample():
        while not stop_event.is_set():
            samples_cpu.append(psutil.cpu_percent(interval=None))
            samples_ram.append(process.memory_info().rss / 1024 / 1024)
            time.sleep(0.5)

    ram_before = process.memory_info().rss / 1024 / 1024
    psutil.cpu_percent(interval=None)  # discard first dummy reading

    sampler = threading.Thread(target=_sample, daemon=True)
    sampler.start()
    t0 = time.perf_counter()

    try:
        result = fn(*args, **kwargs)
    finally:
        stop_event.set()
        sampler.join()

    duration = time.perf_counter() - t0

    ram_peak = max(samples_ram, default=ram_before)
    stats = {
        "duration_s":    round(duration, 2),
        "ram_before_mb": round(ram_before, 1),
        "ram_peak_mb":   round(ram_peak, 1),
        "ram_delta_mb":  round(ram_peak - ram_before, 1),
        "cpu_mean_pct":  round(sum(samples_cpu) / len(samples_cpu), 1) if samples_cpu else 0.0,
        "cpu_peak_pct":  round(max(samples_cpu, default=0.0), 1),
    }
    return result, stats
