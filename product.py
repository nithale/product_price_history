# -*- encoding: utf-8 -*-
from osv import fields, osv


class product_product(osv.osv):
    _inherit = 'product.product'

    def _get_max_actual_cost(self, cr, uid, ids, field_name, arg,
                             context=None):
        res = {}
        dolar_rate = self.pool.get('res.company').browse(
            cr, uid, self.pool.get('res.users').browse(cr, uid, uid).
            company_id.id).\
            currency_id.company_dolar_rate
        for c in self.browse(cr, uid, ids, context=context):
            a = [a.actual_cost
                 * dolar_rate
                 / a.actual_dolar_price
                 for a in c.product_history]
            max_actual_cost = max(a or {0})
            res[c.id] = max_actual_cost
        return res

    def _get_avg_actual_cost(self, cr, uid, ids, field_name, arg,
                             context=None):
        res = {}
        dolar_rate = self.pool.get('res.company').\
            browse(cr, uid, self.pool.get('res.users').
                   browse(cr, uid, uid).company_id.id).\
            currency_id.company_dolar_rate

        def f(x): return x != 0
        for c in self.browse(cr, uid, ids, context=context):
            a = [a.actual_cost
                 * dolar_rate
                 / (a.actual_dolar_price or 1.0)
                 for a in c.product_history]
            a = filter(f, a)
            sum_actual_cost = sum(a)
            avg_actual_cost = sum_actual_cost / (len(a) or 1.0)
            res[c.id] = avg_actual_cost
        return res

    _columns = {
        'product_history':
        fields.one2many('product.price.history',
                        'product_id', 'Cost History'),
        'max_actual_cost':
        fields.function(_get_max_actual_cost,
                        type='float', method=True, store=False,
                        string='Max Actual Cost'),
        'avg_actual_cost':
        fields.function(_get_avg_actual_cost,
                        type='float', method=True, store=False,
                        string='Average Actual Price')
            }


"""
    def write(self, cr, uid, ids, values, context=None):
        Add old Sale Price or Sale Cost to historial
        for id in ids:
            prod_product = self.browse(cr, uid, id)

            history_values = {}
            if 'list_price' in values or 'standard_price' in values:
                history_values['list_price'] = prod_product.list_price
                history_values['standard_price'] = prod_product.standard_price
                history_values['product_id'] =  prod_product.id
                history_values['date_to'] =  time.strftime('%Y-%m-%d %H:%M:%S')

                self.pool.get('product.price.history').\
                    create(cr, uid, history_values)

        return super(product_product, self).\
            write(cr, uid, ids, values, context=context)
"""
product_product()
