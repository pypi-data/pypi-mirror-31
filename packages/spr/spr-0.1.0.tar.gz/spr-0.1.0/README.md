# Spice Raw Parser (spr)

A python package to parse spice raw data files.

## Getting Started

These instructions will get you a copy of the package up and running on your local machine.

### Installation

#### From PyPI
```
pip install spr
```

#### From source code
```
git clone git@github.com:goncalo-godwitlabs/spr.git
cd spr/
make install
```

## Examples

### Inverting amplifier with an opamp LM741

The following circuit is being simulated:

![](examples/amplifier/schematic.png)

To run the simulation (ngspice should be installed!):

```
make run-example-amplifier
```

which will run ngspice generating an output.log and rawspice.raw files and also plot the voltages `vin` and `vout`.

![](examples/amplifier/plot.png)


## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
