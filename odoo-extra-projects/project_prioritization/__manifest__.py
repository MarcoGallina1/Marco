# -*- coding: utf-8 -*-
###################################################################################
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
###################################################################################
{
    'name': "Project Prioritization Matrix",

    'summary': """Prioritize automatically your tasks on each stage, 
        rating effort, value and urgency quickly in kanban or form view. 
        After rating them, they are sorted in every view by the computed 
        priority based on this rating.""",
    'author': 'Juan Albarracin Prados <juan.albarracin@prokom.es>',
    'company': 'PROKOM',
    'website': "https://prokom.es",
    'category': 'Project',
    'version': '13.0.1.0.1',
    'depends': ['project'],
    'data': ['views/view.xml'],
    'license': 'AGPL-3',
    'images': ['static/description/teaser.png'],
    'installable': True,
    'application': True,
}