FROM fedora:31

RUN dnf update -y
RUN dnf install python3-pip libreoffice-core libreoffice-pdfimport libreoffice-opensymbol-fonts.noarch libreoffice-filters libreoffice-pyuno libreoffice-writer libreoffice-calc  -y
RUN dnf clean all

WORKDIR /app

COPY ./ /app

RUN pip install -r /app/requirements.txt

EXPOSE 8080

CMD [ "/usr/bin/python3", "runserver.py" ]