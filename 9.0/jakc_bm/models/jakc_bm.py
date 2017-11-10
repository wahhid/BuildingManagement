from datetime import datetime, timedelta
from openerp import SUPERUSER_ID
from openerp import api, fields, models, _, exceptions
from

import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


AVAILABLE_STATES = [
    ('open','Open'),
    ('active','Active'),
    ('done','Closed'),
]


AVAILABLE_TRANSACTION_STATES = [
    ('draft', 'New'),
    ('open', 'Open'),
    ('terminated', 'Terminated'),
    ('notol', 'Notol'),
    ('done', 'Closed'),
]

class BmLot(models.Model):
    _name = "bm.lot"

    name = fields.Char('Lot #', size=10, required=True)
    lettable_area = fields.Float('Lettable Area (sqm)', required=True)
    rental_charge = fields.Float('Rental (/sqm/month)', required=True)
    service_charge = fields.Float('Service Charge (/sqm/month)', required=True)
    promotion_levy = fields.Float('Promotion Levy (/sqm/month)', required=True)
    state = fields.selection(AVAILABLE_STATES, 'Status', required=True, readonly=True)

class BmLeaseTransaction(osv.osv):
    _name = "bm.lease.transaction"
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    def get_trans(self, cr, uid, ids, context=None):
        trans_id = ids[0]
        return self.browse(cr, uid, trans_id, context=context)

    @api.one
    def trans_open(self):
        values = {}
        values.update({'state': 'open'})
        res = self.write(values)
        self.message_post(body="Transaction status change to <b>Open<b/>", subtype='mt_comment')
        return res

    def trans_cancel(self, cr, uid, ids, context=None):
        values = {}
        values.update({'state': 'cancel'})
        return self.write(cr, uid, ids, values, context=context)

    def process_cancel(self, cr, uid, ids, values, context=None):
        values.update({'state': 'draft'})
        self.message_post(cr, uid, ids[0], body="Transaction status change to <b>New</b>", subtype='mt_comment',
                          context=context)
        return super(bm_lease_transaction, self).write(cr, uid, ids, values, context=context)

    def trans_terminated(self, cr, uid, ids, context=None):
        values = {}
        values.update({'state': 'terminated'})
        return self.write(cr, uid, ids, values, context=context)

    def process_terminated(self, cr, uid, ids, values, context=None):
        self.message_post(cr, uid, ids[0], body="Transaction status change to <b>Terminated</b>", subtype='mt_comment',
                          context=context)
        return super(bm_lease_transaction, self).write(cr, uid, ids, values, context=context)

    def trans_notol(self, cr, uid, ids, context=None):
        values = {}
        values.update({'state': 'notol'})
        return self.write(cr, uid, ids, values, context=context)

    def process_notol(self, cr, uid, ids, values, context=None):
        self.message_post(cr, uid, ids[0], body="Transaction status change to <b>Notol</b>", subtype='mt_comment',
                          context=context)
        return super(bm_lease_transaction, self).write(cr, uid, ids, values, context=context)

    def trans_close(self, cr, uid, ids, context=None):
        values = {}
        values.update({'state': 'done'})
        return self.write(cr, uid, ids, values, context=context)

    def process_close(self, cr, uid, ids, values, context=None):
        self.message_post(cr, uid, ids[0], body="Transaction status change to <b>Close</b>", subtype='mt_comment',
                          context=context)
        return super(bm_lease_transaction, self).write(cr, uid, ids, values, context=context)

    trans_date = fields.Date('Date', required=True)
    trans_code = fields.Char('Transaction #', size=10, required=True)
    res_partner_id = fields.Many2one('res.partner', 'Tenant', required=True)
    sales_id = fields.Many2one('hr.employee', 'Sales', required=True)
    term_of_lease = fields.Float('Term of Lease', required=True)
    down_payment = fields.Float('Down Payment', required=True)
    option_period = fields.Float('Option Period')
    rate_of_commission = fields.Float('Rate of Commision')
    lease_of_comm = fields.Date("Lease of Commencement", required=True)
    rent_of_comm = fields.Date("Rent of Commencement", required=True)
    lease_expiration = fields.Date("Lease Expiration", required=True)
    rent_revision = fields.Date('Rent Revision')
    dep_rental = fields.Float('Deposit Rental')
    dep_parking = fields.Float('Deposit Parking')
    dep_telephone = fields.Float('Deposit Telephone')
    lot_ids = fields.One2many('bm.lease.lot', 'lease_trans_id', "Lots")
    rate_ids = fields.One2many('bm.lease.rate', 'lease_trans_id', "Rates")
    state = fields.selection(AVAILABLE_TRANSACTION_STATES, 'Status', required=True, readonly=True)

    _sql_constraints = [('trans_code_unique', 'unique(trans_code)', 'Transaction code name already exists')]

class BmLeaseLot(osv.osv):
    _name = "bm.lease.lot"

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
        result = {}
        if not ids:
            return result

        trans_id = ids[0]
        trans = self.get_trans(cr, uid, ids, context)
        if trans:
            today = datetime.today()
            rate_ids = trans.lease_trans_id.rate_ids
            if rate_ids:
                for rate_id in rate_ids:
                    if datetime.strptime(rate_id.start_date, '%Y-%m-%d') <= today and datetime.strptime(
                            rate_id.end_date, '%Y-%m-%d') >= today:
                        result[trans_id] = rate_id.rate * rate_id.rupiah * trans.rental_charge
                        break
            return result[trans_id]
        else:
            return result

        'lease_trans_id': fields.many2one('bm.lease.transaction', 'Trans ID'),
        'lot_id': fields.many2one('bm.lot', 'Lot #', required=True),
        # 'rental_conversion': fields.function(_get_conversion_rate, type='float',  digits=(16,2), string="Conversion"),
        'lettable_area': fields.float('Lettable Area (sqm)', required=True),
        'rental_charge': fields.float('Rental (/sqm/month)', required=True),
        'service_charge': fields.float('Service Charge (/sqm/month)', required=True),
        'promotion_levy': fields.float('Promotion Levy (/sqm/month)', required=True),


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