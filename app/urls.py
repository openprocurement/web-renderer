
from app import app
from app.views import(
    RenderView,
    GetJSONSchemaView,
    GetTagSchemaView,
    DisplayFormView,
)


app.add_url_rule('/', view_func=RenderView.as_view('base'))
app.add_url_rule('/get_template_json_schema',
                 view_func=GetJSONSchemaView.as_view('get_template_json_schema'))
app.add_url_rule('/get_template_tag_schema',
                 view_func=GetTagSchemaView.as_view('get_template_tag_schema'))
app.add_url_rule('/display_template_form',
                 view_func=DisplayFormView.as_view('display_template_form'))