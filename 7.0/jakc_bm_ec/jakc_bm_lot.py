from openerp.osv import fields, osv
import logging

_logger = logging.getLogger(__name__)


AVAILABLE_STATES = [    
    ('open','Open'),
    ('active','Active'),    
    ('done','Closed'),
]

class bm_lot(osv.osv):
    _name = "bm.lot"
    _description = "Building Management Lot Number"
    _columns = {        
        'name': fields.char('Lot #', size=10, required=True),        
        'lettable_area': fields.float('Lettable Area (sqm)', required=True),
        'rental_charge': fields.float('Rental (/sqm/month)', required=True),
        'service_charge': fields.float('Service Charge (/sqm/month)', required=True),
        'promotion_levy': fields.float('Promotion Levy (/sqm/month)', required=True),        
        'state': fields.selection(AVAILABLE_STATES, 'Status', required=True, readonly=True),         
    }
    _defaults = {
        'state': lambda *a: 'open', 
    }
        
bm_lot()    