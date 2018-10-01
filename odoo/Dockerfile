FROM quay.io/akretion/odoo:11.0-full-latest

COPY . /opt/odoo
RUN pip install -r /opt/odoo/requirements.txt
RUN pip install -e /opt/odoo
RUN pip install -e /opt/odoo/src
