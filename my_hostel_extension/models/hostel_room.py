import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)

class HostelRoom(models.Model):
    _inherit = 'hostel.room'

    extended_field = fields.Char(string="Extended Field")

    def make_closed(self):
        _logger.info('Extension of Make Closed executed')
        return super(HostelRoom, self).make_closed()

    def make_available(self):
        _logger.info('Extension of Make Available executed')
        return super(HostelRoom, self).make_available()