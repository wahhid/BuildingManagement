from openerp.osv import fields, osv
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
import logging
import uuid

_logger = logging.getLogger(__name__)


AVAILABLE_STATES = [    
    ('draft','New'),                
    ('open','Open'),    
    ('done','Closed'),
]

AVAILABLE_MEMBER_STATES = [
    ('draft','New'),
    ('open','Active'),
    ('inactive','In-Active'),
    ('stop','Stop'),
]

STATE = [
    ('none', 'Non Member'),
    ('canceled', 'Cancelled Member'),
    ('old', 'Old Member'),
    ('expired', 'Expired'),
    ('waiting', 'Waiting Member'),
    ('invoiced', 'Invoiced Member'),
    ('free', 'Free Member'),
    ('paid', 'Paid Member'),
]

class res_partner(osv.osv):
    _name = "res.partner"
    _inherit = "res.partner"
    
    def get_trans(self, cr, uid, ids, context=None):
        trans_id = ids[0]
        return self.browse(cr, uid, trans_id, context=context)        
        
    def trans_generate_uuid(self, cr, uid, ids, context=None):
        uuid = uuid.uuid5(uuid.NAMESPACE_DNS, 'jakc-labs.com'),
        values = {}
        values.update({'member_uuid':uuid})
        return super(res_partner, self).write(cr, uid, ids, values, context=context)
        
    _columns = {                
        'trade_name': fields.char('Trade Name ', size=100),           
        'customer_code': fields.char('Tenant Code', size=10),
        'join_date': fields.date('Join Date'),
        'tenant_category_id': fields.many2one('bm.tenant.category', 'Tenant Category'),
        'lease_transaction_ids': fields.one2many('bm.lease.transaction', 'res_partner_id', 'Lease Transaction'),
        'agreement_ids': fields.one2many('bm.agreement', 'partner_id', 'Agreements'),
        'thd_logbook_ids': fields.one2many('bm.thd.logbook','partner_id', 'THD Logbook'),
    }             
    _defaults = {                
        'join_date': fields.date.context_today,            
    }        
        
res_partner()

class bm_tenant_category(osv.osv):
    _name = "bm.tenant.category"
    _description = "Building Management Tenant Category"
    _columns = {
        'name': fields.char("Name", size=50, required=True)
    }

bm_tenant_category()


class bm_tenant_inquiries(osv.osv):
    _name = "bm.tenant.inquiries"
    _description = "Building Management Tenant Inquiries"
    _columns = {
        'trans_no': fields.char('No #', size=10, required=True),
        'trans_date': fields.datetime('Date', required=True),
        'partner_id': fields.many2one('res.partner','Customer', required=True),
        'name': fields.text('Description', required=True),
        'completion_date': fields.datetime('Completion Date'),
        'phone': fields.char('Phone No', required=True),
        'state': fields.selection(AVAILABLE_STATES, 'Status'),
    }

    _defaults = {
        'state': lambda  *a: 'open',
    }

bm_tenant_inquiries()


class bm_thd_logbook(osv.osv):
    _name = "bm.thd.logbook"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Building Management THD Logbook"

    def trans_close(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'done'}, context=context)

    def _get_users(self, cr, uid, context=None):
        users_ids = []
        officer_ids = self.search(cr, uid, 'bpl.officer', [('is_user', '=', True)])
        for record in self.browse(cr, uid, officer_ids, context=context):
            if record.user_id:
                users_ids.append(record.user_id.id)
        return users_ids

    def onchange_partner_id(self, cr, uid, ids, partner_id, context=None):
        res = {}
        bm_lease_transaction_obj = self.pool.get('bm.lease.transaction')
        args = [('partner_id', '=', partner_id),('state','=','open')]
        ids = bm_lease_transaction_obj.search(cr, uid, [('res_partner_id', '=', partner_id)], context=context)
        bm_lease_transaction = bm_lease_transaction_obj.browse(cr, uid, ids[0], context=context)
        lot_ids = []
        for lot_id in bm_lease_transaction.lot_ids:
            lot_ids.append(lot_id.lot_id.id)
        return {'domain': {'lot_id': [('id', 'in', lot_ids)]}}

    _columns = {
        'trans_no': fields.char('No #', size=10, required=True),
        'trans_date': fields.date('Date'),
        'partner_id': fields.many2one('res.partner', 'Tenant', required=True),
        'name': fields.char('Description', size=200, required=True),
        'lot_id': fields.many2one('bm.lot', 'Lot #', required=True),
        'confirm_by': fields.many2one('res.users', 'Confirm By'),
        'state': fields.selection(AVAILABLE_STATES, 'Status', required=True, readonly=True),
    }
    _defaults = {
        'state': lambda *a: 'open',
    }


bm_thd_logbook()