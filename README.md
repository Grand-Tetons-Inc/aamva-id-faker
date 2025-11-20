# License Generator

This project generates test license data and prints the data along with a PDF417 barcode in the proper AAMVA format on one side of a business card. It is entirely possible that this is broken. I wrote the original to create PDF417 barcodes with enough data for me to verify them visually when scanned using a 2D USB barcode scanner. I wanted a bit of cruft adeded to it, so I had an AI munge some things in, and I haven't tested it very much. Nor do I intend to do so. If you need this sort of thing, then you can look at this, use it as a base and generate test data for your project. If you are using it for soemthing else, well that's fine too, but you'll have to figure it out. Good luck and have a nice day.

## Features
- Generates sample license data for testing purposes.
- Encodes license data into a PDF417 barcode following the AAMVA (American Association of Motor Vehicle Administrators) standard.
- DRL #s are in correct format for each state, as defined by: [US Personal Identifiers: US Driver's License Number](https://docs.umbrella.com/cloudlock-documentation/docs/us-personal-identifiers#us-drivers-license-number)
- Outputs:
  - Text data files for each license
  - PDF files formatted for business card printing
  - Bitmap images of the PDF417 barcodes

## Output Structure
- `output/cards/`: Contains PDF files for each generated license, formatted for business cards.
- `output/barcodes/`: Contains bitmap images of the PDF417 barcodes for each license.
- `output/data/`: Contains text files with the raw license data for each license.

## Usage
1. Run the main script to generate licenses and output files:
   ```powershell
   python generate_licenses.py
   ```
2. Find the generated cards, barcodes, and data in the `output/` directory.

## Requirements
- Python 3.x
- Python venv
```
  sudo apt install python3-venv
  cd <project-directory>
  python -m venv .venv
```

- Required Python packages (see script for details)
```
  cd <project-directory>
  source .venv/bin/activate
  pip install faker pdf417 pillow odfpy reportlab python-docx
```

# MIT License

Copyright (c) 2025 James W Rogers, Jr. / Grand Tetons Inc.  
Written for SMLA Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
