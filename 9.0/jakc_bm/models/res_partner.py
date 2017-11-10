from datetime import datetime, timedelta
from openerp import SUPERUSER_ID
from openerp import api, fields, models, _, exceptions

import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class ResPartner(modelds.Model):
    _inherit = 'res.partner'

    trade_name = fields.Char('Trade Name ', size=100, required=True),
    customer_code = fields.Char('Tenant Code', size=10, required=True),
    join_date = fields.Date('Join Date', required=True),
    tenant_category_id = fields.Many2one('res.partner.category', 'Category'),
    lease_transaction_ids = fields.One2many('bm.lease.transaction', 'res_partner_id', 'Lease Transaction'),


class ResPartnerCategory(osv.osv):
    _name = "res.partner.category"

    name = fields.Char("Name", size=50, required=True)
