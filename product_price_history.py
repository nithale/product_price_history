# -*- encoding: utf-8 -*-

from osv import fields, osv
# from tools.translate import _

import decimal_precision as dp


class company_dolar_reference(osv.osv):
    """ Referential dolar price used by the company"""
    _inherit = 'res.currency'

    _columns = {
        'company_dolar_rate': fields.float(
            'Company Dolar Rate',
            digits_compute=dp.get_precision('Sale Price'),
            readonly=False),
    }


company_dolar_reference()


class product_price_history(osv.osv):
    _name = 'product.price.history'
    _rec_name = 'product_id'
    _order = 'cost_date'

    def _get_pph_ids_1(self, cr, uid, ids, context=None):
        """Return product_price_history ids to be updated when any changes are
        written to fields in the list ['cost_date', 'cost_currency'] on object
        ‘res.currency.rate’.

    :cr: database cursor
    :uids: current user id
    :ids: id's of changed register on object 'res.currency.rate'
    :context: (dictionary) – context arguments not used
    :returns: list of ids to change in 'product.price.history'

    """
        list_ids = []
        pph_obj = self.pool.get('product.price.history')
        rcr_obj = self.pool.get('res.currency.rate')
        rate_lst = rcr_obj.read(cr, uid, ids, ['name', 'rate'])
        for rate in rate_lst:
            list_ids = pph_obj.search(cr, uid,
                [('cost_date', '=', rate['name'])])
        return list_ids

    def _get_pph_ids(self, cr, uid, ids, context=None):
        """Return product_price_history ids to be updated when any changes are
        written to fields in the list ['company_dolar_rate'] on object
        ‘res.currency’.

    :cr: database cursor
    :uids: current user id
    :ids: id's of changed register on object 'res.currency' not used
    :context: (dictionary) – context arguments not used
    :returns: list of 'ALL' ids to change in 'product.price.history'

    """
        list_ids = []
        pph_obj = self.pool.get('product.price.history')
        list_ids = pph_obj.search(cr, uid, [])
        return list_ids

    def _cost_rate(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for c in self.browse(cr, uid, ids, context=context):
            res[c.id] = 0
            if c.cost_currency.base == True:
                res[c.id] = 1
            else:
                rcr_obj = self.pool.get('res.currency.rate')
                rcr_ids = rcr_obj.\
                    search(cr, uid, [('name', '=', c.cost_date),
                        ('currency_id', '=', c.cost_currency.id)])
                if rcr_ids != []:
                    rate = rcr_obj.\
                        read(cr, uid, rcr_ids, ['name', 'rate'])
                    res[c.id] = rate[0]['rate']
        return res

    def _actual_cost_currency(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for i in ids:
            res[i] = self.pool.get('res.company').\
                browse(cr, uid, self.pool.get('res.users').\
                    browse(cr, uid, uid).company_id.id).\
                currency_id.id
        return res

    def _actual_cost_rate(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for c in self.browse(cr, uid, ids, context=context):
            res[c.id] = c.actual_cost_currency.company_dolar_rate
        return res

    def _rated_cost(self, cr, uid, ids, field_name, arg,
        context=None):
        res = {}
        for c in self.browse(cr, uid, ids, context=context):
            cost_rate = c.cost_rate
            if cost_rate != 0.0:
                res[c.id] = c.cost / cost_rate
            else:
                res[c.id] = 0.0
        return res

    def _estimate_actual_cost(self, cr, uid, ids, field_name, arg,
        context=None):
        res = {}
        for c in self.browse(cr, uid, ids, context=context):
            cost_rate = c.cost_rate
            if cost_rate != 0.0:
                res[c.id] = c.cost * c.actual_cost_rate / cost_rate
            else:
                res[c.id] = 0.0
        return res

    _columns = {
        'supplier_id': fields.many2one('res.partner', 'Supplier',
            required=True,
            domain=[('supplier', '=', True)],
            ondelete='cascade',
            help="Supplier of this product"),
            'purchase_order_line_id':
        fields.many2one('purchase.order.line', 'Order Reference',
            select=True, required=False, ondelete='cascade',
            help='Associated whit the product purchase'),
        'cost_date': fields.date('Date', readonly=False, required=True),
        'cost_currency': fields.many2one(
            'res.currency', 'Cost Currency', required=True,
            help='The currency used for product purchase'),
        'cost_rate': fields.function(
            _cost_rate, type='float', method=True,
            store={
                'res.currency.rate':
                (_get_pph_ids_1,
                 ['name', 'rate'], 10),
                'product.price.history':
                (lambda self, cr, uid, ids, c={}: ids,
                 ['cost_date', 'cost_currency'], 10)},
            string='Cost Currency Rate',
            help=('Price of the cost currency in currency of rate 1'
                  '(USD for example) at the date of the cost')
            ),
        'cost': fields.float(
            'Cost Price',
            digits_compute=dp.get_precision('Sale Price'),
            readonly=False),
        'rated_cost': fields.function(
            _rated_cost,
            type='float', method=True,
            store={
                'product.price.history':
                (lambda self, cr, uid, ids, c={}: ids,
                 ['cost_date', 'cost', 'cost_currency', 'cost_rate'], 11),
                },
            string='Rated Cost',
            help='Cost in currency of rate 1 i.e. USD'
            ),
        'actual_cost_rate': fields.function(
            _actual_cost_rate,
            type='float', method=True,
            store=False,
            string='Actual Rate',
            help=('Official company dolar rate associted with'
                  'the current currency used by the company set it in:'
                  'Accounting->Configuration->Miscellaneous->Currency')),
        'actual_cost_currency': fields.function(
            _actual_cost_currency,
            type='many2one', obj='res.currency', method=True,
            store=False,
            string='Actual Currency',
            help=('Oficial company\'s currency set in'
                  'Configuration->Companies->Company->Currency')
            ),
        'actual_cost': fields.function(
            _estimate_actual_cost,
            type='float', method=True,
            store={
                'product.price.history':
                (lambda self, cr, uid, ids, c={}: ids,
                 ['cost', 'cost_currency', 'cost_rate',
                  'actual_cost_rate', 'actual_cost_currency',
                  ],
                 11),
                'res.currency':
                (_get_pph_ids,
                 ['company_dolar_rate'], 11)
            },
            string='Actual Cost',
            help=('Cost estimated up to date using company\'s oficial rate'
                  'Accounting->Configuration->Miscellaneous->Currency'
                  'Where Currency is the company\'s currency'
                  'Configuration->Companies->Company->Currency'
                  )
            ),
        'product_id':
        fields.many2one('product.product', 'Product',
            ondelete='cascade'),
    }

    _defaults = {
        'cost_currency': lambda self, cr, uid, c:
        self.pool.get('res.company').browse(
            cr, uid,
            self.pool.get('res.users').\
                browse(cr, uid, uid).company_id.id
            ).currency_id.id,
        }


product_price_history()
