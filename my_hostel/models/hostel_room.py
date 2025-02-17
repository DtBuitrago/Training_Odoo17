import logging

from odoo import fields, models, api, _
from odoo.osv import expression
from odoo.exceptions import ValidationError, UserError
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)

class BaseArchive(models.AbstractModel):
	_name = 'base.archive'
	active = fields.Boolean(default=True)
	
	def do_archive(self):
		for record in self:
			record.active = not record.active

class HostelRoom(models.Model):

    _name = "hostel.room"
    _inherit = ['base.archive']
    _description = "Hostel Room Information"
    _rec_name = "room_no"

    @api.depends("student_per_room", "student_ids")
    def _compute_check_availability(self):
        """Method to check room availability"""
        for rec in self:
            rec.availability = rec.student_per_room - len(rec.student_ids.ids)

    name = fields.Char(string="Room Name", required=True)
    room_no = fields.Char("Room No.", required=True)
    floor_no = fields.Integer("Floor No.", default=1, help="Floor Number")
    currency_id = fields.Many2one('res.currency', string='Currency')
    rent_amount = fields.Monetary('Rent Amount', help="Enter rent amount per month") # optional attribute: currency_field='currency_id' incase currency field have another name then 'currency_id'
    hostel_id = fields.Many2one("hostel.hostel", "hostel", help="Name of hostel")
    student_ids = fields.One2many("hostel.student", "room_id",
        string="Students", help="Enter students")
    hostel_amenities_ids = fields.Many2many("hostel.amenities",
        column1="room_id", column2="amenitiy_id",
        string="Amenities", domain="[('active', '=', True)]",
        help="Select hostel room amenities")
    student_per_room = fields.Integer("Student Per Room", required=True,
        help="Students allocated per room")
    availability = fields.Float(compute="_compute_check_availability",
        store=True, string="Availability", help="Room availability in hostel")
    state = fields.Selection([
        ('draft', 'Unavailable'),
        ('available', 'Available'),
        ('closed', 'Closed')],
        'State', default="draft")
    member_ids = fields.Many2many('hostel.room.member', string='Members')
    remarks = fields.Text('Remarks')
    previous_room_id = fields.Many2one('hostel.room', string='Previous Room')
    hostel_room_category_id = fields.Many2one(
        'hostel.room.category',
        string='Parent Category',
        ondelete='restrict',
        index=True
    )

    @api.model
    def is_allowed_transition(self, old_state, new_state):
        allowed = [('draft', 'available'),
                   ('available', 'closed'),
                   ('closed', 'draft')]
        return (old_state, new_state) in allowed
    def change_state(self, new_state):
        for room in self:
            if room.is_allowed_transition(room.state, new_state):
                room.state = new_state
            else:
                message = _('Moving from %s to %s is not allowed') % (room.state, new_state)
                raise UserError(message)
    def make_available(self):
        self.change_state('available')
    def make_closed(self):
        self.change_state('closed')
    def log_all_room_members(self):
        hostel_room_obj = self.env['hostel.room.member']  # This is an empty recordset of model hostel.room.member
        all_members = hostel_room_obj.search([])
        print("ALL MEMBERS:", all_members)
        return True
    def update_room_no(self):
        self.ensure_one()
        self.room_no = "RM002"
    def find_room(self):
        domain = [
            '|',
                '&', ('name', 'ilike', 'Suite1'),
                     ('room_no', '=', 'RM002'),
                '&', ('name', 'ilike', 'Second Room Name'),
                     ('room_no', '=', 'Second Room Name')
        ]
        Rooms = self.search(domain)
        _logger.info('Room found: %s', Rooms)
        return True
    #Filter Rooms with members
    def filter_members(self):
        all_rooms = self.search([])
        filtered_rooms = self.rooms_with_multiple_members(all_rooms)
        _logger.info('Filtered Rooms: %s', filtered_rooms)
    @api.model
    def rooms_with_multiple_members(self, all_rooms):
        return all_rooms.filtered(lambda b: len(b.member_ids) > 1)
     # Traversing recordset
    def mapped_rooms_members(self):
        all_rooms = self.search([])
        room_authors = self.get_member_names(all_rooms)
        _logger.info('Room Members: %s', room_authors)
    @api.model
    def get_member_names(self, all_rooms):
        return all_rooms.mapped('member_ids.name')


    _sql_constraints = [
       ("room_no_unique", "unique(room_no)", "Room number must be unique!")]
    
    @api.constrains("rent_amount")
    def _check_rent_amount(self):
        """Constraint on negative rent amount"""
        if self.rent_amount < 0:
            raise ValidationError(_("Rent Amount Per Month should not be a negative value!"))
    
    @api.model
    def create(self, values):
        if not self.user_has_groups('my_hostel.group_hostel_manager'):
            values.get('remarks')
            if values.get('remarks'):
                raise UserError(
                    'You are not allowed to modify '
                    'remarks'
                )
        return super(HostelRoom, self).create(values)

    def write(self, values):
        if not self.user_has_groups('my_hostel.group_hostel_manager'):
            if values.get('remarks'):
                raise UserError(
                    'You are not allowed to modify '
                    'remarks'
                )
        return super(HostelRoom, self).write(values)
    
    def name_get(self):
        result = []
        for room in self:
            members = room.member_ids.mapped('name')
            name = '%s (%s)' % (room.name, ', '.join(members))
            result.append((room.id, name))
        return result
    
    @api.model
    def _name_search(self, name='', domain=None, operator='ilike', limit=100, order=None):
        domain = [] if domain is None else domain.copy()
        if not(name == '' and operator == 'ilike'):
            domain += ['|', '|', '|',
                ('name', operator, name),
                ('room_no', operator, name),
                ('member_ids.name', operator, name)
            ]
        return super(HostelRoom, self)._name_search(name=name, domain=domain, operator=operator, limit=limit, order=order)
    
    def action_remove_room_members(self):
        for student in self.student_ids:
            student.with_context(is_hostel_room=True).action_remove_room()