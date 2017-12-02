from openerp.osv import fields, osv
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)


AVAILABLE_STATES = [
    ('draft','New'),
    ('confirm','Confirm'),
    ('waiting', 'Waiting Agreement'),
    ('open','Open'),    
    ('terminated','Terminated'),
    ('notol','Notol'),    
    ('done','Closed'),
]

class bm_lease_transaction(osv.osv):
    _name = "bm.lease.transaction"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Building Management Lease Transaction"
    
    def get_trans(self, cr, uid, ids, context=None):
        trans_id = ids[0]        
        return self.browse(cr, uid, trans_id, context=context)
    
    def trans_open(self, cr, uid, ids, context=None):
        values = {}
        values.update({'state': 'open'})
        return self.write(cr, uid, ids, values, context=context)
    
    def process_open(self, cr, uid, ids, values, context=None):        
        self.message_post(cr, uid, ids[0], body="Transaction status change to <b>Open<b/>", subtype='mt_comment', context=context)     
        return super(bm_lease_transaction,self).write(cr, uid, ids, values, context=context)

    def trans_cancel(self, cr, uid, ids, context=None):
        values = {}
        values.update({'state': 'cancel'})
        return self.write(cr, uid, ids, values, context=context)
    
    def process_cancel(self, cr, uid, ids, values, context=None):
        values.update({'state': 'draft'})        
        self.message_post(cr, uid, ids[0], body="Transaction status change to <b>New</b>", subtype='mt_comment', context=context)     
        return super(bm_lease_transaction,self).write(cr, uid, ids, values, context=context)

    def trans_terminated(self, cr, uid, ids, context=None):
        values = {}
        values.update({'state': 'terminated'})
        return self.write(cr, uid, ids, values, context=context)
    
    def process_terminated(self, cr, uid, ids, values, context=None):        
        self.message_post(cr, uid, ids[0], body="Transaction status change to <b>Terminated</b>", subtype='mt_comment', context=context)     
        return super(bm_lease_transaction,self).write(cr, uid, ids, values, context=context)

    def trans_notol(self, cr, uid, ids, context=None):
        values = {}
        values.update({'state': 'notol'})
        return self.write(cr, uid, ids, values, context=context)
    
    def process_notol(self, cr, uid, ids, values, context=None):        
        self.message_post(cr, uid, ids[0], body="Transaction status change to <b>Notol</b>", subtype='mt_comment', context=context)     
        return super(bm_lease_transaction,self).write(cr, uid, ids, values, context=context)
        
        
    def trans_close(self, cr, uid, ids, context=None):
        values = {}
        values.update({'state': 'done'})
        return self.write(cr, uid, ids, values, context=context)
        
    def process_close(self, cr, uid, ids, values, context=None):
        self.message_post(cr, uid, ids[0], body="Transaction status change to <b>Close</b>", subtype='mt_comment', context=context)     
        return super(bm_lease_transaction,self).write(cr, uid, ids, values, context=context)
    
        
    _columns = {
        'trans_date': fields.date('Date', required=True),
        'trans_code': fields.char('Transaction #', size=10, required=True),
        'res_partner_id': fields.many2one('res.partner', 'Tenant', required=True),        
        'sales_id': fields.many2one('hr.employee','Sales', required=True),
        'term_of_lease': fields.float('Term of Lease', required=True),
        'down_payment': fields.float('Down Payment', required=True),
        'option_period': fields.float('Option Period'),
        'rate_of_commission': fields.float('Rate of Commision'),
        'lease_of_comm': fields.date("Lease of Commencement", required=True),
        'rent_of_comm': fields.date("Rent of Commencement", required=True),
        'lease_expiration': fields.date("Lease Expiration", required=True),        
        'rent_revision': fields.date('Rent Revision'),   
        'dep_rental': fields.float('Deposit Rental'),
        'dep_parking': fields.float('Deposit Parking'),
        'dep_telephone': fields.float('Deposit Telephone'),
        'iface_loi_process': fields.boolean('Loi Process'),
        'loi_trans_number': fields.char('No #', size=10),
        'loi_date_received': fields.date('Received'),
        'loi_date_agreement_sent': fields.date('Agreement Sent'),
        'loi_status_agreement_sent': fields.boolean('Sent Status'),
        'iface_loi_achieved': fields.boolean('Achieved'),
        'loi_remark': fields.text('Remark'),
        'iface_agreement_process': fields.boolean('Loi Process'),
        'agreement_trans_number': fields.char('No #', size=10, required=True),
        'agreement_date_signed': fields.date('Date Signed'),
        'agreement_remark': fields.text("Remark"),
        'iface_agreement_achieved': fields.boolean('Achieved'),
        'lot_ids': fields.one2many('bm.lease.lot','lease_trans_id', "Lots"),
        'rate_ids': fields.one2many('bm.lease.rate','lease_trans_id',"Rates"),
        'state': fields.selection(AVAILABLE_STATES, 'Status', required=True, readonly=True),         
    }
    _defaults = {                    
        'state': lambda *a: 'draft', 
        'trans_date': fields.date.context_today,
        'iface_loi_process': lambda *a: False,
        'iface_loi_achieved': lambda *a: False,
    }    
    _sql_constraints = [('trans_code_unique', 'unique(trans_code)', 'Transaction code name already exists')]    
        
    def write(self, cr, uid, ids, values, context=None):
        trans = self.get_trans(cr, uid, ids, context=context)
                
        if trans.state == 'done':
            raise osv.except_osv(('Warning'), ('Edit not allowed, Transaction already closed!'))
        
        if 'state' in values.keys():
            if values.get('state') == 'open':
                return self.process_open(cr, uid, ids, values, context=context)
            if values.get('state') == 'cancel':
                return self.process_cancel(cr, uid, ids, values, context=context)
            if values.get('state') == 'terminated':
                return self.process_terminated(cr, uid, ids, values, context=context)
            if values.get('state') == 'notol':
                return self.process_notol(cr, uid, ids, values, context=context)
            if values.get('state') == 'done':
                return self.process_close(cr, uid, ids, values, context=context)
                                
        return super(bm_lease_transaction,self).write(cr, uid, ids, values, context=context)
        
bm_lease_transaction() 


class bm_lease_lot(osv.osv):
    _name = "bm.lease.lot"
    _description = "Building Management Lease Lot"
      
    def get_trans(self, cr, uid, ids, context=None):
        trans_id = ids[0]        
        return self.browse(cr, uid, trans_id, context=context)

    def onchange_lot_id(self, cr, uid, ids, lot_id, context=None):
        res = {}
        if lot_id:
            lot = self.pool.get('bm.lot').browse(cr, uid, lot_id)
            res['lettable_area'] = lot.lettable_area 
            res['rental_charge'] = lot.rental_charge
            res['service_charge'] = lot.service_charge 
            res['promotion_levy'] = lot.promotion_levy
        return {'value': res}

    def _get_conversion_rate(self, cr, uid, ids, field_name, field_value, args, context=None):
        _logger.info('Start Get Conversion Rate')
        result={} 
        if not ids:
            return result
                
        trans_id = ids[0]     
        trans = self.get_trans(cr, uid, ids, context)
        if trans:            
            today = datetime.today()
            rate_ids = trans.lease_trans_id.rate_ids                          
            if rate_ids:
                for rate_id in rate_ids:            
                    if datetime.strptime(rate_id.start_date, '%Y-%m-%d') <= today and datetime.strptime(rate_id.end_date, '%Y-%m-%d') >= today:
                        result[trans_id] = rate_id.rate * rate_id.rupiah * trans.rental_charge                                                                
                        break                         
            return result[trans_id]
        else:
            return result
             
    _columns = {
        'lease_trans_id': fields.many2one('bm.lease.transaction', 'Trans ID'),        
        'lot_id': fields.many2one('bm.lot', 'Lot #', required=True),        
        #'rental_conversion': fields.function(_get_conversion_rate, type='float',  digits=(16,2), string="Conversion"),
        'lettable_area': fields.float('Lettable Area (sqm)', required=True),
        'rental_charge': fields.float('Rental (/sqm/month)', required=True),
        'service_charge': fields.float('Service Charge (/sqm/month)', required=True),
        'promotion_levy': fields.float('Promotion Levy (/sqm/month)', required=True),
    }
    
bm_lease_lot()

class bm_lease_rate(osv.osv):
    _name = "bm.lease.rate"
    _description = "Building Management Lease Rate"    
        
    _columns = {
        'lease_trans_id': fields.many2one('bm.lease.transaction', 'Trans ID'),
        'start_date': fields.date('Start Date', required=True),
        'end_date': fields.date('End Date', required=True),
        'rate': fields.float('Rate', required=True), 
        'rupiah': fields.float('Rupiah', required=True),                   
    }
    
    _defaults = {
        'rate': lambda *a: 0.0,
        'rupiah': lambda *a: 0.0,        
    }
    
bm_lease_rate()

AVAILABLE_AGREEMENT_STATES = [
    ('open', 'Open'),
    ('done', 'Closed'),
]
