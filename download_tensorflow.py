import time

from rich.progress import Progress

progress = Progress()
progress.start()
try:
    task1 = progress.add_task("[red]Downloading Tensorflow...", total=1000)
    task2 = progress.add_task("[green]Processing Tensorflow...", total=1000)

    while not progress.finished:
        progress.update(task1, advance=0.5)
        progress.update(task2, advance=0.3)
        time.sleep(0.5)
finally:
    progress.stop()
