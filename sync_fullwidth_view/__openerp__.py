# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015-Today Synconics Technologies Private Ltd.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.     
#
##############################################################################
{
    "name": "Full Screen View",
    "version": "1.0",
    "author": "Synconics Technologies Pvt. Ltd.",
    "website": "www.synconics.com",
    "version": "1.0",
    "catagory": "Tools",
    "complexity": "easy",
    "summary": "Odoo Fullscreen View Using Sliding Sidebars",
    "description": """
    This module enables the toggle button at the edge of the sidebars horizontally, which provides user to hide in both sides as per its necessity.
    """,
    "depends": ["mail", "im_chat"],
	"data": ["views/fullwidth_view.xml"],
    "qweb": ["static/src/xml/*.xml"],
    "installable": True,
    "auto_install": False
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: