import argparse
import math
import random
import time

import numba
import numpy as np
import tqdm
from PIL import Image, ImageDraw


@numba.njit(cache=True)
def ising(*, size, steps, beta, J, B):
    n = size * size
    lattice = np.random.choice(np.array([-1.0, 1.0]), size=n)

    magnets = []
    states = []

    for step in range(1, steps * n + 1):
        idx = np.random.randint(0, n - 1)
        spin = lattice[idx]

        x, y = idx % size, idx // size
        neighbors = (
            lattice[((x - 1) % size) + y * size]
            + lattice[((x + 1) % size) + y * size]
            + lattice[x + ((y - 1) % size) * size]
            + lattice[x + ((y + 1) % size) * size]
        )
        dE = 2.0 * spin * (J * neighbors + B)

        if dE < 0.0 or random.random() < math.exp(-dE * beta):
            lattice[idx] *= -1.0

        if step % n == 0:
            magnets.append(np.sum(lattice) / n)
            states.append(lattice.copy())

    return magnets, states


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ising Simulation")
    parser.add_argument("--size", type=int, required=True)
    parser.add_argument("--beta", type=float, required=True)
    parser.add_argument("--steps", type=int, required=True)
    parser.add_argument("-J", type=float, default=1)
    parser.add_argument("-B", type=float, default=0)
    parser.add_argument("--output-images", type=str)
    parser.add_argument("--output-animation", type=str)
    parser.add_argument("--output-stats", type=str)
    args = parser.parse_args()

    start = time.perf_counter()
    M, states = ising(
        size=args.size,
        steps=args.steps,
        J=args.J,
        beta=args.beta,
        B=args.B,
    )
    end = time.perf_counter()

    print(f"time elapsed: {end - start} [ms]")

    images = []
    cell_size = 1024 // args.size

    if args.output_images or args.output_animation is not None:
        for step, spins in tqdm.tqdm(
            enumerate(states),
            ascii=True,
            total=args.steps,
            unit="step",
            colour="magenta",
        ):
            image = Image.new("RGB", (1024, 1024), (256, 256, 256))
            draw = ImageDraw.Draw(image)

            for idx in range(len(spins)):
                x, y = idx % args.size, idx // args.size
                draw.rectangle(
                    [
                        y * cell_size,
                        x * cell_size,
                        (y + 1) * cell_size,
                        (x + 1) * cell_size,
                    ],
                    fill="white" if spins[idx] > 0 else "black",
                )

            if args.output_images:
                image.save(f"{args.output_images}_{step:03}.png")
            if args.output_animation is not None:
                images.append(image)

        if args.output_animation and images:
            images[0].save(
                args.output_animation,
                save_all=True,
                append_images=images[1:],
                duration=40,
                loop=0,
            )

    if args.output_stats:
        with open(args.output_stats, "w") as f:
            for step, magnet in enumerate(M):
                f.write(f"{step},{magnet}\n")
