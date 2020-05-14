FROM fedora:31

RUN dnf update -y
RUN dnf install python3-pip libreoffice-core libreoffice-pdfimport libreoffice-opensymbol-fonts.noarch libreoffice-filters libreoffice-pyuno libreoffice-writer libreoffice-calc  -y
RUN dnf clean all

WORKDIR /app

COPY ./ /app

RUN pip install -r /app/requirements.txt

COPY libreoffice_config.txt ~/libreoffice_config.txt
RUN libreoffice --headless --terminate_after_init
RUN sed -i -e '/<\/oor:items>/{r ~/libreoffice_config.txt' -e 'd}' /root/.config/libreoffice/4/user/registrymodifications.xcu

EXPOSE 8080

CMD [ "/usr/bin/python3", "runserver.py" ]