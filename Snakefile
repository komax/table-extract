

rule mk_dir:
    input:
        pdf="pdfs/{pdf_file}.pdf"
    output:
        pdf_dir=directory("ocr_output/{pdf_file}")
    shell:
        "scripts/mkdir_for_pdf.sh {output.pdf_dir}"

rule cp_pdf:
    input:
        pdf="pdfs/{pdf_file}.pdf"
    output:
        pdf="ocr_output/{pdf_file}/orig.pdf"
    shell:
        "cp {input.pdf} {output.pdf}"

rule pdf_to_text:
    input:
        pdf="ocr_output/{pdf_file}/orig.pdf"
    output:
        txt="ocr_output/{pdf_file}/pdftotext.txt"
    shell:
        "pdftotext {input.pdf} - -enc UTF-8 > {output.txt}"

rule pages_to_png:
    input:
        pdf="pdfs/{pdf_file}.pdf"
    output:
        png_dir=directory("ocr_output/{pdf_file}/png/page_{page_no}.png")
    wildcard_constraints:
        page_no="\d+"
    run:
        shell("echo {wildcards.page_no}")
        print(input.pdf)
        print(wildcards.page_no)
        print("I am in a rule for page {wildcards.page_no}")

rule pdf_to_png:
    input:
        pdf="pdfs/{pdf_file}.pdf"
#    output:
#        png_dir=directory("ocr_output/{pdf_file}/png")
    output:
        png_dir=directory("ocr_output/{pdf_file}/png/page_{page_no}.png")
    wildcard_constraints:
        page_no="\d+"
    shell:
        "scripts/pdf_to_png.sh {output.png_dir} {input.pdf}"

rule ocr_tesseract:
    script:
        "ocr_script.sh"
        # Employ gnu parallel.

rule table_extract:
    run:
        "table-extract.py"
