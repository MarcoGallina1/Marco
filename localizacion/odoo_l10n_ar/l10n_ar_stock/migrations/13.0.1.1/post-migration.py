#!/usr/bin/env python
# coding: utf-8

from odoo import api, SUPERUSER_ID


def migrate(cr, installed_version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    for picking in env['stock.picking'].search([('cai', '!=', False)]):
        picking.update_move_names()
