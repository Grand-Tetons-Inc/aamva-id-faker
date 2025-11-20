#!/usr/bin/env python3
"""
Generate documentation diagrams for AAMVA ID Faker
"""

from PIL import Image, ImageDraw, ImageFont
import os

# Create docs/images directory
os.makedirs('docs/images', exist_ok=True)

def create_architecture_diagram():
    """Create system architecture diagram"""
    width, height = 1200, 1400
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)

    # Try to load a font, fallback to default
    try:
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
        header_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
        text_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
        small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
    except:
        title_font = ImageFont.load_default()
        header_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
        small_font = ImageFont.load_default()

    # Title
    draw.text((width//2, 30), "AAMVA ID Faker - System Architecture",
              fill='black', font=title_font, anchor='mm')

    # Layer 1: CLI Interface
    draw.rectangle([100, 100, 1100, 180], outline='#2E86AB', fill='#E8F4F8', width=2)
    draw.text((600, 140), "CLI Interface (main)", fill='black', font=header_font, anchor='mm')
    draw.text((600, 160), "argparse: -n <num> -s <state> --all-states", fill='#555', font=small_font, anchor='mm')

    # Arrow
    draw.line([600, 180, 600, 220], fill='black', width=2)
    draw.polygon([(600, 220), (595, 210), (605, 210)], fill='black')

    # Layer 2: Data Generation
    draw.rectangle([100, 220, 1100, 400], outline='#A23B72', fill='#F9E8F0', width=2)
    draw.text((600, 250), "Data Generation Layer", fill='black', font=header_font, anchor='mm')

    # Sub-boxes in data generation
    draw.rectangle([120, 280, 360, 380], outline='#A23B72', fill='white', width=1)
    draw.text((240, 300), "generate_license_data()", fill='black', font=text_font, anchor='mm')
    draw.text((240, 320), "• Faker: Names, DOB", fill='#555', font=small_font, anchor='mm')
    draw.text((240, 340), "• Physical attributes", fill='#555', font=small_font, anchor='mm')
    draw.text((240, 360), "• Dates, addresses", fill='#555', font=small_font, anchor='mm')

    draw.rectangle([380, 280, 620, 380], outline='#A23B72', fill='white', width=1)
    draw.text((500, 300), "generate_state_", fill='black', font=text_font, anchor='mm')
    draw.text((500, 320), "license_number()", fill='black', font=text_font, anchor='mm')
    draw.text((500, 350), "30 state formats", fill='#555', font=small_font, anchor='mm')

    draw.rectangle([640, 280, 880, 380], outline='#A23B72', fill='white', width=1)
    draw.text((760, 300), "generate_state_", fill='black', font=text_font, anchor='mm')
    draw.text((760, 320), "subfile()", fill='black', font=text_font, anchor='mm')
    draw.text((760, 350), "State-specific data", fill='#555', font=small_font, anchor='mm')

    # Arrow
    draw.line([600, 400, 600, 440], fill='black', width=2)
    draw.polygon([(600, 440), (595, 430), (605, 430)], fill='black')

    # Layer 3: Barcode Encoding
    draw.rectangle([100, 440, 1100, 620], outline='#F18F01', fill='#FFF4E6', width=2)
    draw.text((600, 470), "Barcode Encoding Layer", fill='black', font=header_font, anchor='mm')

    draw.rectangle([120, 500, 540, 600], outline='#F18F01', fill='white', width=1)
    draw.text((330, 520), "format_barcode_data()", fill='black', font=text_font, anchor='mm')
    draw.text((330, 545), "AAMVA 2020 Format", fill='#555', font=small_font, anchor='mm')
    draw.text((330, 565), "• Header construction", fill='#555', font=small_font, anchor='mm')
    draw.text((330, 585), "• Subfile assembly", fill='#555', font=small_font, anchor='mm')

    draw.rectangle([560, 500, 980, 600], outline='#F18F01', fill='white', width=1)
    draw.text((770, 520), "save_barcode_and_data()", fill='black', font=text_font, anchor='mm')
    draw.text((770, 545), "pdf417.encode()", fill='#555', font=small_font, anchor='mm')
    draw.text((770, 565), "pdf417.render_image()", fill='#555', font=small_font, anchor='mm')
    draw.text((770, 585), "Save BMP + TXT", fill='#555', font=small_font, anchor='mm')

    # Arrow
    draw.line([600, 620, 600, 660], fill='black', width=2)
    draw.polygon([(600, 660), (595, 650), (605, 650)], fill='black')

    # Layer 4: Document Generation
    draw.rectangle([100, 660, 1100, 840], outline='#6A994E', fill='#F1F8E9', width=2)
    draw.text((600, 690), "Document Generation Layer", fill='black', font=header_font, anchor='mm')

    draw.rectangle([120, 720, 390, 820], outline='#6A994E', fill='white', width=1)
    draw.text((255, 740), "create_avery_pdf()", fill='black', font=text_font, anchor='mm')
    draw.text((255, 760), "ReportLab", fill='#555', font=small_font, anchor='mm')
    draw.text((255, 780), "10 cards/page", fill='#555', font=small_font, anchor='mm')
    draw.text((255, 800), "Avery 28371", fill='#555', font=small_font, anchor='mm')

    draw.rectangle([410, 720, 680, 820], outline='#6A994E', fill='white', width=1)
    draw.text((545, 740), "create_docx_card()", fill='black', font=text_font, anchor='mm')
    draw.text((545, 760), "python-docx", fill='#555', font=small_font, anchor='mm')
    draw.text((545, 780), "5×2 table", fill='#555', font=small_font, anchor='mm')
    draw.text((545, 800), "Embed PNG", fill='#555', font=small_font, anchor='mm')

    draw.rectangle([700, 720, 980, 820], outline='#999', fill='#f5f5f5', width=1)
    draw.text((840, 740), "create_odt_card()", fill='#666', font=text_font, anchor='mm')
    draw.text((840, 770), "DISABLED", fill='#999', font=small_font, anchor='mm')

    # Arrow
    draw.line([600, 840, 600, 880], fill='black', width=2)
    draw.polygon([(600, 880), (595, 870), (605, 870)], fill='black')

    # Layer 5: Output
    draw.rectangle([100, 880, 1100, 1020], outline='#333', fill='#f0f0f0', width=2)
    draw.text((600, 910), "File System Output", fill='black', font=header_font, anchor='mm')

    draw.text((300, 945), "output/barcodes/", fill='#555', font=text_font, anchor='mm')
    draw.text((300, 970), "license_N.bmp", fill='#555', font=small_font, anchor='mm')

    draw.text((500, 945), "output/data/", fill='#555', font=text_font, anchor='mm')
    draw.text((500, 970), "license_N.txt", fill='#555', font=small_font, anchor='mm')

    draw.text((700, 945), "output/cards/", fill='#555', font=text_font, anchor='mm')
    draw.text((700, 970), "license_N_card.png", fill='#555', font=small_font, anchor='mm')

    draw.text((400, 1000), "licenses_avery_28371.pdf", fill='#555', font=small_font, anchor='mm')
    draw.text((700, 1000), "cards.docx", fill='#555', font=small_font, anchor='mm')

    # Legend
    draw.text((600, 1060), "Legend:", fill='black', font=header_font, anchor='mm')
    draw.rectangle([200, 1090, 350, 1110], outline='#2E86AB', fill='#E8F4F8', width=1)
    draw.text((360, 1100), "CLI Layer", fill='black', font=small_font, anchor='lm')

    draw.rectangle([500, 1090, 650, 1110], outline='#A23B72', fill='#F9E8F0', width=1)
    draw.text((660, 1100), "Data Generation", fill='black', font=small_font, anchor='lm')

    draw.rectangle([200, 1130, 350, 1150], outline='#F18F01', fill='#FFF4E6', width=1)
    draw.text((360, 1140), "Barcode Encoding", fill='black', font=small_font, anchor='lm')

    draw.rectangle([500, 1130, 650, 1150], outline='#6A994E', fill='#F1F8E9', width=1)
    draw.text((660, 1140), "Document Generation", fill='black', font=small_font, anchor='lm')

    img.save('docs/images/architecture_diagram.png', 'PNG', dpi=(300, 300))
    print("✓ Created architecture_diagram.png")


def create_data_flow_diagram():
    """Create data flow diagram"""
    width, height = 1000, 1200
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)

    try:
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
        header_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
        text_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 13)
        small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
    except:
        title_font = header_font = text_font = small_font = ImageFont.load_default()

    # Title
    draw.text((width//2, 30), "Data Flow - Single License Generation",
              fill='black', font=title_font, anchor='mm')

    y = 80

    # Step 1: User Input
    draw.rectangle([200, y, 800, y+60], outline='#2E86AB', fill='#E8F4F8', width=2)
    draw.text((500, y+20), "User Input", fill='black', font=header_font, anchor='mm')
    draw.text((500, y+40), "State: CA, Number: 1", fill='#555', font=text_font, anchor='mm')
    y += 60

    # Arrow
    draw.line([500, y, 500, y+30], fill='black', width=2)
    draw.polygon([(500, y+30), (495, y+20), (505, y+20)], fill='black')
    y += 30

    # Step 2: Data Generation
    draw.rectangle([150, y, 850, y+150], outline='#A23B72', fill='#F9E8F0', width=2)
    draw.text((500, y+15), "generate_license_data('CA')", fill='black', font=header_font, anchor='mm')

    draw.text((230, y+45), "Name: John Doe", fill='#555', font=text_font, anchor='lm')
    draw.text((230, y+65), "DOB: 1990-05-15", fill='#555', font=text_font, anchor='lm')
    draw.text((230, y+85), "Address: 123 Main St", fill='#555', font=text_font, anchor='lm')
    draw.text((230, y+105), "Physical: 70\", 180lbs", fill='#555', font=text_font, anchor='lm')

    draw.text((550, y+45), "License #: A1234567", fill='#555', font=text_font, anchor='lm')
    draw.text((550, y+65), "Issue: 2025-11-20", fill='#555', font=text_font, anchor='lm')
    draw.text((550, y+85), "Expires: 2032-08-14", fill='#555', font=text_font, anchor='lm')
    draw.text((550, y+105), "Class: D, DHS: F", fill='#555', font=text_font, anchor='lm')

    draw.text((500, y+130), "Returns: [DL_dict, State_dict]", fill='#333', font=small_font, anchor='mm')
    y += 150

    # Arrow
    draw.line([500, y, 500, y+30], fill='black', width=2)
    draw.polygon([(500, y+30), (495, y+20), (505, y+20)], fill='black')
    y += 30

    # Step 3: Barcode Formatting
    draw.rectangle([150, y, 850, y+120], outline='#F18F01', fill='#FFF4E6', width=2)
    draw.text((500, y+15), "format_barcode_data(data)", fill='black', font=header_font, anchor='mm')

    draw.text((230, y+45), "@\\n\\x1E\\rANSI 636014100002", fill='#555', font=text_font, anchor='lm')
    draw.text((230, y+65), "DL00380158ZC01580030", fill='#555', font=text_font, anchor='lm')
    draw.text((230, y+85), "DLDAQA1234567\\nDCSDOE...", fill='#555', font=text_font, anchor='lm')

    draw.text((500, y+105), "Returns: AAMVA string (~400 bytes)", fill='#333', font=small_font, anchor='mm')
    y += 120

    # Arrow
    draw.line([500, y, 500, y+30], fill='black', width=2)
    draw.polygon([(500, y+30), (495, y+20), (505, y+20)], fill='black')
    y += 30

    # Step 4: PDF417 Encoding
    draw.rectangle([150, y, 850, y+100], outline='#F18F01', fill='#FFF4E6', width=2)
    draw.text((500, y+15), "save_barcode_and_data(data, 0)", fill='black', font=header_font, anchor='mm')

    draw.text((230, y+45), "pdf417.encode(13 cols, security=5)", fill='#555', font=text_font, anchor='lm')
    draw.text((230, y+65), "pdf417.render_image() → BMP", fill='#555', font=text_font, anchor='lm')

    draw.text((500, y+85), "Saves: license_0.bmp, license_0.txt", fill='#333', font=small_font, anchor='mm')
    y += 100

    # Arrow
    draw.line([500, y, 500, y+30], fill='black', width=2)
    draw.polygon([(500, y+30), (495, y+20), (505, y+20)], fill='black')
    y += 30

    # Step 5: Document Generation (split)
    draw.rectangle([80, y, 480, y+100], outline='#6A994E', fill='#F1F8E9', width=2)
    draw.text((280, y+15), "create_avery_pdf()", fill='black', font=header_font, anchor='mm')
    draw.text((280, y+45), "Avery 28371 layout", fill='#555', font=text_font, anchor='mm')
    draw.text((280, y+65), "10 cards per page", fill='#555', font=text_font, anchor='mm')
    draw.text((280, y+85), "→ PDF output", fill='#333', font=small_font, anchor='mm')

    draw.rectangle([520, y, 920, y+100], outline='#6A994E', fill='#F1F8E9', width=2)
    draw.text((720, y+15), "create_docx_card()", fill='black', font=header_font, anchor='mm')
    draw.text((720, y+45), "5×2 table layout", fill='#555', font=text_font, anchor='mm')
    draw.text((720, y+65), "Embed card images", fill='#555', font=text_font, anchor='mm')
    draw.text((720, y+85), "→ DOCX output", fill='#333', font=small_font, anchor='mm')
    y += 100

    # Arrows converge
    draw.line([280, y, 280, y+20], fill='black', width=2)
    draw.line([720, y, 720, y+20], fill='black', width=2)
    draw.line([280, y+20, 500, y+40], fill='black', width=2)
    draw.line([720, y+20, 500, y+40], fill='black', width=2)
    draw.polygon([(500, y+40), (495, y+30), (505, y+30)], fill='black')
    y += 40

    # Final output
    draw.rectangle([200, y, 800, y+80], outline='#333', fill='#f0f0f0', width=2)
    draw.text((500, y+20), "Output Files Generated", fill='black', font=header_font, anchor='mm')
    draw.text((500, y+45), "licenses_avery_28371.pdf  |  cards.docx", fill='#555', font=text_font, anchor='mm')
    draw.text((500, y+65), "Barcodes, Data, Card Images", fill='#555', font=small_font, anchor='mm')

    img.save('docs/images/data_flow_diagram.png', 'PNG', dpi=(300, 300))
    print("✓ Created data_flow_diagram.png")


def create_barcode_structure_diagram():
    """Create AAMVA PDF417 barcode structure diagram"""
    width, height = 1100, 1000
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)

    try:
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
        header_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
        text_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 13)
        small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
        mono_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 11)
    except:
        title_font = header_font = text_font = small_font = mono_font = ImageFont.load_default()

    # Title
    draw.text((width//2, 30), "AAMVA PDF417 Barcode Data Structure",
              fill='black', font=title_font, anchor='mm')

    y = 80
    x_left = 50
    box_width = 1000

    # Segment 1: Compliance Markers
    draw.rectangle([x_left, y, x_left+box_width, y+60], outline='#E63946', fill='#FFE5E7', width=2)
    draw.text((x_left+10, y+10), "SEGMENT 1: Compliance Markers", fill='black', font=header_font, anchor='lm')
    draw.text((x_left+10, y+35), "@  \\n  \\x1E  \\r", fill='#333', font=mono_font, anchor='lm')
    draw.text((x_left+200, y+35), "(4 bytes: @ + LF + RS + CR)", fill='#666', font=small_font, anchor='lm')
    y += 70

    # Segment 2: Header
    draw.rectangle([x_left, y, x_left+box_width, y+120], outline='#F77F00', fill='#FFF3E0', width=2)
    draw.text((x_left+10, y+10), "SEGMENT 2: Header", fill='black', font=header_font, anchor='lm')
    draw.text((x_left+10, y+35), "File Type:      \"ANSI \" (5 bytes)", fill='#333', font=mono_font, anchor='lm')
    draw.text((x_left+10, y+55), "IIN:            \"636014\" (6 bytes)", fill='#333', font=mono_font, anchor='lm')
    draw.text((x_left+10, y+75), "Version:        \"10\" (2 bytes)", fill='#333', font=mono_font, anchor='lm')
    draw.text((x_left+10, y+95), "Jurisdiction:   \"00\" (2 bytes)    Num Entries: \"02\" (2 bytes)",
              fill='#333', font=mono_font, anchor='lm')
    y += 130

    # Segment 3: Subfile Designators
    draw.rectangle([x_left, y, x_left+box_width, y+110], outline='#06A77D', fill='#E8F5F1', width=2)
    draw.text((x_left+10, y+10), "SEGMENT 3: Subfile Designators (10 bytes each)",
              fill='black', font=header_font, anchor='lm')
    draw.text((x_left+10, y+40), "DL Subfile:     Type=\"DL\"  Offset=\"0038\"  Length=\"0158\"",
              fill='#333', font=mono_font, anchor='lm')
    draw.text((x_left+10, y+65), "State Subfile:  Type=\"ZC\"  Offset=\"0196\"  Length=\"0047\"",
              fill='#333', font=mono_font, anchor='lm')
    draw.text((x_left+600, y+90), "(Offset: byte position, Length: data size)",
              fill='#666', font=small_font, anchor='lm')
    y += 120

    # Segment 4: DL Subfile Data
    draw.rectangle([x_left, y, x_left+box_width, y+180], outline='#4361EE', fill='#EBF2FF', width=2)
    draw.text((x_left+10, y+10), "SEGMENT 4: DL Subfile Data (~158 bytes)",
              fill='black', font=header_font, anchor='lm')
    draw.text((x_left+10, y+40), "DL                          (subfile marker)", fill='#333', font=mono_font, anchor='lm')
    draw.text((x_left+10, y+60), "DAQA1234567\\n              (license number)", fill='#333', font=mono_font, anchor='lm')
    draw.text((x_left+10, y+80), "DCSDOE\\n                   (last name)", fill='#333', font=mono_font, anchor='lm')
    draw.text((x_left+10, y+100), "DACJOHN\\n                  (first name)", fill='#333', font=mono_font, anchor='lm')
    draw.text((x_left+10, y+120), "DBB05151990\\n              (birth date)", fill='#333', font=mono_font, anchor='lm')
    draw.text((x_left+10, y+140), "... (26 more fields) ...", fill='#666', font=small_font, anchor='lm')
    draw.text((x_left+10, y+160), "\\r                          (terminator CR)", fill='#333', font=mono_font, anchor='lm')
    y += 190

    # Segment 5: State Subfile Data
    draw.rectangle([x_left, y, x_left+box_width, y+120], outline='#7209B7', fill='#F5E8FF', width=2)
    draw.text((x_left+10, y+10), "SEGMENT 5: State Subfile Data (~47 bytes)",
              fill='black', font=header_font, anchor='lm')
    draw.text((x_left+10, y+40), "ZC                          (subfile marker for CA)", fill='#333', font=mono_font, anchor='lm')
    draw.text((x_left+10, y+60), "ZCWORANGE\\n                (county field)", fill='#333', font=mono_font, anchor='lm')
    draw.text((x_left+10, y+80), "ZCTTEST STRING\\n           (test field)", fill='#333', font=mono_font, anchor='lm')
    draw.text((x_left+10, y+100), "\\r                          (terminator CR)", fill='#333', font=mono_font, anchor='lm')
    y += 130

    # Footer note
    draw.text((width//2, y), "Total Size: ~263 bytes (varies by data content)",
              fill='#666', font=text_font, anchor='mm')

    img.save('docs/images/barcode_structure_diagram.png', 'PNG', dpi=(300, 300))
    print("✓ Created barcode_structure_diagram.png")


def create_state_coverage_chart():
    """Create state coverage visualization"""
    width, height = 1000, 700
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)

    try:
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
        header_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
        text_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
    except:
        title_font = header_font = text_font = ImageFont.load_default()

    # Title
    draw.text((width//2, 30), "State License Format Coverage",
              fill='black', font=title_font, anchor='mm')

    # Stats boxes
    y = 80

    # Implemented states box
    draw.rectangle([100, y, 450, y+120], outline='#06A77D', fill='#E8F5F1', width=3)
    draw.text((275, y+30), "30 States", fill='#06A77D', font=title_font, anchor='mm')
    draw.text((275, y+60), "Custom Formats", fill='black', font=header_font, anchor='mm')
    draw.text((275, y+90), "59% Coverage", fill='#06A77D', font=text_font, anchor='mm')

    # Missing states box
    draw.rectangle([550, y, 900, y+120], outline='#F77F00', fill='#FFF3E0', width=3)
    draw.text((725, y+30), "21 States", fill='#F77F00', font=title_font, anchor='mm')
    draw.text((725, y+60), "Default Format", fill='black', font=header_font, anchor='mm')
    draw.text((725, y+90), "41% Remaining", fill='#F77F00', font=text_font, anchor='mm')

    y = 230

    # List of implemented states
    draw.text((100, y), "Implemented States (30):", fill='black', font=header_font, anchor='lm')
    y += 30

    implemented = [
        "AL, AK, AZ, AR, CA, CO, CT, DE, DC, FL",
        "GA, HI, ID, IL, IN, IA, KS, KY, LA, ME",
        "MD, MA, MI, MN, MS, MO, NY, TX, VA, WI, WY"
    ]

    for line in implemented:
        draw.text((120, y), line, fill='#06A77D', font=text_font, anchor='lm')
        y += 25

    y += 20

    # List of missing states
    draw.text((100, y), "Missing States (21):", fill='black', font=header_font, anchor='lm')
    y += 30

    missing = [
        "MT, NE, NV, NH, NJ, NM, NC, ND, OH, OK",
        "OR, PA, RI, SC, SD, TN, UT, VT, WA, WV, WV"
    ]

    for line in missing:
        draw.text((120, y), line, fill='#F77F00', font=text_font, anchor='lm')
        y += 25

    # Progress bar
    y = 600
    bar_width = 800
    bar_height = 40
    bar_x = (width - bar_width) // 2

    # Background
    draw.rectangle([bar_x, y, bar_x+bar_width, y+bar_height],
                   outline='#333', fill='#f0f0f0', width=2)

    # Progress
    progress_width = int(bar_width * 0.59)
    draw.rectangle([bar_x, y, bar_x+progress_width, y+bar_height],
                   fill='#06A77D', outline='#06A77D', width=0)

    # Labels
    draw.text((bar_x + progress_width//2, y + bar_height//2), "59%",
              fill='white', font=header_font, anchor='mm')
    draw.text((bar_x + progress_width + (bar_width-progress_width)//2, y + bar_height//2), "41%",
              fill='#666', font=header_font, anchor='mm')

    img.save('docs/images/state_coverage_chart.png', 'PNG', dpi=(300, 300))
    print("✓ Created state_coverage_chart.png")


def create_component_dependency_graph():
    """Create component dependency graph"""
    width, height = 1200, 900
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)

    try:
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
        header_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
        text_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
        small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 10)
    except:
        title_font = header_font = text_font = small_font = ImageFont.load_default()

    # Title
    draw.text((width//2, 30), "Component Dependency Graph",
              fill='black', font=title_font, anchor='mm')

    # Main function at top
    draw.rectangle([450, 80, 750, 140], outline='#2E86AB', fill='#E8F4F8', width=2)
    draw.text((600, 110), "main()", fill='black', font=header_font, anchor='mm')

    # Level 2 - called by main
    y = 200

    # ensure_dirs
    draw.rectangle([100, y, 280, y+50], outline='#666', fill='#f5f5f5', width=1)
    draw.text((190, y+25), "ensure_dirs()", fill='black', font=text_font, anchor='mm')
    draw.line([600, 140, 190, y], fill='#666', width=1, joint='curve')

    # generate_license_data
    draw.rectangle([320, y, 580, y+50], outline='#A23B72', fill='#F9E8F0', width=2)
    draw.text((450, y+25), "generate_license_data()", fill='black', font=text_font, anchor='mm')
    draw.line([600, 140, 450, y], fill='#A23B72', width=2)

    # save_barcode_and_data
    draw.rectangle([620, y, 880, y+50], outline='#F18F01', fill='#FFF4E6', width=2)
    draw.text((750, y+25), "save_barcode_and_data()", fill='black', font=text_font, anchor='mm')
    draw.line([600, 140, 750, y], fill='#F18F01', width=2)

    # create_*
    draw.rectangle([920, y, 1100, y+50], outline='#6A994E', fill='#F1F8E9', width=2)
    draw.text((1010, y+25), "create_*_pdf/docx()", fill='black', font=text_font, anchor='mm')
    draw.line([600, 140, 1010, y], fill='#6A994E', width=2)

    # Level 3 - dependencies
    y = 320

    # Under generate_license_data
    draw.rectangle([200, y, 380, y+50], outline='#A23B72', fill='white', width=1)
    draw.text((290, y+15), "generate_state_", fill='black', font=small_font, anchor='mm')
    draw.text((290, y+35), "license_number()", fill='black', font=small_font, anchor='mm')
    draw.line([450, 250, 290, y], fill='#A23B72', width=1)

    draw.rectangle([400, y, 580, y+50], outline='#A23B72', fill='white', width=1)
    draw.text((490, y+15), "generate_state_", fill='black', font=small_font, anchor='mm')
    draw.text((490, y+35), "subfile()", fill='black', font=small_font, anchor='mm')
    draw.line([450, 250, 490, y], fill='#A23B72', width=1)

    # Under save_barcode_and_data
    draw.rectangle([620, y, 780, y+50], outline='#F18F01', fill='white', width=1)
    draw.text((700, y+25), "format_barcode_data()", fill='black', font=small_font, anchor='mm')
    draw.line([750, 250, 700, y], fill='#F18F01', width=1)

    # Under create functions
    draw.rectangle([800, y, 1000, y+50], outline='#6A994E', fill='white', width=1)
    draw.text((900, y+15), "generate_individual_", fill='black', font=small_font, anchor='mm')
    draw.text((900, y+35), "card_image()", fill='black', font=small_font, anchor='mm')
    draw.line([1010, 250, 900, y], fill='#6A994E', width=1)

    # Level 4 - sub-dependencies
    y = 450

    # Under format_barcode_data
    draw.rectangle([500, y, 680, y+50], outline='#F18F01', fill='white', width=1)
    draw.text((590, y+25), "get_iin_by_state()", fill='black', font=small_font, anchor='mm')
    draw.line([700, 370, 590, y], fill='#F18F01', width=1)

    draw.rectangle([700, y, 850, y+50], outline='#F18F01', fill='white', width=1)
    draw.text((775, y+25), "format_date()", fill='black', font=small_font, anchor='mm')
    draw.line([700, 370, 775, y], fill='#F18F01', width=1)

    # External dependencies at bottom
    y = 600
    draw.text((600, y), "External Library Dependencies", fill='black', font=header_font, anchor='mm')

    y += 40
    libs = [
        ("faker", "#A23B72", 100, "Data generation"),
        ("pdf417", "#F18F01", 300, "Barcode encoding"),
        ("Pillow", "#6A994E", 500, "Image operations"),
        ("reportlab", "#6A994E", 700, "PDF creation"),
        ("python-docx", "#6A994E", 900, "DOCX creation"),
    ]

    for lib, color, x, desc in libs:
        draw.rectangle([x, y, x+150, y+60], outline=color, fill='white', width=2)
        draw.text((x+75, y+20), lib, fill='black', font=text_font, anchor='mm')
        draw.text((x+75, y+45), desc, fill='#666', font=small_font, anchor='mm')

    # Arrows to external libs
    draw.line([290, 370, 175, y], fill='#A23B72', width=1)  # faker
    draw.line([700, 370, 375, y], fill='#F18F01', width=1)  # pdf417
    draw.line([900, 370, 575, y], fill='#6A994E', width=1)  # Pillow
    draw.line([1010, 250, 775, y], fill='#6A994E', width=1)  # reportlab
    draw.line([1010, 250, 975, y], fill='#6A994E', width=1)  # python-docx

    # Legend
    y = 750
    draw.text((600, y), "Legend:", fill='black', font=header_font, anchor='mm')
    y += 30

    legends = [
        ("Data Generation", "#A23B72"),
        ("Barcode Encoding", "#F18F01"),
        ("Document Generation", "#6A994E"),
        ("Utilities", "#666"),
    ]

    x_start = 250
    for label, color in legends:
        draw.rectangle([x_start, y, x_start+15, y+15], outline=color, fill=color, width=1)
        draw.text((x_start+25, y+7), label, fill='black', font=small_font, anchor='lm')
        x_start += 200

    img.save('docs/images/component_dependency_graph.png', 'PNG', dpi=(300, 300))
    print("✓ Created component_dependency_graph.png")


if __name__ == '__main__':
    print("Creating documentation diagrams...\n")

    create_architecture_diagram()
    create_data_flow_diagram()
    create_barcode_structure_diagram()
    create_state_coverage_chart()
    create_component_dependency_graph()

    print("\n✅ All diagrams created in docs/images/")
    print("\nGenerated files:")
    print("  - architecture_diagram.png")
    print("  - data_flow_diagram.png")
    print("  - barcode_structure_diagram.png")
    print("  - state_coverage_chart.png")
    print("  - component_dependency_graph.png")
