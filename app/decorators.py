
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
        DOC_TYPE = 'doc_type'

        def __init__(self, *args, **kargs):
            super(FormData, self).__init__(*args, **kargs)

    return FormData


def ignore(exceptions=(Exception,), default_value=""):
    """Decorator for ignoring exceptions in SOFT mode"""

    def wrap(func):
        def wrapped(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
            except exceptions:
                result = default_value
            return result

        return wrapped
    return wrap
