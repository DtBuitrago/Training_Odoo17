from odoo import fields, models, api
from odoo.exceptions import ValidationError


class HostelCategory(models.Model):
    _name = "hostel.category"
    _description = "Hostel Categories"
    _parent_store = True
    _parent_name = "parent_id" # optional if field is 'parent_id'

    name = fields.Char('Category')
    description = fields.Text('Description')
    parent_id = fields.Many2one(
        'hostel.category',
        string='Parent Category',
        ondelete='restrict',
        index=True)
    parent_path = fields.Char(index=True, unaccent=False)
    child_ids = fields.One2many(
        'hostel.category', 'parent_id',
        string='Child Categories')
    amount = fields.Float('Amount', default=100.0)

    @api.constrains('parent_id')
    def _check_hierarchy(self):
        if not self._check_recursion():
            raise models.ValidationError('Error! You cannot create recursive categories.')