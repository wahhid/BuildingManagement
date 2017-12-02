from openerp.osv import fields, osv
import logging

_logger = logging.getLogger(__name__)


AVAILABLE_STATES = [    
    ('open','Open'),
    ('done','Closed'),
]

class bm_agreement(osv.osv):
    _name = "bm.agreement"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Building Management Agreement"
    _columns = {
        'trans_no': fields.char('No #', size=10, required=True),
        'partner_id': fields.many2one('res.partner','Tenant', required=True),
        'name': fields.char('Description', size=200, required=True),
        'agreement_date_signed': fields.date('Date Signed'),
        'agreement_remark': fields.text("Remark"),
        'state': fields.selection(AVAILABLE_STATES, 'Status', required=True, readonly=True),         
    }
    _defaults = {
        'state': lambda *a: 'open', 
    }
        
bm_agreement()