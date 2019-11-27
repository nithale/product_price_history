# -*- encoding: utf-8 -*-

from osv import fields, osv
# from tools.translate import _

import decimal_precision as dp


class company_dolar_reference(osv.osv):
    """ Precio referencial del dolar usado por la compañia"""
    _inherit = 'res.currency'

    _columns = {
        'company_dolar_rate': fields.float('Company Dolar Rate',
                                           digits_compute=dp.
                                           get_precision('Sale Price'),
                                           readonly=False),
    }


company_dolar_reference()


class product_price_history(osv.osv):
    _name = 'product.price.history'
    _rec_name = 'product_id'
    _order = 'date'

    def _get_product_price_history_id(self, cr, uid, ids, context=None):
        list_ids = []
        pph_obj = self.pool.get('product.price.history')
        list_ids = pph_obj.search(cr, uid, [])
        return list_ids

    def _cost_dolar_rate(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for c in self.browse(cr, uid, ids, context=context):
            res[c.id] = 0
            res_currency_rate_obj = self.pool.get('res.currency.rate')
            currency_rate_ids = res_currency_rate_obj.\
                search(cr, uid, [('name', '=', c.date),
                                 ('currency_id', '=', c.cost_currency.id)])
            if currency_rate_ids != []:
                rate = res_currency_rate_obj.\
                    read(cr, uid, currency_rate_ids, ['name', 'rate'])
                res[c.id] = rate[0]['rate']
        return res

    def _actual_dolar_rate(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for c in self.browse(cr, uid, ids, context=context):
            res[c.id] = c.actual_cost_currency.company_dolar_rate
        return res

    def _estimate_actual_cost(self, cr, uid, ids, field_name, arg,
                              context=None):
        res = {}
        for c in self.browse(cr, uid, ids, context=context):
            dolar_price = c.dolar_price
            if dolar_price != 0.0:
                res[c.id] = c.cost * c.actual_dolar_price / dolar_price
            else:
                res[c.id] = 0.0
        return res

    _columns = {
        'supplier_id':
        fields.many2one('res.partner', 'Supplier',
                        required=True,
                        domain=[('supplier', '=', True)],
                        ondelete='cascade',
                        help="Supplier of this product"),
        'purchase_order_line_id':
        fields.many2one('purchase.order.line', 'Order Reference',
                        select=True, required=False, ondelete='cascade',
                        help='Associated whit the product purchase'),
        'date': fields.date('Date', readonly=False, required=True),
        'cost_currency':
        fields.many2one('res.currency', 'Cost Currency', required=True,
                        help='The currency used for product purchase'),
        'dolar_price':
        fields.function(_cost_dolar_rate, type='float', method=True,
                        store={'product.price.history':
                               (lambda self, cr, uid, ids, c={}: ids,
                                ['date', 'cost_currency'], 10)},
                        string='Dolar Price',
                        help='Dolar Price associated with the cost date'),
        'cost':
        fields.float('Cost Price',
                     digits_compute=dp.get_precision('Sale Price'),
                     readonly=False),
        'actual_cost_currency':
        fields.many2one('res.currency',
                        'Actual Cost Currency',
                        required=True,
                        help='Can be different from the cost currency'),
        'actual_dolar_price':
        fields.function(_actual_dolar_rate,
                        type='float', method=True,
                        store=False,
                        string='Actual Dolar Price',
                        help='Official company dolar rate associted with \
                        the current currency used by the company'),
        'actual_cost':
        fields.function(_estimate_actual_cost,
                        type='float', method=True,
                        store={'product.price.history':
                               (lambda self, cr, uid, ids, c={}: ids,
                                ['cost', 'cost_currency', 'dolar_price',
                                 'actual_dolar_price', 'actual_cost_currency'],
                                11),
                               'res.currency':
                               (_get_product_price_history_id,
                                ['company_dolar_rate'], 11)
                               },
                        string='Actual Cost',
                        help='Cost estimated up to date using the Actual Dolar\
                        Rate'),
        'product_id':
        fields.many2one('product.product', 'Product',
                        ondelete='cascade'),
    }

    _defaults = {
        'cost_currency': lambda self, cr, uid, c:
        self.pool.get('res.company').browse(
            cr, uid,
            self.pool.get('res.users').browse(cr, uid, uid).company_id.id
        ).currency_id.id,
        'actual_cost_currency': lambda self, cr, uid, c:
        self.pool.get('res.company').browse(
            cr, uid,
            self.pool.get('res.users').browse(cr, uid, uid).company_id.id
        ).currency_id.id,
    }


product_price_history()
