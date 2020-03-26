# web-renderer

Requests:

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