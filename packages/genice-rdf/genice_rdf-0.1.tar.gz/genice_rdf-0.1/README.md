# genice-rdf

A [GenIce](https://github.com/vitroid/GenIce) plugin to calculate the radial distribution functions.

## Requirements

* [GenIce](https://github.com/vitroid/GenIce) >=0.16 must be installed.

## Installation

### System-wide installation

    % make install

### Private installation

Copy the files in formats/ into your local formats folder of GenIce.

## Usage

	% genice 1c -r 3 3 3 -f _RDF > 1c.rdf

## Test in place

    % make test
