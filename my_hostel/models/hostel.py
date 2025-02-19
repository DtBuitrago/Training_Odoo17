import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)

class Hostel(models.Model):
    _name = 'hostel.hostel'
    _description = "Information about hostel"
    _order = "id desc, name"
    _rec_name = 'hostel_code'

    name = fields.Char(string="hostel Name", required=True)
    hostel_code = fields.Char(string="Code", required=True)
    street = fields.Char('Street')
    street2 = fields.Char('Street2')
    zip = fields.Char('Zip', change_default=True)
    city = fields.Char('City')
    state_id = fields.Many2one("res.country.state", string='State')
    country_id = fields.Many2one('res.country', string='Country')
    phone = fields.Char('Phone',required=True)
    mobile = fields.Char('Mobile',required=True)
    email = fields.Char('Email')
    hostel_floors = fields.Integer(string="Total Floors")
    image = fields.Binary('Hostel Image')
    active = fields.Boolean("Active", default=True,
        help="Activate/Deactivate hostel record")
    type = fields.Selection([("male", "Boys"), ("female", "Girls"),
        ("common", "Common")], "Type", help="Type of Hostel",
        required=True, default="common")
    other_info = fields.Text("Other Information",
        help="Enter more information")
    description = fields.Html('Description')
    hostel_rating = fields.Float('Hostel Average Rating', 
                                # digits=(14, 4) # Method 1: Optional precision (total, decimals),
                                digits='Rating Value' # Method 2
                                )
    category_id = fields.Many2one('hostel.category')
    ref_doc_id = fields.Reference(selection='_referencable_models', string='Reference Document')
    rooms_count = fields.Integer(compute="_compute_rooms_count")

    def _compute_rooms_count(self):
        room_obj = self.env['hostel.room']
        for hostel in self:
            hostel.rooms_count = room_obj.search_count([('hostel_id', '=', hostel.id)])

    @api.model
    def _referencable_models(self):
        models = self.env['ir.model'].search([('field_id.name', '=', 'message_ids')])
        return [(x.model, x.name) for x in models]

    @api.depends('hostel_code')
    def _compute_display_name(self):
        for record in self:
            name = record.name
            if record.hostel_code:
                name = f'{name} ({record.hostel_code})'
            record.display_name = name
    
    def create_categories(self):
        categ1 = {
            'name': 'Child category 1',
            'description': 'Description for child 1'
        }
        categ2 = {
            'name': 'Child category 2',
            'description': 'Description for child 2'
        }
        parent_category_val = {
            'name': 'Parent category',
            'description': 'Description for parent category',
            'child_ids': [
                (0, 0, categ1),
                (0, 0, categ2),
            ]
        }
        # Total 3 records (1 parent and 2 child) will be created in hostel.room.category model
        record = self.env['hostel.category'].create(parent_category_val)
        return True
    
    # Sorting recordset
    def sort_hostel(self):
        all_hostels = self.search([])
        hostels_sorted = self.sort_hostels_by_rating(all_hostels)
        _logger.info('Hostels before sorting: %s', all_hostels)
        _logger.info('Hostels after sorting: %s', hostels_sorted)
    @api.model
    def sort_hostels_by_rating(self, all_hostels):
        return all_hostels.sorted(key='hostel_rating')
    
    def grouped_data(self):
        data = self._get_average_rating()
        _logger.info("Grouped Data %s" % data)

    @api.model
    def _get_average_rating(self):
        grouped_result = self.read_group(
            [('hostel_rating', "!=", False)], # Domain
            ['category_id', 'avg_hostel_rating:avg(hostel_rating)'], # Fields to access
            ['category_id'] # group_by
            )
        return grouped_result
    
    def action_category_with_amount(self):
        self.env.cr.execute("""
            SELECT
                hc.name,
                hc.amount,
                hc.description
            FROM
                hostel_hostel AS hostel
            JOIN
                hostel_category as hc ON hc.id = hostel.category_id
            WHERE hostel.category_id = %(cate_id)s;""", 
            {'cate_id': self.category_id.id})
        result = self.env.cr.fetchall()
        _logger.warning("Hostel With Amount: %s", result)