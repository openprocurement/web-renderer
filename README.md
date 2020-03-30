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

- ##### `{{ iso_str_date | format_date}}`  
   The function for formating an ISO date to the string one. 
    - **input:** date (ISO): 2019-08-22T13:35:00+03:00 
    - **output:** date (str): "22" серпня 2019 року 
- ##### `{{ str_float_number | to_float}}`
    The function for formatting comma float string to float. 
    - **input:** "12\xa0588\xa0575.00" 
    - **output:** 12588575.0 
- ##### `{{ str_float_number | convert_amount_to_words}}`
    The function for formatting an amount of money to the word string.
    - **input:** "12\xa0588\xa0575.00" 
    - **output:** "триста двадцять двi тисячi шiстсот шiстдесят дев'ять гривень 00 копійок"
