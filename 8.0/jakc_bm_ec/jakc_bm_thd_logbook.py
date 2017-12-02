from openerp.osv import fields, osv
import logging

_logger = logging.getLogger(__name__)


AVAILABLE_STATES = [    
    ('open','Open'),
    ('done','Closed'),
]

class bm_thd_logbook(osv.osv):
    _name = "bm.thd_logbook"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Building Management THD Logbook"
    _columns = {
        'trans_no': fields.char('No #', size=10, required=True),
        'trans_date': fields.date('Date'),
        'partner_id': fields.many2one('res.partner','Tenant', required=True),
        'name': fields.char('Description', size=200, required=True),
        'confirm_by': fields.many2one('res.users','Confirm By'),
        'state': fields.selection(AVAILABLE_STATES, 'Status', required=True, readonly=True),         
    }
    _defaults = {
        'state': lambda *a: 'open', 
    }
        
bm_thd_logbook()