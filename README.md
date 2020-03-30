# web-renderer

### Requests:

```
paths:
    /:
    post:
        summary: Render a document.
        requestBody:
            json_data:
                description: json data of the Tender
                content: application/json:
            template:
                description: template .docx file
                content: file
        responses:
        '200':
            file: Generated file
```

### Jinja template functions:

- `{{ iso_str_date | format_date}}`  </br>
   The function for formating an ISO date to the string one. </br>
    - **input:** date (ISO): 2019-08-22T13:35:00+03:00 </br>
    - **output:** date (str): "22" серпня 2019 року </br>
- `{{ str_float_number | to_float}}`</br>
    The function for formatting comma float string to float. </br>
    - **input:** "12\xa0588\xa0575.00" </br>
    - **output:** 12588575.0 </br>
- `{{ str_float_number | convert_amount_to_words}}`</br>
    The function for formatting an amount of money to the word string.
    - **input:** "12\xa0588\xa0575.00" </br>
    - **output:** "триста двадцять двi тисячi шiстсот шiстдесят дев'ять гривень 00 копійок"</br>
