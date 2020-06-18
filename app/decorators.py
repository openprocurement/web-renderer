
# Form data decorator


def form_data(cls):

    class FormData(cls):
        # form fields
        TEMPLATE = 'template'
        JSON_DATA = 'json_data'
        INCLUDE_ATTACHMENTS = 'include_attachments'
        HIDE_EMPTY_FIELDS = 'hide_empty_fields'
        DOCUMENT_NAMES = 'document_names'
        CONTRACT_TEMPLATE = 'contractTemplate'
        CONTRACT_DATA = 'contractData'
        CONTRACT_PROFORMA = 'contractProforma'

        def __init__(self, *args, **kargs):
            super(FormData, self).__init__(*args, **kargs)

    return FormData
