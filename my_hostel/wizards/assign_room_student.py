# -*- coding: utf-8 -*-
from odoo import models, fields
from datetime import datetime


class AssignRoomStudentWizard(models.TransientModel):
    _name = 'assign.room.student.wizard'

    room_id = fields.Many2one("hostel.room", "Room", required=True)

    def add_room_in_student(self):
        hostel_room_student = self.env['hostel.student'].browse(
            self.env.context.get('active_id'))
        if hostel_room_student:
            hostel_room_student.update({
                'room_id': self.room_id.id,
                'admission_date': datetime.today(),
            })
        rooms = self.mapped('room_id')
        action = rooms.get_formview_action()
        if len(rooms.ids) > 1:
            action['domain'] = [('id', 'in', tuple(rooms.ids))]
            action['view_mode'] = 'tree,form'
        return action