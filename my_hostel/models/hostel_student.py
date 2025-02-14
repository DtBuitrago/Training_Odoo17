
from datetime import datetime, timedelta
from odoo import fields, models, api
from odoo.tests.common import Form

class HostelStudent(models.Model):
    _name = "hostel.student"
    _description = "Hostel Student Information"

    #partner_id = fields.Many2one('res.partner', ondelete='cascade', delegate=True)

    @api.depends("admission_date", "discharge_date")
    def _compute_check_duration(self):
        """Method to check duration"""
        for rec in self:
            if rec.discharge_date and rec.admission_date:
                rec.duration = (rec.discharge_date - rec.admission_date).days

    def _inverse_duration(self):
        for stu in self:
            if stu.discharge_date and stu.admission_date:
                duration = (stu.discharge_date - stu.admission_date).days
                if duration != stu.duration:
                    stu.discharge_date = (stu.admission_date + timedelta(days=stu.duration)).strftime('%Y-%m-%d')

    name = fields.Char("Student Name")
    gender = fields.Selection([("male", "Male"),
        ("female", "Female"), ("other", "Other")],
        string="Gender", help="Student gender")
    active = fields.Boolean("Active", default=True,
        help="Activate/Deactivate hostel record")
    room_id = fields.Many2one("hostel.room", "Room",
        help="Select hostel room")
    hostel_id = fields.Many2one("hostel.hostel", related='room_id.hostel_id')
    #hostel_name = fields.Char("Nombre Hotel", compute='_get_name_hostel')
    status = fields.Selection([("draft", "Draft"),
        ("reservation", "Reservation"), ("pending", "Pending"),
        ("paid", "Done"),("discharge", "Discharge"), ("cancel", "Cancel")],
        string="Status", copy=False, default="draft",
        help="State of the student hostel")
    admission_date = fields.Date("Admission Date",
        help="Date of admission in hostel",
        default=fields.Datetime.today)
    discharge_date = fields.Date("Discharge Date",
        help="Date on which student discharge")
    duration = fields.Integer("Duration", compute="_compute_check_duration", inverse="_inverse_duration",
                               help="Enter duration of living")
    duration_months = fields.Integer("Duration on Months",help="Enter duration of living")
    
    def action_assign_room(self):
        self.ensure_one()
        room_as_superuser = self.env['hostel.room'].sudo()
        domain = [
            ('name', 'ilike', 'Hotel Cochabamba')
        ]
        hostel_id = self.env['hostel.hostel'].search(domain)
        room_rec = room_as_superuser.create({
            "name": "Room A-103",
            "room_no": "A-104",
            "floor_no": 1,
            "hostel_id": hostel_id.id,
            "student_per_room": 3,
        })
        if room_rec:
            self.sudo().room_id = room_rec.id
        
    def action_remove_room(self):
        if self.env.context.get("is_hostel_room"):
            self.room_id = False
        else:
            print("Context is not set")

    @api.onchange('admission_date', 'discharge_date')
    def onchange_duration(self):
        if self.discharge_date and self.admission_date:
            self.duration_months = (self.discharge_date.year - \
                            self.admission_date.year) * 12 + \
                            (self.discharge_date.month - \
                            self.admission_date.month)
            
    def return_room(self):
        self.ensure_one()
        wizard = self.env['assign.room.student.wizard']
        with Form(wizard) as return_form:
            return_form.room_id = self.env.ref('my_hostel.101_room')
            record = return_form.save()
            record.with_context(active_id=self.id).add_room_in_student()
