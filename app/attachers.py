import PyPDF2

from app.files import(
    PdfFile,
)
from app.constants import(
    GeneralConstants,
)

class PdfAttacher:
    """
        Class that provides functionality for adding attachments to PDF-A files.
    """
    def __init__(self, pdf_file):
        # Input pdf file
        self.pdf_file = pdf_file
        self.pdf_file.set_mode('rb')
        # Output pdfa file
        self.pdfa_file = PdfFile.make_copy(pdf_file)
        self.pdfa_file.name = "pdfa_" + self.pdfa_file.name
        self.pdfa_file.set_mode('wb')
        # Create writers and readers
        self.create_reader()
        self.create_writer()
        # Transfer data from pdf to pdfa
        self.transfer_data_to_pdfa()

    def create_writer(self):
        self.pdf_writer = PyPDF2.PdfFileWriter()

    def create_reader(self):
        self.pdf_reader = PyPDF2.PdfFileReader(self.pdf_file.storage_object)

    def transfer_data_to_pdfa(self):
        for page in range(self.pdf_reader.numPages):
            page_obj = self.pdf_reader.getPage(page)
            self.pdf_writer.addPage(page_obj)

    def add_attachment(self, attachment_file):
        attachment_file.set_mode('rb')
        attachment_file.read()
        self.pdf_writer.addAttachment(
            attachment_file.output_full_name, attachment_file.body)
        attachment_file.storage_object.close()

    def get_attachments(self):
        return [a for a in self.pdf_reader.listAttachments()]

    def save_attachments(self):
        for att in self.attachments:
            with open('attachment_{}'.format(att), 'w') as attachment_file:
                attachment_body = new_reader.getAttachment(att)
                attachment_file.write(attachment_body)

    def write_output(self):
        self.pdf_writer.write(self.pdfa_file.storage_object)
        self.pdfa_file.storage_object.close()