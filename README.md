# aamva-id-faker
Generates AAMVA DRL/IDs to test with scanners. Has various settings. Produces PDF417 barcode. Use at your own risk. Unsupported, but may be useful for research and testing projects.

I needed a script to produce reasonable PDF417 barcodes accurately simulating AAMVA license data using faker-based data generators, and then printed on cards. I use this to test varying private projects including an android app and a web app that uses USB & BlueTooth 2D barcode scanners. I could NOT find anything that would make enough licneses using automated data generators, and would produce something that adhered to AAMVA standards. This... _SHOULD_. However, I do not guarantee that it will. 

If you use this code, and find erorrs, please feel free to contact me. I might not fix things, as I'm not being paid for it anymore. However, I think this (though it is horrible to read... I am NOT a python programmer and created this very quickly) should be useful-ish.

This produces 'licenses' that can be printed on Avery style business cards using a laser printer. You can adjust things in the script to do things. If you need a bunch of cards with PDF417s to test your scanner, this should work.

Basic Check data is printed on the front of the card. You're on your own for printing double-sided cards. I don't need that and my printer only prints one-sided pages. I never did get Open/Libre Office ODF/ODT documents to print. But DOCX and PDF seem to work quite well.

You should also be able to add sections to the licenses to generate state-specific fields. Some random bullshit ones are included because I needed to test having multiple data files in the PDF417 data. If you are NOT testing for having multiple data files & subfiles in your PDF417 data, then you are doing it wrong. 
