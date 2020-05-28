import PyPDF2

from app.files import(
    AttachmentFile,
)

class PdfAttacher:
    """
        Class that provides functionality for adding attachments to PDF-A files.
    """
    def __init__(self, pdf_file_name):
        self.pdf_file_name = pdf_file_name
        self.pdf_file = AttachmentFile(self.pdf_file_name, 'rb')
        self.output_file = AttachmentFile('pdfa_'+self.pdf_file_name, 'wb')
        self.create_reader()
        self.create_writer()
        self.transfer_data_to_new_pdf()

    def create_writer(self):
        self.pdf_writer = PyPDF2.PdfFileWriter()

    def create_reader(self):
        self.pdf_reader = PyPDF2.PdfFileReader(self.pdf_file.storage_object)

    def transfer_data_to_new_pdf(self):
        for page in range(self.pdf_reader.numPages):
            page_obj = self.pdf_reader.getPage(page)
            self.pdf_writer.addPage(page_obj)

    def add_attachment(self, file_name):
        attachment_file = AttachmentFile(file_name, 'rb')
        self.pdf_writer.addAttachment(
            attachment_file.name, attachment_file.body)
        attachment_file.storage_object.close()

    def get_attachments(self):
        return [a for a in self.pdf_reader.listAttachments()]

    def save_attachments(self):
        for att in self.attachments:
            with open('attachment_{}'.format(att), 'w') as attachment_file:
                attachment_body = new_reader.getAttachment(att)
                attachment_file.write(attachment_body)

    def write_output(self):
        self.pdf_writer.write(self.output_file.storage_object)
        self.output_file.storage_object.close()