from unstructured.partition.pdf import partition_pdf

elements = partition_pdf("/Users/santhosh/Desktop/Intern/pdf_parser_accelerator/pdf_parser_project/shared/input_pdfs/images+text.pdf")
for el in elements:
    print(el.metadata.page_number, el.text)
