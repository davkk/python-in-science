import argparse
import math
import random
from dataclasses import dataclass
from typing import Any, Generator

import tqdm
from PIL import Image, ImageDraw


@dataclass
class Ising:
    size: int
    steps: int
    density: float

    beta: float
    J: float
    B: float

    def __post_init__(self) -> None:
        self.n = self.size * self.size
        self.lattice = [
            random.choices(
                [-1.0, 1.0],
                [1 - self.density, self.density],
            )[0]
            for _ in range(self.n)
        ]
        self.energy = -0.5 * self.J * sum(self.lattice)
        self.magnet = sum(self.lattice)

    def coords(self, idx: int) -> tuple[int, int]:
        assert idx < self.n
        return idx % self.size, idx // self.size

    def sum_neighbors(self, idx: int):
        assert idx < self.n
        i, j = self.coords(idx)
        return (
            self.lattice[(i - 1) % self.size + j * self.size]
            + self.lattice[(i + 1) % self.size + j * self.size]
            + self.lattice[i + (j - 1) % self.size * self.size]
            + self.lattice[i + (j + 1) % self.size * self.size]
        )

    def simulation(self) -> Generator[tuple[int, float, list[float]], Any, None]:
        for step in range(1, self.steps * self.n + 1):
            idx = random.randint(0, self.n - 1)

            spin = self.lattice[idx]

            dE = 2.0 * spin * (self.J * self.sum_neighbors(idx) + self.B)
            dM = 2 * spin

            if dE < 0.0 or random.random() < math.exp(-dE * self.beta):
                self.lattice[idx] *= -1.0
                self.energy += dE
                self.magnet += dM

            if step % self.n == 0:
                yield step, self.magnet / self.n, self.lattice.copy()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="run Ising simulation")
    parser.add_argument(
        "--size",
        type=int,
        required=True,
        help="size of lattice (N x N)",
    )
    parser.add_argument(
        "--beta",
        type=float,
        required=True,
        help="initial beta for simulation",
    )
    parser.add_argument(
        "--steps",
        type=int,
        required=True,
        help="maximum number of steps",
    )
    parser.add_argument(
        "-J",
        type=float,
        default=1,
        help="J constant value",
    )
    parser.add_argument(
        "-B",
        type=float,
        default=0,
        help="magnetic field",
    )
    parser.add_argument(
        "--density",
        type=float,
        default=0.5,
        help="intial +1 spin density",
    )
    parser.add_argument(
        "--output-images",
        type=str,
        help="output image file names prefix",
    )
    parser.add_argument(
        "--output-animation",
        type=str,
        help="output animation file name",
    )
    parser.add_argument(
        "--output-stats",
        type=str,
        help="output stats file name",
    )
    args = parser.parse_args()

    ising = Ising(
        size=args.size,
        steps=args.steps,
        J=args.J,
        beta=args.beta,
        B=args.B,
        density=args.density,
    )

    width = 1024
    height = 1024

    images = [] if args.output_animation else None
    output_stats = open(args.output_stats, "w") if args.output_stats else None

    for step, magnet, spins in tqdm.tqdm(
        ising.simulation(),
        ascii=True,
        total=args.steps,
        unit="step",
        colour="magenta",
    ):
        image = Image.new("RGB", (width, height), (256, 256, 256))
        draw = ImageDraw.Draw(image)

        cell_size = width // args.size
        colors = ["white", "black"]

        for idx in range(ising.n):
            i, j = ising.coords(idx)

            x1 = j * cell_size
            y1 = i * cell_size
            x2 = x1 + cell_size
            y2 = y1 + cell_size

            draw.rectangle(
                [x1, y1, x2, y2],
                fill=colors[int(spins[idx] + 1) // 2],
            )

        if args.output_images:
            image.save(f"{args.output_images}_{step//ising.n:03}.png")

        if args.output_animation and images is not None:
            images.append(image)

        if args.output_stats and output_stats is not None:
            output_stats.write(f"{step//ising.n},{magnet}\n")

    if args.output_animation and images:
        print(f"Saving animation as '{args.output_animation}' ...")
        images[0].save(
            args.output_animation,
            save_all=True,
            append_images=images[1:],
            optimize=False,
            duration=40,
            loop=0,
        )
