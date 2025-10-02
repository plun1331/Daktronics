# Daktronics

A Python library for reading data from Daktronics consoles.

## Installation

You can install the library using pip:

```bash
pip install daktronics
```

## Usage

Connect to the RTD port of your Daktronics Omnisport 2000 console.

```python
from daktronics.console import Omnisport2000
from daktronics.processors import WaterPoloProcessor

console = Omnisport2000("COM5")  # Replace "COM5" with your port

console.connect()
processor = WaterPoloProcessor()
console.read(processor)
```

## Supported Consoles

| Console        | Sports     | Notes |
|----------------|------------|-------|
| Omnisport 2000 | Water Polo |       |