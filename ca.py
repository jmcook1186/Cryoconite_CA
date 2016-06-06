import argparse
import cellular

parser = argparse.ArgumentParser()
parser.add_argument('--ticks', action='store', default=60)
parser.add_argument('--slope_length', action='store', default=450)
parser.add_argument('--ticks_per_delivery', action='store', default=30)
parser.add_argument('--delivery_zone', action='store', default=10)
parser.add_argument('--coverage', action='store', default=0.15)
parser.add_argument('--singlelayer_speed', action='store', default=0.3)
parser.add_argument('--multilayer_speed', action='store', default=0.7)
parser.add_argument('--flat_speed', action='store', default=0.2)
parser.add_argument('--drop_zone', action='store', default=6)
parser.add_argument('--gridx', action='store', default=640)
parser.add_argument('--gridy', action='store', default=480)
args = parser.parse_args()

grid = cellular.init_grid(args.gridx, args.gridy, coverage=args.coverage)
cellular.run(grid,
    ticks=args.ticks,
    slope_length=args.slope_length,
    ticks_per_delivery=args.ticks_per_delivery,
    delivery_zone=args.delivery_zone,
    coverage=args.coverage,
    singlelayer_speed=args.singlelayer_speed,
    multilayer_speed=args.multilayer_speed,
    flat_speed=args.flat_speed,
    drop_zone=args.drop_zone
    )
